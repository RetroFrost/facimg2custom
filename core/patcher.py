import os
import shutil
import subprocess
import re
import platform
import requests
import zipfile
from utils.helpers import get_bin_path
from core.metadata import MetadataTracker

class PropPatcher:
    def patch(self, prop_path, target_info):
        if not os.path.exists(prop_path): return
        print(f"[*] Deep patching properties: {prop_path}")
        try:
            with open(prop_path, 'r', errors='ignore') as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if any(p in line for p in ["ro.product.model=", "ro.product.brand=", "ro.product.device=", "ro.product.name="]):
                    key = line.split('=')[0]
                    suffix = key.split('.')[-1]
                    if suffix in target_info:
                         line = f"{key}={target_info[suffix]}\n"
                new_lines.append(line)
            with open(prop_path, 'w') as f:
                f.writelines(new_lines)
        except Exception as e: print(f"[!] Prop patching failed: {e}")

class Patcher:
    def __init__(self, img_dir, device_tree=None, model_name=None, base_img_dir=None):
        self.img_dir = img_dir
        self.device_tree = device_tree
        self.model_name = model_name
        self.base_img_dir = base_img_dir
        self.working_dir = os.path.join(os.path.dirname(img_dir), "patched")
        self.block_path = "/dev/block/bootdevice/by-name/"
        self.partition_sizes = {}
        self.device_info = {}
        self.processed_files = set()
        self.prop_patcher = PropPatcher()
        self.meta_tracker = MetadataTracker(os.path.join(self.working_dir, "metadata.json"))

    def _find_file(self, base_name):
        if not self.device_tree or not os.path.isdir(self.device_tree): return None
        search_dirs = [self.device_tree]
        if self.model_name: search_dirs.insert(0, os.path.join(self.device_tree, self.model_name))
        for d in search_dirs:
            for ext in ["", ".mk"]:
                path = os.path.join(d, base_name + ext)
                if os.path.exists(path): return path
        return None

    def _read_recursive(self, file_path):
        if not file_path or file_path in self.processed_files: return ""
        self.processed_files.add(file_path)
        content = ""
        try:
            with open(file_path, 'r', errors='ignore') as f:
                lines = f.readlines()
                for line in lines:
                    content += line
                    match = re.search(r'(?:include|inherit-product),\s*[\$\(]*DEVICE_PATH[\)]*/?([^ \n\)]+)', line)
                    if match:
                        target_path = self._find_file(match.group(1).replace(".mk", ""))
                        if target_path: content += "\n" + self._read_recursive(target_path)
        except Exception as e: print(f"[!] Error reading {file_path}: {e}")
        return content

    def flatten_apex_modules(self, system_dir):
        """Unpacks all .apex modules into the flattened /system/apex structure."""
        apex_dir = os.path.join(system_dir, "apex")
        if not os.path.exists(apex_dir): return
        print("[*] Flattening APEX modules for non-Google hardware...")
        for file in os.listdir(apex_dir):
            if file.endswith(".apex"):
                apex_path = os.path.join(apex_dir, file)
                module_name = file.replace(".apex", "")
                target_dir = os.path.join(apex_dir, module_name)
                try:
                    # Apex is basically a zip containing an image
                    with zipfile.ZipFile(apex_path, 'r') as zip_ref:
                        zip_ref.extractall(target_dir)
                    os.remove(apex_path)
                    print(f"[*] Flattened: {module_name}")
                except Exception as e:
                    print(f"[!] Failed to flatten {file}: {e}")

    def patch_boot_image(self, boot_path):
        bin_dir = get_bin_path()
        magiskboot = os.path.join(bin_dir, "magiskboot.exe" if platform.system()=="Windows" else "magiskboot")
        if not os.path.exists(magiskboot): return
        print(f"[*] Performing Advanced Ramdisk surgery: {boot_path}")
        old_cwd = os.getcwd()
        tmp_patch_dir = os.path.join(self.working_dir, "boot_patch_tmp")
        os.makedirs(tmp_patch_dir, exist_ok=True)
        shutil.copy2(boot_path, os.path.join(tmp_patch_dir, "boot.img"))
        os.chdir(tmp_patch_dir)
        try:
            subprocess.run([magiskboot, "unpack", "boot.img"], check=True, creationflags=0x08000000 if platform.system()=="Windows" else 0)
            for root, dirs, files in os.walk("."):
                for file in files:
                    if "fstab" in file:
                        f_path = os.path.join(root, file)
                        with open(f_path, 'r') as f: lines = f.readlines()
                        new_lines = []
                        for line in lines:
                            line = re.sub(r',avb[=\w\d\.]*', '', line)
                            line = re.sub(r',verify', '', line)
                            line = re.sub(r',fileencryption=[=\w\d\.]*', '', line)
                            if " /" in line and "wait" in line and "nofail" not in line:
                                    line = line.replace("wait", "wait,nofail,latemount")
                            new_lines.append(line)
                        with open(f_path, 'w') as f: f.writelines(new_lines)
                    if file.endswith(".rc"):
                        f_path = os.path.join(root, file)
                        with open(f_path, 'r') as f: content = f.read()
                        content = re.sub(r'(service\s+(?:vaultkeeper|sced|secure_storage|sec_gnss|gatekeeper|keymaster).*)', r'# \1', content)
                        with open(f_path, 'w') as f: f.write(content)
            subprocess.run([magiskboot, "repack", "boot.img", "new-boot.img"], check=True, creationflags=0x08000000 if platform.system()=="Windows" else 0)
            shutil.move("new-boot.img", boot_path)
        except Exception as e: print(f"[!] Ramdisk surgery failed: {e}")
        finally:
            os.chdir(old_cwd)
            shutil.rmtree(tmp_patch_dir, ignore_errors=True)

    def apply_smart_patches(self, use_blank_vbmeta=True, advanced_fixes=True):
        print("[*] Starting Actual Porting Engine...")
        all_content = ""
        if self.device_tree and os.path.isdir(self.device_tree):
            for base in ["BoardConfig", "device", "recovery.fstab", "fstab.samsung"]:
                f_path = self._find_file(base)
                if f_path: all_content += self._read_recursive(f_path)
        match = re.search(r'(/dev/block/(?:platform/[^ \n]+/)?by-name/)', all_content)
        if match: self.block_path = match.group(1)
        if not os.path.exists(self.working_dir): os.makedirs(self.working_dir)

        for file in os.listdir(self.img_dir):
            if file.replace(".img", "").lower() in ["system", "product", "system_ext"]:
                shutil.copy2(os.path.join(self.img_dir, file), os.path.join(self.working_dir, file))
                # If we could mount images, we would run flatten_apex_modules here

        if self.base_img_dir and os.path.isdir(self.base_img_dir):
            hardware_parts = ["boot.img", "vendor.img", "dtbo.img", "prism.img", "odm.img", "optics.img", "vbmeta.img", "init_boot.img", "vendor_boot.img"]
            for part in hardware_parts:
                base_file = os.path.join(self.base_img_dir, part)
                if os.path.exists(base_file):
                    if part == "vbmeta.img" and use_blank_vbmeta: continue
                    dst_path = os.path.join(self.working_dir, part)
                    shutil.copy2(base_file, dst_path)
                    if part == "boot.img" and advanced_fixes: self.patch_boot_image(dst_path)

        if advanced_fixes:
            system_prop = self._find_file("system.prop")
            if system_prop:
                info = {'model': self.model_name or 'Pixel Port', 'device': self.model_name or 'generic'}
                self.prop_patcher.patch(system_prop, info)

        if use_blank_vbmeta:
            with open(os.path.join(self.working_dir, "vbmeta.img"), 'wb') as f: f.write(b'\x00' * 256)

        self.meta_tracker.generate_fix_script(os.path.join(self.working_dir, "fix_attrs.sh"))
        return self.working_dir

    def generate_updater_script(self, flash_text, binary_type="dummy"):
        scripts_dir = os.path.join(self.working_dir, "META-INF", "com", "google", "android")
        os.makedirs(scripts_dir, exist_ok=True)
        binary_path = os.path.join(scripts_dir, "update-binary")
        images = [img for img in os.listdir(self.working_dir) if img.endswith((".img", ".bin"))]
        if binary_type == "dummy":
            with open(binary_path, "w", newline='\n') as f:
                f.write("#!/sbin/sh\nOUTFD=$2\nZIP=$3\nui_print() { echo \"ui_print $1\" >&$OUTFD; echo \"ui_print\" >&$OUTFD; }\n")
                f.write("ui_print \"---------------------------------------\"\n")
                f.write(f"ui_print \"{flash_text}\"\n")
                f.write("ui_print \"---------------------------------------\"\n")
                flash_order = ["boot", "init_boot", "vendor_boot", "dtbo", "pvmfw", "vbmeta", "vendor", "odm", "prism", "optics", "system", "system_ext", "product"]
                for part in flash_order:
                    for ext in [".img", ".bin"]:
                        img = f"{part}{ext}"
                        if img in images:
                            f.write(f"ui_print \"Flashing {part}...\"\n")
                            f.write(f"unzip -p \"$ZIP\" \"{img}\" | dd of=\"{self.block_path}{part}\" bs=4096\n")
                f.write("ui_print \"Restoring attributes...\"\n")
                f.write("unzip -p \"$ZIP\" fix_attrs.sh > /tmp/fix_attrs.sh\n")
                f.write("chmod 755 /tmp/fix_attrs.sh; /tmp/fix_attrs.sh\n")
                f.write("ui_print \"Installation Complete!\"\nexit 0\n")
        return scripts_dir
