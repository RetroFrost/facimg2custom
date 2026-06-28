import os
import json

class MetadataTracker:
    """Stores and restores Unix metadata (symlinks, permissions) lost on Windows."""
    def __init__(self, metadata_path):
        self.metadata_path = metadata_path
        self.data = {"symlinks": [], "permissions": [], "custom_fixes": []}

        # Hardcoded "Safe-Fall" symlinks for critical Android operation
        self.safe_fall = [
            {"target": "/system/bin/app_process64", "path": "bin/app_process"},
            {"target": "/system/bin/linker64", "path": "bin/linker"},
            {"target": "/system/bin/sh", "path": "bin/shell"},
            {"target": "/system/etc/hosts", "path": "etc/hosts"},
            {"target": "/system/bin/toolbox", "path": "bin/ls"},
            {"target": "/system/bin/toolbox", "path": "bin/cat"}
        ]

    def record_symlink(self, target, link_path):
        self.data["symlinks"].append({"target": target, "path": link_path})

    def record_permission(self, path, mode):
        self.data["permissions"].append({"path": path, "mode": oct(mode)})

    def add_custom_fix(self, cmd):
        self.data["custom_fixes"].append(cmd)

    def save(self):
        with open(self.metadata_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def generate_fix_script(self, output_path):
        """Generates a shell script to restore metadata and fix Setup Wizard permissions."""
        with open(output_path, 'w', newline='\n') as f:
            f.write("#!/sbin/sh\n")
            f.write("# facimg2custom - Advanced Restoration & Setup Fix\n")
            f.write("mount /system\n")

            # 1. Restore Hardcoded Safe-Fall Symlinks
            for s in self.safe_fall:
                f.write(f'ln -sf "{s["target"]}" "/system/{s["path"]}"\n')

            # 2. Restore Recorded Symlinks
            for s in self.data["symlinks"]:
                path = s["path"].replace("\\", "/")
                f.write(f'ln -sf "{s["target"]}" "/system/{path}"\n')

            # 3. Restore Recorded Permissions
            for p in self.data["permissions"]:
                path = p["path"].replace("\\", "/")
                f.write(f'chmod {p["mode"][-4:]} "/system/{path}"\n')

            # 4. Custom Fixes (Properties etc)
            for cmd in self.data["custom_fixes"]:
                f.write(f"{cmd}\n")

            # 5. Setup Wizard Permission Fix
            f.write("pm grant com.google.android.setupwizard android.permission.READ_PHONE_STATE 2>/dev/null\n")
            f.write("pm grant com.google.android.setupwizard android.permission.CAMERA 2>/dev/null\n")
            f.write("pm grant com.google.android.setupwizard android.permission.READ_CONTACTS 2>/dev/null\n")

            f.write("umount /system\n")
