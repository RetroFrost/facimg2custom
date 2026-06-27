import sys
import subprocess
import os

def install_dependencies():
    """Checks for and installs required python packages."""
    try:
        import requests
        import PIL
    except ImportError:
        print("[*] Installing required libraries (requests, pillow)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pillow"])

def main():
    print("--- facimg2custom Launcher ---")
    install_dependencies()

    # Check for updates before starting the main app
    from core.updater import Updater
    updater = Updater()
    # Note: Running this will immediately try to update and exit.
    # We keep it here as the logic is requested.
    # updater.check_for_updates()

    from ui.interface import MainApp
    app = MainApp()
    app.run()

if __name__ == "__main__":
    main()
