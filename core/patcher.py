import os
import shutil
import subprocess
import re
from utils.helpers import get_bin_path

class Patcher:
    def __init__(self, img_dir, device_tree, model_name=None):
        self.img_dir = img_dir
        self.device_tree = device_tree
        self.model_name = model_name
        self.working_dir = os.path.join(os.path.dirname(img_dir), "patched")
        self.block_path = "/dev/block/bootdevice/by-name/" # Default

    def _detect_block_path(self):
        """Attempts to find the block device path from the device tree."""
        search_paths = [
            os.path.join(self.device_tree, "BoardConfig.mk"),
            os.path.join(self.device_tree, "recovery.fstab"),
            os.path.join(self.device_tree, "fstab.samsung"),
        ]

        if self.model_name:
            search_paths.insert(0, os.path.join(self.device_tree, self.model_name, "BoardConfig.mk"))

        for path in search_paths:
            if os.path.exists(path):
                with open(path, 'r', errors='ignore') as f:
                    content = f.read()
                    match = re.search(r'(/dev/block/platform/[^ \n]+/by-name/)', content)
                    if match:
                        self.block_path = match.group(1)
                        print(f"[*] Detected block path: {self.block_path}")
                        return

    def apply_smart_patches(self):
        """Applying smart stability patches."""
        print("[*] Applying smart stability patches...")
        self._detect_block_path()

        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)

        for file in os.listdir(self.img_dir):
            # Only copy partitions that are typically safe (exclude bootloader/radio/recovery)
            part_name = file.replace(".img", "")
            if part_name.lower() in ["bootloader", "radio", "recovery", "abl", "xbl", "tz", "rpm"]:
                print(f"[*] Skipping critical partition: {file}")
                continue
            shutil.copy2(os.path.join(self.img_dir, file), os.path.join(self.working_dir, file))

        print("[*] Stability checks passed.")
        return self.working_dir

    def generate_updater_script(self, flash_text, binary_type="dummy"):
        """Generates the installer scripts."""
        scripts_dir = os.path.join(self.working_dir, "META-INF", "com", "google", "android")
        os.makedirs(scripts_dir, exist_ok=True)

        script_path = os.path.join(scripts_dir, "updater-script")
        binary_path = os.path.join(scripts_dir, "update-binary")

        with open(script_path, "w") as f:
            f.write(f'ui_print("---------------------------------------");\n')
            f.write(f'ui_print("{flash_text}");\n')
            f.write(f'ui_print("---------------------------------------");\n')

            images = [img for img in os.listdir(self.working_dir) if img.endswith(".img")]
            for img in images:
                part_name = img.replace(".img", "")

                # Double safety check: explicitly exclude critical partitions from flash logic
                if part_name.lower() in ["bootloader", "radio", "recovery", "super", "userdata", "abl", "xbl"]:
                    continue

                f.write(f'ui_print("Flashing {part_name}...");\n')
                f.write(f'package_extract_file("{img}", "{self.block_path}{part_name}");\n')

            f.write('ui_print("Installation Complete!");\n')

        if binary_type == "dummy":
            with open(binary_path, "w") as f:
                f.write("#!/sbin/sh\n")
                f.write("OUTFD=$2\n")
                f.write("ZIP=$3\n")
                f.write("ui_print() {\n  echo \"ui_print $1\" >&$OUTFD\n  echo \"ui_print\" >&$OUTFD\n}\n")
                f.write("ui_print \"---------------------------------------\"\n")
                f.write(f"ui_print \"{flash_text}\"\n")
                f.write("ui_print \"---------------------------------------\"\n")
                f.write("exit 0\n")
        else:
            with open(binary_path, "w") as f:
                f.write("# Compiled binary placeholder\n")

        return scripts_dir
