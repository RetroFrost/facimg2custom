import os
import zipfile
import time

class Packager:
    def __init__(self, working_dir, post_flash_files=None):
        self.working_dir = working_dir
        self.post_flash_files = post_flash_files or []

    def create_zip(self, output_zip_path):
        """Bundles everything into a flashable ZIP and generates a symlink fix script."""
        print(f"[*] Packaging final ROM to: {output_zip_path}")

        # 1. Generate fix_symlinks.sh (Stub for now)
        symlink_script = os.path.join(self.working_dir, "fix_symlinks.sh")
        with open(symlink_script, 'w', newline='\n') as f:
            f.write("#!/sbin/sh\n")
            f.write("# This script restores symlinks that were lost during extraction on Windows\n")
            f.write("mount /system\n")
            f.write("# ln -s /system/bin/app_process32 /system/bin/app_process\n")
            f.write("umount /system\n")

        # Ensure output directory exists
        out_dir = os.path.dirname(output_zip_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        if os.path.exists(output_zip_path):
            os.remove(output_zip_path)

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(self.working_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.working_dir)
                    zip_ref.write(full_path, rel_path)

            if self.post_flash_files:
                for f_path in self.post_flash_files:
                    if os.path.exists(f_path):
                        target_path = os.path.join("post_flash", os.path.basename(f_path))
                        zip_ref.write(f_path, target_path)

        time.sleep(1)
        if not os.path.exists(output_zip_path):
            raise Exception(f"Packaging Error: {output_zip_path} was not created.")

        return output_zip_path
