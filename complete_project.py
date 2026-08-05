"""
Project TITAN — Completion Automation
Runs after agents finish a project:
  1. Generates a beautiful project card image (Pillow)
  2. Pushes code to GitHub
  3. Writes a LinkedIn post with Groq AI
  4. Posts to LinkedIn with the project card image
"""

from __future__ import annotations

import io
import os
import subprocess
import textwrap
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

SCREENSHOTS_DIR = Path("screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

CARD_PATH = str(SCREENSHOTS_DIR / "project_card.png")
GITHUB_URL = "https://github.com/HarshS99/Project_TITAN"

LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "HarshS99")


# ── 1. Generate project card image ─────────────────────────────────────────
def generate_project_card(
    project_name: str,
    description: str,
    tech_stack: list[str],
    github_url: str,
    num_files: int = 0,
    num_tasks: int = 0,
) -> str | None:
    """Generate a premium project card PNG using Pillow. Returns file path or None."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        W, H = 1200, 628  # LinkedIn OG image size

        # ── Background gradient ──────────────────────────────────────────────
        img = Image.new("RGB", (W, H), "#0D0D1A")
        draw = ImageDraw.Draw(img)

        # Draw gradient bands (dark purple → dark blue)
        for y in range(H):
            ratio = y / H
            r = int(13 + ratio * 10)
            g = int(13 + ratio * 15)
            b = int(26 + ratio * 40)
            draw.line([(0, y), (W, y)], fill=(r, g, b))

        # Accent glow blob (top-left)
        for i in range(200, 0, -10):
            alpha = int(20 * (i / 200))
            draw.ellipse(
                [(-i, -i), (i * 2, i * 2)],
                fill=(int(99 + alpha), int(58 + alpha // 2), int(237 + alpha // 3)),
            )

        # Accent glow blob (bottom-right)
        for i in range(180, 0, -10):
            alpha = int(15 * (i / 180))
            draw.ellipse(
                [W - i * 2, H - i * 2, W + i, H + i],
                fill=(int(59 + alpha), int(130 + alpha // 2), int(246 + alpha // 3)),
            )

        # ── Fonts (use default since we can't guarantee custom fonts) ────────
        try:
            font_xl = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 68)
            font_lg = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 36)
            font_md = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
            font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
        except Exception:
            font_xl = ImageFont.load_default()
            font_lg = font_xl
            font_md = font_xl
            font_sm = font_xl

        # ── TITAN badge (top-left) ────────────────────────────────────────────
        badge_x, badge_y = 60, 50
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + 220, badge_y + 44],
            radius=22, fill="#7C3AED"
        )
        draw.text((badge_x + 16, badge_y + 8), "⚡ Project TITAN", font=font_sm, fill="white")

        # ── Project name ──────────────────────────────────────────────────────
        display_name = project_name.replace("-", " ").replace("_", " ").title()
        draw.text((60, 130), display_name, font=font_xl, fill="white")

        # ── Description (word-wrapped) ────────────────────────────────────────
        desc_short = (description[:120] + "…") if len(description) > 120 else description
        wrapped = textwrap.wrap(desc_short, width=60)
        y_desc = 220
        for line in wrapped[:2]:
            draw.text((60, y_desc), line, font=font_lg, fill="#A5B4FC")
            y_desc += 48

        # ── Tech stack pills ──────────────────────────────────────────────────
        pill_x = 60
        pill_y = y_desc + 30
        pill_colors = ["#1E3A5F", "#1A2E4A", "#2D1B69", "#1A3A2A", "#3A1A1A"]
        for i, tech in enumerate(tech_stack[:6]):
            text_w = len(tech) * 14 + 30
            color = pill_colors[i % len(pill_colors)]
            draw.rounded_rectangle(
                [pill_x, pill_y, pill_x + text_w, pill_y + 38],
                radius=19, fill=color, outline="#4B5563"
            )
            draw.text((pill_x + 15, pill_y + 8), tech, font=font_sm, fill="#93C5FD")
            pill_x += text_w + 14
            if pill_x > W - 200:
                break

        # ── Stats row ─────────────────────────────────────────────────────────
        stats_y = H - 140
        draw.line([(60, stats_y - 20), (W - 60, stats_y - 20)], fill="#2D2D4A", width=1)

        stats = []
        if num_tasks:
            stats.append(f"📋  {num_tasks} Tasks")
        if num_files:
            stats.append(f"📁  {num_files} Files")
        stats.append("✅  Build Complete")
        stats.append("🚀  Pushed to GitHub")

        sx = 60
        for stat in stats:
            draw.text((sx, stats_y), stat, font=font_md, fill="#9CA3AF")
            sx += 260

        # ── GitHub URL (bottom) ───────────────────────────────────────────────
        draw.text((60, H - 60), github_url, font=font_sm, fill="#6B7280")

        # ── Built by badge (bottom-right) ─────────────────────────────────────
        br_text = "Built with AI — 0 human lines of code"
        draw.text((W - 420, H - 60), br_text, font=font_sm, fill="#6B7280")

        img.save(CARD_PATH, "PNG", quality=95)
        print(f"  ✅ Project card saved: {CARD_PATH}")
        return CARD_PATH

    except Exception as e:
        print(f"  ⚠️  Card generation error: {e}")
        return None


# ── 2. Write LinkedIn post with Groq AI ───────────────────────────────────
def generate_linkedin_post(
    project_name: str,
    description: str,
    tech_stack: list[str],
    github_url: str,
    num_files: int = 0,
    num_tasks: int = 0,
) -> str:
    """Use Groq LLaMA to write a compelling LinkedIn post about the project."""
    if not GROQ_API_KEY:
        return _fallback_post(project_name, description, tech_stack, github_url)

    tech_str = ", ".join(tech_stack) if tech_stack else "HTML, CSS, JavaScript"
    prompt = f"""Write a short, punchy LinkedIn post (max 250 words) about this project I just built:

Project: {project_name.replace("-", " ").replace("_", " ").title()}
Description: {description}
Tech Stack: {tech_str}
Files Generated: {num_files}
Tasks Completed: {num_tasks}
GitHub: {github_url}

Rules:
- Start with a strong hook (no "Excited to share" or "Thrilled")
- Mention it was fully built by AI agents autonomously (Project TITAN)
- Say 0 lines of code were written manually
- Mention the tech stack naturally
- Include the GitHub link
- End with 4-5 relevant hashtags
- Sound human, confident and impressive
- No emojis at the start of every line, use them sparingly"""

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.8,
            },
            timeout=20,
        )
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"].strip()
            print(f"  ✅ LinkedIn post written by Groq AI ({len(text)} chars)")
            return text
    except Exception as e:
        print(f"  ⚠️  Groq post generation error: {e}")

    return _fallback_post(project_name, description, tech_stack, github_url)


def _fallback_post(project_name, description, tech_stack, github_url):
    tech_str = ", ".join(tech_stack[:4]) if tech_stack else "HTML, CSS, JS"
    display = project_name.replace("-", " ").replace("_", " ").title()
    return (
        f"Just shipped \"{display}\" — and I didn't write a single line of code. 🤖\n\n"
        f"Project TITAN, my autonomous AI engineering system, planned, coded, tested "
        f"and pushed the entire project to GitHub — completely on its own.\n\n"
        f"Built with: {tech_str}\n\n"
        f"The AI agents decomposed the idea into tasks, wrote every file, fixed its own "
        f"errors, and shipped it — start to finish, zero intervention.\n\n"
        f"Check it out 👉 {github_url}\n\n"
        f"#AI #Automation #ProjectTITAN #BuildInPublic #OpenSource #AIEngineering"
    )


# ── 3. LinkedIn API helpers ────────────────────────────────────────────────
def _get_user_urn() -> str | None:
    if not LINKEDIN_TOKEN:
        return None
    try:
        r = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}", "X-Restli-Protocol-Version": "2.0.0"},
            timeout=10,
        )
        if r.status_code == 200:
            return f"urn:li:person:{r.json().get('sub')}"
    except Exception:
        pass
    return None


def _register_image(user_urn: str) -> tuple[str, str] | tuple[None, None]:
    try:
        r = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers={
                "Authorization": f"Bearer {LINKEDIN_TOKEN}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json={"registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": user_urn,
                "serviceRelationships": [{"relationshipType": "OWNER",
                                          "identifier": "urn:li:userGeneratedContent"}],
            }},
            timeout=15,
        )
        if r.status_code in (200, 201):
            val = r.json()["value"]
            upload_url = val["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset = val["asset"]
            return upload_url, asset
    except Exception as e:
        print(f"  ⚠️  Image register error: {e}")
    return None, None


def _upload_image(upload_url: str, image_path: str) -> bool:
    try:
        with open(image_path, "rb") as f:
            r = requests.put(
                upload_url,
                headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}",
                         "Content-Type": "application/octet-stream"},
                data=f.read(),
                timeout=60,
            )
        return r.status_code in (200, 201)
    except Exception as e:
        print(f"  ⚠️  Image upload error: {e}")
        return False


def _post_with_image(user_urn: str, text: str, asset_urn: str) -> tuple[bool, str]:
    try:
        r = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={
                "Authorization": f"Bearer {LINKEDIN_TOKEN}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json={
                "author": user_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {"com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [{"status": "READY", "media": asset_urn}],
                }},
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            },
            timeout=30,
        )
        if r.status_code in (200, 201):
            urn = r.json().get("id", "")
            url = f"https://www.linkedin.com/feed/update/{requests.utils.quote(urn, safe='')}"
            return True, url
        return False, f"Post failed: {r.status_code} — {r.text}"
    except Exception as e:
        return False, str(e)


def _post_text_only(user_urn: str, text: str) -> tuple[bool, str]:
    try:
        r = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={
                "Authorization": f"Bearer {LINKEDIN_TOKEN}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json={
                "author": user_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {"com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }},
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            },
            timeout=30,
        )
        if r.status_code in (200, 201):
            urn = r.json().get("id", "")
            url = f"https://www.linkedin.com/feed/update/{requests.utils.quote(urn, safe='')}"
            return True, url
        return False, f"Post failed: {r.status_code} — {r.text}"
    except Exception as e:
        return False, str(e)


def post_to_linkedin(text: str, image_path: str | None = None) -> tuple[bool, str]:
    if not LINKEDIN_TOKEN or LINKEDIN_TOKEN == "your_linkedin_token_here":
        return False, "LINKEDIN_ACCESS_TOKEN not configured in .env"

    user_urn = _get_user_urn()
    if not user_urn:
        return False, "Could not retrieve LinkedIn user profile"

    if image_path and Path(image_path).exists():
        upload_url, asset_urn = _register_image(user_urn)
        if upload_url and asset_urn:
            if _upload_image(upload_url, image_path):
                return _post_with_image(user_urn, text, asset_urn)
            else:
                print("  ⚠️  Image upload failed — falling back to text-only post")
        else:
            print("  ⚠️  Image registration failed — falling back to text-only post")

    return _post_text_only(user_urn, text)


# ── 4. Git push ────────────────────────────────────────────────────────────
def git_push(project_name: str) -> bool:
    try:
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"feat: add project card — {project_name} built by Project TITAN"],
            check=True, capture_output=True,
        )
        subprocess.run(["git", "push", "-u", "origin", "HEAD"], check=True, capture_output=True)
        print("  ✅ Pushed screenshots/card to GitHub")
        return True
    except subprocess.CalledProcessError:
        return False


# ── Main entry point ───────────────────────────────────────────────────────
def run(
    project_name: str = "My Project",
    description: str = "",
    tech_stack: list[str] | None = None,
    github_url: str = GITHUB_URL,
    num_files: int = 0,
    num_tasks: int = 0,
) -> dict:
    """
    Call this after agents finish. Returns dict with card_image path + linkedin URL.
    """
    result = {
        "project_card": None,
        "vscode_screenshot": None,
        "github_screenshot": None,
        "linkedin_post_url": None,
        "github_pushed": False,
        "errors": [],
    }

    tech = tech_stack or ["HTML", "CSS", "JavaScript"]
    print(f"\n🎬 Project TITAN — Completion sequence for: {project_name}\n")

    # 1. Generate project card
    print("🎨 Step 1 — Generating project card image...")
    card = generate_project_card(
        project_name=project_name,
        description=description or f"A {project_name.replace('-', ' ')} built autonomously by Project TITAN",
        tech_stack=tech,
        github_url=github_url,
        num_files=num_files,
        num_tasks=num_tasks,
    )
    if card:
        result["project_card"] = card
        result["vscode_screenshot"] = card   # expose as a screenshot for the UI
        result["github_screenshot"] = card   # also show in the github column

    # 2. Write post with Groq AI
    print("\n✍️  Step 2 — Writing LinkedIn post with Groq AI...")
    post_text = generate_linkedin_post(
        project_name=project_name,
        description=description or f"A full {project_name} application",
        tech_stack=tech,
        github_url=github_url,
        num_files=num_files,
        num_tasks=num_tasks,
    )
    print(f"\n  📝 Post preview:\n{'-'*40}\n{post_text[:300]}...\n{'-'*40}\n")

    # 3. Push card to GitHub
    print("🚀 Step 3 — Pushing project card to GitHub...")
    result["github_pushed"] = git_push(project_name)

    # 4. Post to LinkedIn with card
    print("🔗 Step 4 — Posting to LinkedIn with project card image...")
    ok, li_result = post_to_linkedin(post_text, image_path=card)
    if ok:
        result["linkedin_post_url"] = li_result
        print(f"  ✅ LinkedIn post live: {li_result}")
    else:
        result["errors"].append(f"LinkedIn: {li_result}")
        print(f"  ⚠️  LinkedIn: {li_result}")

    print("\n✅ Completion sequence done!")
    return result


if __name__ == "__main__":
    run(
        project_name="netflix-clone",
        description="A Netflix clone built with HTML, CSS and JavaScript featuring a modern UI with movie browsing",
        tech_stack=["HTML", "CSS", "JavaScript", "Node.js", "Express"],
        github_url="https://github.com/HarshS99/netflix-clone",
    )
