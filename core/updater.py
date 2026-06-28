import os
import requests
import zipfile
import shutil
import sys
import subprocess

REPO_API_URL = "https://api.github.com/repos/RetroFrost/facimg2custom/commits/facimg2custom"
REPO_ZIP_URL = "https://codeload.github.com/RetroFrost/facimg2custom/zip/refs/heads/facimg2custom"
VERSION_FILE = ".version"

class Updater:
    def __init__(self):
        self.update_dir = "update_tmp"

    def check_for_updates(self):
        """Checks if the latest commit hash on GitHub differs from the local version."""
        print("[*] Checking for updates...")
        try:
            r = requests.get(REPO_API_URL, timeout=10)
            r.raise_for_status()
            latest_sha = r.json().get('sha')

            current_sha = None
            if os.path.exists(VERSION_FILE):
                with open(VERSION_FILE, 'r') as f:
                    current_sha = f.read().strip()

            if latest_sha and latest_sha != current_sha:
                print(f"[*] New update found: {latest_sha[:7]}")
                self._download_and_apply_update(latest_sha)
                return True
            else:
                print("[*] Already up to date.")
                return False
        except Exception as e:
            print(f"[!] Update check failed: {e}")
            return False

    def _download_and_apply_update(self, new_sha):
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

        with open(VERSION_FILE, 'w') as f:
            f.write(new_sha)

        extracted_folder = None
        for item in os.listdir(self.update_dir):
            if os.path.isdir(os.path.join(self.update_dir, item)):
                extracted_folder = os.path.join(self.update_dir, item)
                break

        if not extracted_folder:
            print("[!] Could not find update content.")
            return

        self._create_windows_updater_script(extracted_folder)
        print("[*] Update applied. Application will restart.")
        sys.exit(0)

    def _create_windows_updater_script(self, src_folder):
        batch_path = "update_apply.bat"
        app_path = os.getcwd()
        src = os.path.abspath(src_folder)
        dst = os.path.abspath(app_path)

        with open(batch_path, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 /nobreak > nul\n")
            f.write(f'xcopy "{src}\\*" "{dst}\\" /E /I /Y\n')
            f.write(f'rd /s /q "{os.path.abspath(self.update_dir)}"\n')
            f.write(f'start python launcher.py\n')
            f.write(f'del "%~f0"\n')

        subprocess.Popen(["cmd", "/c", batch_path], shell=True, creationflags=0x00000010)
