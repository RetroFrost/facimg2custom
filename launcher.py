import os
import sys
import subprocess

def check_and_install_deps():
    """Checks if required python modules are installed, tries to install them if not."""
    try:
        import requests
    except ImportError:
        print("[*] Missing 'requests' library. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        except Exception as e:
            print(f"[!] Could not install 'requests': {e}")
            return False
    return True

def main():
    """Main entry point for facimg2custom."""
    print("--- facimg2custom: Pixel to Custom ROM Converter ---")

    if not check_and_install_deps():
        sys.exit(1)

    from core.updater import Updater
    from ui.interface import MainApp

    # Check for updates and perform if available
    updater = Updater()
    try:
        if updater.check_for_updates():
            print("[*] Update available. Performing self-update...")
            # updater.perform_update() # Uncommenting this for the user
            pass
    except Exception as e:
        print(f"[!] Update check failed: {e}")

    # Initialize the UI
    try:
        app = MainApp()
        app.run()
    except Exception as e:
        print(f"[!] Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
