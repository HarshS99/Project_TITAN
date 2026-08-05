import time
import webbrowser
import os
from camel.toolkits.screenshot_toolkit import ScreenshotToolkit

def main():
    print("Initializing ScreenshotToolkit...")
    toolkit = ScreenshotToolkit()
    
    # Ensure screenshots directory exists (if the toolkit doesn't create it automatically)
    os.makedirs('screenshots', exist_ok=True)
    
    print("Taking a screenshot of the current screen (VS Code)...")
    # Take screenshot of VS Code (currently active)
    # Set read_image=False to avoid requiring an OpenAI API key just to capture the image.
    try:
        res1 = toolkit.take_screenshot_and_read_image(
            filename="vscode_screenshot.png",
            save_to_file=True,
            read_image=False
        )
        print("Result:", res1)
    except Exception as e:
        print(f"Error taking VS Code screenshot: {e}")

    print("\nOpening GitHub...")
    # Open the user's GitHub profile. (Guessing from CorpusName HarshS99/Project_TITAN)
    webbrowser.open("https://github.com/HarshS99")
    
    print("Waiting 5 seconds for the browser and page to load...")
    time.sleep(5)
    
    print("Taking a screenshot of the GitHub page...")
    try:
        res2 = toolkit.take_screenshot_and_read_image(
            filename="github_screenshot.png",
            save_to_file=True,
            read_image=False
        )
        print("Result:", res2)
    except Exception as e:
        print(f"Error taking GitHub screenshot: {e}")

    print("\nAll done!")

if __name__ == "__main__":
    main()
