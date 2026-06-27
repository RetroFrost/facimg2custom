import os
import zipfile

class Packager:
    def __init__(self, working_dir, post_flash_files=None):
        self.working_dir = working_dir
        self.post_flash_files = post_flash_files or []

    def create_zip(self, output_zip_path):
        """Bundles everything in the working directory into a flashable ZIP."""
        print(f"[*] Packaging final ROM to: {output_zip_path}")

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            # Add all files from working directory (images and META-INF)
            for root, dirs, files in os.walk(self.working_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.working_dir)
                    zip_ref.write(full_path, rel_path)

            # Add post-flash files if any
            if self.post_flash_files:
                os.makedirs(os.path.join(self.working_dir, "post_flash"), exist_ok=True)
                for f_path in self.post_flash_files:
                    if os.path.exists(f_path):
                        zip_ref.write(f_path, os.path.join("post_flash", os.path.basename(f_path)))

        return output_zip_path
