import time
import webbrowser
import os
import subprocess
from camel.toolkits.screenshot_toolkit import ScreenshotToolkit

def main():
    print("Initializing project completion sequence...")
    toolkit = ScreenshotToolkit()
    os.makedirs('screenshots', exist_ok=True)
    
    # 1. Take a screenshot of VS Code
    print("1. Taking a screenshot of VS Code...")
    try:
        toolkit.take_screenshot_and_read_image(
            filename="vscode_screenshot.png",
            save_to_file=True,
            read_image=False
        )
    except Exception as e:
        print(f"Error taking VS Code screenshot: {e}")

    # 2. Add screenshots and commit and push to GitHub
    print("2. Pushing project to GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Project completed: Added VS Code screenshot"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "HEAD"], check=True)
        print("Successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Git push failed. Ensure you have the right permissions and there's something to commit: {e}")
    except Exception as e:
        print(f"Error during git operations: {e}")

    # 3. Open the GitHub repository
    print("3. Opening GitHub repository...")
    repo_url = "https://github.com/HarshS99/Project_TITAN"
    webbrowser.open(repo_url)
    
    print("Waiting 5 seconds for the browser and page to load...")
    time.sleep(5)
    
    # 4. Take a screenshot of the GitHub page
    print("4. Taking a screenshot of the GitHub page...")
    try:
        toolkit.take_screenshot_and_read_image(
            filename="github_screenshot.png",
            save_to_file=True,
            read_image=False
        )
    except Exception as e:
        print(f"Error taking GitHub screenshot: {e}")

    # 5. Push the final GitHub screenshot as well
    print("5. Pushing final GitHub screenshot...")
    try:
        subprocess.run(["git", "add", "screenshots/github_screenshot.png"], check=True)
        subprocess.run(["git", "commit", "-m", "Added GitHub repo screenshot"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "HEAD"], check=True)
        print("Successfully pushed final screenshot.")
    except subprocess.CalledProcessError as e:
        print(f"Final Git push failed: {e}")
    except Exception as e:
        print(f"Error during final git push: {e}")

    print("\nProject completion sequence finished!")

if __name__ == "__main__":
    main()
