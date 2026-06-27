import os
import shutil
import subprocess
import re
import platform
import requests
from utils.helpers import get_bin_path

COMPILED_BINARY_URL = "https://github.com/S-Trace/android-update-binary/raw/master/arm64-v8a/update-binary"

class Patcher:
    def __init__(self, img_dir, device_tree, model_name=None):
        self.img_dir = img_dir
        self.device_tree = device_tree
        self.model_name = model_name
        self.working_dir = os.path.join(os.path.dirname(img_dir), "patched")
        self.block_path = "/dev/block/bootdevice/by-name/"
        self.partition_sizes = {}
        self.device_info = {}
        self.processed_files = set()

    def _find_file(self, base_name):
        """Finds a file in the device tree with or without .mk extension."""
        search_dirs = [self.device_tree]
        if self.model_name:
            search_dirs.insert(0, os.path.join(self.device_tree, self.model_name))

        for d in search_dirs:
            for ext in ["", ".mk"]:
                path = os.path.join(d, base_name + ext)
                if os.path.exists(path):
                    return path
        return None

    def _read_recursive(self, file_path):
        """Reads a file and recursively follows includes/inherits."""
        if not file_path or file_path in self.processed_files:
            return ""

        self.processed_files.add(file_path)
        content = ""
        try:
            with open(file_path, 'r', errors='ignore') as f:
                lines = f.readlines()
                for line in lines:
                    content += line
                    # Match include $(DEVICE_PATH)/filename or include filename
                    include_match = re.search(r'include\s+[\$\(]*DEVICE_PATH[\)]*/?([^ \n\)]+)', line)
                    inherit_match = re.search(r'inherit-product,\s*[\$\(]*DEVICE_PATH[\)]*/?([^ \n\)]+)', line)

                    target = None
                    if include_match: target = include_match.group(1)
                    elif inherit_match: target = inherit_match.group(1)

                    if target:
                        target_base = target.replace(".mk", "")
                        target_path = self._find_file(target_base)
                        if target_path:
                            content += "\n" + self._read_recursive(target_path)
        except Exception as e:
            print(f"[!] Error reading {file_path}: {e}")

        return content

    def _detect_block_path(self, content):
        """Attempts to find the block device path from the gathered content."""
        match = re.search(r'(/dev/block/platform/[^ \n]+/by-name/)', content)
        if match:
            self.block_path = match.group(1)
            print(f"[*] Detected block path: {self.block_path}")

    def _extract_device_info(self, content):
        """Extracts technical info from the gathered content."""
        matches = re.findall(r'BOARD_(\w+IMAGE)_PARTITION_SIZE\s*:=\s*(\d+)', content)
        for part, size in matches:
            self.partition_sizes[part.lower().replace("image", "")] = int(size)

        sw = re.search(r'TARGET_SCREEN_WIDTH\s*:=\s*(\d+)', content)
        sh = re.search(r'TARGET_SCREEN_HEIGHT\s*:=\s*(\d+)', content)
        if sw: self.device_info['width'] = sw.group(1)
        if sh: self.device_info['height'] = sh.group(1)

        plt = re.search(r'TARGET_BOARD_PLATFORM\s*:=\s*(\w+)', content)
        if plt: self.device_info['platform'] = plt.group(1)

    def apply_smart_patches(self):
        """Applying smart stability patches."""
        print("[*] Starting Smart Patching...")
        all_content = ""
        for base in ["BoardConfig", "device", "recovery.fstab", "fstab.samsung"]:
            f_path = self._find_file(base)
            if f_path:
                all_content += self._read_recursive(f_path)

        self._detect_block_path(all_content)
        self._extract_device_info(all_content)

        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)

        for file in os.listdir(self.img_dir):
            part_name = file.replace(".img", "")
            if part_name.lower() in ["bootloader", "radio", "recovery", "abl", "xbl", "tz", "rpm"]:
                continue

            src_file = os.path.join(self.img_dir, file)
            dst_file = os.path.join(self.working_dir, file)
            shutil.copy2(src_file, dst_file)

        print("[*] Smart Patching completed.")
        return self.working_dir

    def generate_updater_script(self, flash_text, binary_type="dummy"):
        """Generates the installer scripts."""
        scripts_dir = os.path.join(self.working_dir, "META-INF", "com", "google", "android")
        os.makedirs(scripts_dir, exist_ok=True)

        script_path = os.path.join(scripts_dir, "updater-script")
        binary_path = os.path.join(scripts_dir, "update-binary")

        images = [img for img in os.listdir(self.working_dir) if img.endswith(".img")]

        if binary_type == "dummy":
            with open(binary_path, "w", newline='\n') as f:
                f.write("#!/sbin/sh\n")
                f.write("OUTFD=$2\n")
                f.write("ZIP=$3\n")
                f.write("ui_print() {\n  echo \"ui_print $1\" >&$OUTFD\n  echo \"ui_print\" >&$OUTFD\n}\n")
                f.write("ui_print \"---------------------------------------\"\n")
                f.write(f"ui_print \"{flash_text}\"\n")
                f.write("ui_print \"---------------------------------------\"\n")
                for img in images:
                    part_name = img.replace(".img", "")
                    if part_name.lower() in ["bootloader", "radio", "recovery", "super", "userdata", "abl"]: continue
                    f.write(f"ui_print \"Flashing {part_name}...\"\n")
                    f.write(f"unzip -p \"$ZIP\" \"{img}\" | dd of=\"{self.block_path}{part_name}\" bs=4096\n")
                f.write("ui_print \"Installation Complete!\"\n")
                f.write("exit 0\n")
        else:
            print("[*] Downloading compiled update-binary...")
            try:
                r = requests.get(COMPILED_BINARY_URL, timeout=10)
                r.raise_for_status()
                with open(binary_path, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                print(f"[!] Failed to download update-binary: {e}")
                return self.generate_updater_script(flash_text, "dummy")

            with open(script_path, "w") as f:
                f.write(f'ui_print("---------------------------------------");\n')
                f.write(f'ui_print("{flash_text}");\n')
                f.write(f'ui_print("---------------------------------------");\n')
                for img in images:
                    part_name = img.replace(".img", "")
                    if part_name.lower() in ["bootloader", "radio", "recovery", "super", "userdata"]: continue
                    f.write(f'ui_print("Flashing {part_name}...");\n')
                    f.write(f'package_extract_file("{img}", "{self.block_path}{part_name}");\n')
                f.write('ui_print("Installation Complete!");\n')

        return scripts_dir
