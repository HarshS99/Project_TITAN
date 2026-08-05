"""
Project TITAN — Completion Automation
Runs after agents finish a project:
  1. Takes a screenshot of VS Code via AppleScript
  2. Pushes code to GitHub
  3. Opens GitHub repo in browser
  4. Takes a screenshot of the GitHub repo page
  5. Posts to LinkedIn with both screenshots
"""

import os
import subprocess
import time
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCREENSHOTS_DIR = Path("screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

VSCODE_SS  = str(SCREENSHOTS_DIR / "vscode_screenshot.png")
GITHUB_SS  = str(SCREENSHOTS_DIR / "github_screenshot.png")
GITHUB_URL = "https://github.com/HarshS99/Project_TITAN"
LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")


# ── 1. Screenshot helper via AppleScript (works from background) ───────────
def take_screenshot_applescript(save_path: str, delay: float = 0.5) -> bool:
    """Capture full screen using screencapture via interactive AppleScript."""
    try:
        time.sleep(delay)
        # screencapture -x suppresses the shutter sound and works in bg processes
        result = subprocess.run(
            ["screencapture", "-x", "-t", "png", save_path],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and Path(save_path).exists():
            print(f"  ✅ Screenshot saved: {save_path}")
            return True
        else:
            print(f"  ⚠️  screencapture failed (rc={result.returncode}): {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  ⚠️  Screenshot error: {e}")
        return False


# ── 2. LinkedIn posting ────────────────────────────────────────────────────
def post_to_linkedin(text: str, image_path: str | None = None) -> tuple[bool, str]:
    """Post text (+ optional image) to LinkedIn using the UGC Posts API."""
    import requests

    if not LINKEDIN_TOKEN or LINKEDIN_TOKEN == "your_linkedin_token_here":
        return False, "LINKEDIN_ACCESS_TOKEN not configured in .env"

    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Get user URN
    try:
        r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=10)
        if r.status_code != 200:
            return False, f"Failed to get profile: {r.status_code} — {r.text}"
        user_id = r.json().get("sub")
        user_urn = f"urn:li:person:{user_id}"
    except Exception as e:
        return False, f"Profile fetch error: {e}"

    asset_urn = None
    # Upload image if provided
    if image_path and Path(image_path).exists():
        try:
            # Register upload
            reg = requests.post(
                "https://api.linkedin.com/v2/assets?action=registerUpload",
                headers=headers,
                json={"registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": user_urn,
                    "serviceRelationships": [{"relationshipType": "OWNER",
                                              "identifier": "urn:li:userGeneratedContent"}]
                }}, timeout=15
            )
            if reg.status_code in (200, 201):
                upload_url = reg.json()["value"]["uploadMechanism"][
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                asset_urn = reg.json()["value"]["asset"]

                # Upload bytes
                with open(image_path, "rb") as f:
                    up = requests.put(
                        upload_url,
                        headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}",
                                 "Content-Type": "application/octet-stream"},
                        data=f.read(), timeout=60
                    )
                if up.status_code not in (200, 201):
                    asset_urn = None  # fall back to text-only
        except Exception as e:
            print(f"  ⚠️  Image upload error: {e}")
            asset_urn = None

    # Build post payload
    if asset_urn:
        media_content = {
            "shareMediaCategory": "IMAGE",
            "media": [{"status": "READY", "media": asset_urn}]
        }
    else:
        media_content = {"shareMediaCategory": "NONE"}

    payload = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                **media_content,
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        r = requests.post("https://api.linkedin.com/v2/ugcPosts",
                          headers=headers, json=payload, timeout=30)
        if r.status_code in (200, 201):
            post_urn = r.json().get("id", "")
            encoded = requests.utils.quote(post_urn, safe="")
            post_url = f"https://www.linkedin.com/feed/update/{encoded}"
            return True, post_url
        return False, f"Post failed: {r.status_code} — {r.text}"
    except Exception as e:
        return False, f"Post request error: {e}"


# ── Main ───────────────────────────────────────────────────────────────────
def run(project_name: str = "Project TITAN", github_url: str = GITHUB_URL):
    """
    Call this after agents finish. Returns dict with screenshot paths + linkedin URL.
    """
    result = {
        "vscode_screenshot": None,
        "github_screenshot": None,
        "linkedin_post_url": None,
        "github_pushed": False,
        "errors": [],
    }

    print("\n🎬 Starting Project TITAN completion sequence...\n")

    # 1. VS Code screenshot
    print("📸 Step 1 — Taking VS Code screenshot...")
    if take_screenshot_applescript(VSCODE_SS, delay=1.0):
        result["vscode_screenshot"] = VSCODE_SS
    else:
        result["errors"].append("VS Code screenshot failed (run from your terminal with display access)")

    # 2. Git commit + push
    print("\n🚀 Step 2 — Pushing to GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m",
                        f"feat: {project_name} — automated by Project TITAN"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "HEAD"], check=True)
        result["github_pushed"] = True
        print("  ✅ Pushed to GitHub")
    except subprocess.CalledProcessError as e:
        msg = f"Git push failed: {e}"
        result["errors"].append(msg)
        print(f"  ⚠️  {msg}")

    # 3. Open GitHub in browser, wait, screenshot
    print(f"\n🌐 Step 3 — Opening GitHub: {github_url}")
    webbrowser.open(github_url)
    print("  ⏳ Waiting 6 seconds for browser to load...")
    time.sleep(6)

    print("📸 Step 4 — Taking GitHub screenshot...")
    if take_screenshot_applescript(GITHUB_SS, delay=1.0):
        result["github_screenshot"] = GITHUB_SS
        # Push screenshot to repo
        try:
            subprocess.run(["git", "add", str(SCREENSHOTS_DIR)], check=True)
            subprocess.run(["git", "commit", "-m", "docs: Add completion screenshots"], check=True)
            subprocess.run(["git", "push", "-u", "origin", "HEAD"], check=True)
            print("  ✅ Screenshots pushed to GitHub")
        except subprocess.CalledProcessError:
            pass  # Non-critical
    else:
        result["errors"].append("GitHub screenshot failed")

    # 5. Post to LinkedIn
    print("\n🔗 Step 5 — Posting to LinkedIn...")
    post_text = (
        f"🚀 Just shipped \"{project_name}\" using Project TITAN — "
        f"an autonomous AI software engineering system!\n\n"
        f"The AI agents planned, coded, tested, and pushed the entire project "
        f"to GitHub automatically — without me touching a single line. 🤖\n\n"
        f"Check it out 👉 {github_url}\n\n"
        f"#AI #Automation #ProjectTITAN #CamelAI #OpenSource #BuildInPublic"
    )
    # Use VS Code screenshot as the LinkedIn post image
    img = result["vscode_screenshot"] if result["vscode_screenshot"] else None
    ok, li_result = post_to_linkedin(post_text, image_path=img)
    if ok:
        result["linkedin_post_url"] = li_result
        print(f"  ✅ LinkedIn post live: {li_result}")
    else:
        result["errors"].append(f"LinkedIn: {li_result}")
        print(f"  ⚠️  LinkedIn: {li_result}")

    print("\n✅ Completion sequence finished!")
    return result


if __name__ == "__main__":
    run()
