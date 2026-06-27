import os
import zipfile

class Packager:
    def __init__(self, working_dir, post_flash_files=None):
        self.working_dir = working_dir
        self.post_flash_files = post_flash_files or []

    def create_zip(self, output_zip_path):
        """Bundles everything in the working directory into a flashable ZIP."""
        print(f"[*] Packaging final ROM to: {output_zip_path}")

        # Ensure output directory exists
        out_dir = os.path.dirname(output_zip_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            # 1. Add images and META-INF (installer)
            for root, dirs, files in os.walk(self.working_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.working_dir)
                    zip_ref.write(full_path, rel_path)
                    print(f"[*] Adding to ZIP: {rel_path}")

            # 2. Add post-flash files if any
            if self.post_flash_files:
                print("[*] Adding post-flash files...")
                for f_path in self.post_flash_files:
                    if os.path.exists(f_path):
                        target_path = os.path.join("post_flash", os.path.basename(f_path))
                        zip_ref.write(f_path, target_path)
                        print(f"[*] Added post-flash: {target_path}")

        return output_zip_path
