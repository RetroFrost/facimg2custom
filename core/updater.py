import os
import requests
import zipfile
import shutil
import sys
import subprocess

REPO_ZIP_URL = "https://codeload.github.com/RetroFrost/facimg2custom/zip/refs/heads/create-readme-idea-6690560623530223609"

class Updater:
    def __init__(self, current_version="1.0.0"):
        self.current_version = current_version
        self.update_dir = "update_tmp"

    def check_for_updates(self):
        """Checks if a new version is available on GitHub and triggers redownload."""
        print("[*] Checking for updates...")
        try:
            # In a real scenario, we'd check a version file first.
            # For this task, we assume we always want to pull the latest from the branch.
            self._download_and_apply_update()
            return True
        except Exception as e:
            print(f"[!] Update check failed: {e}")
            return False

    def _download_and_apply_update(self):
        print(f"[*] Downloading update from {REPO_ZIP_URL}...")
        r = requests.get(REPO_ZIP_URL, timeout=30)
        r.raise_for_status()

        if os.path.exists(self.update_dir):
            shutil.rmtree(self.update_dir)
        os.makedirs(self.update_dir)

        zip_path = os.path.join(self.update_dir, "update.zip")
        with open(zip_path, 'wb') as f:
            f.write(r.content)

        print("[*] Extracting update...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.update_dir)

        # Find the extracted folder (GitHub ZIPs usually have a folder inside)
        extracted_folder = None
        for item in os.listdir(self.update_dir):
            if os.path.isdir(os.path.join(self.update_dir, item)):
                extracted_folder = os.path.join(self.update_dir, item)
                break

        if not extracted_folder:
            print("[!] Could not find update content.")
            return

        # Prepare a batch script to replace files and relaunch (Windows specific)
        self._create_windows_updater_script(extracted_folder)
        print("[*] Update ready. Application will restart.")
        sys.exit(0)

    def _create_windows_updater_script(self, src_folder):
        """Creates a .bat file to move files and restart the app after exit."""
        batch_path = "update_apply.bat"
        app_path = os.getcwd()

        # We need to quote paths in case they have spaces
        src = os.path.abspath(src_folder)
        dst = os.path.abspath(app_path)

        with open(batch_path, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 /nobreak > nul\n") # Wait for app to close
            f.write(f'xcopy "{src}\\*" "{dst}\\" /E /I /Y\n')
            f.write(f'rd /s /q "{os.path.abspath(self.update_dir)}"\n')
            f.write(f'start python launcher.py\n')
            f.write(f'del "%~f0"\n') # Delete itself

        # Execute the batch script and detached
        subprocess.Popen(["cmd", "/c", batch_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
