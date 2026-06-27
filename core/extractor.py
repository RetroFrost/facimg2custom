import os
import zipfile
import shutil
import subprocess
import platform
from utils.helpers import get_bin_path

class Extractor:
    def __init__(self, pixel_zip, output_dir):
        self.pixel_zip = pixel_zip
        self.output_dir = output_dir
        self.extracted_path = os.path.join(output_dir, "extracted_pixel")
        self.nested_zip_path = None

    def extract_main_zip(self):
        """Unzips the main factory image and finds the nested image zip."""
        """Unzips the main factory image to find the nested image zip."""
        print(f"[*] Extracting main Pixel zip: {self.pixel_zip}")
        if not os.path.exists(self.extracted_path):
            os.makedirs(self.extracted_path)

        with zipfile.ZipFile(self.pixel_zip, 'r') as zip_ref:
            zip_ref.extractall(self.extracted_path)

        for root, dirs, files in os.walk(self.extracted_path):
            for file in files:
                if file.startswith("image-") and file.endswith(".zip"):
                    self.nested_zip_path = os.path.join(root, file)
                    print(f"[*] Found nested image zip: {file}")
                    return self.nested_zip_path

        raise Exception("Nested image zip not found in factory image!")
        # Find the nested image zip (usually starts with 'image-')
        for file in os.listdir(self.extracted_path):
            if file.startswith("image-") and file.endswith(".zip"):
                self.nested_zip_path = os.path.join(self.extracted_path, file)
                break

        raise Exception("Nested image zip not found in factory image!")

    def extract_nested_zip(self):
        """Unzips the nested image zip containing .img files."""
        if not self.nested_zip_path:
            raise Exception("Nested zip path not set!")

        img_extract_path = os.path.join(self.extracted_path, "images")
        print(f"[*] Extracting nested images: {self.nested_zip_path}")

        with zipfile.ZipFile(self.nested_zip_path, 'r') as zip_ref:
            zip_ref.extractall(img_extract_path)

        for root, dirs, files in os.walk(img_extract_path):
            if root == img_extract_path: continue
            for file in files:
                if file.endswith(".img"):
                    shutil.move(os.path.join(root, file), os.path.join(img_extract_path, file))

        return img_extract_path

    def convert_sparse_images(self, img_dir):
        """Converts sparse Android images to raw if necessary."""
        bin_dir = get_bin_path()
        binary_name = "simg2img.exe" if platform.system() == "Windows" else "simg2img"
        simg2img = os.path.join(bin_dir, binary_name)

        if not os.path.exists(simg2img):
            return

        for file in os.listdir(img_dir):
            if file.endswith(".img") and file in ["system.img", "vendor.img", "product.img", "system_ext.img"]:
                input_img = os.path.join(img_dir, file)
                output_img = os.path.join(img_dir, f"raw_{file}")

                try:
                    subprocess.run([simg2img, input_img, output_img], check=True, creationflags=0x08000000 if platform.system()=="Windows" else 0)
                    os.remove(input_img)
                    os.rename(output_img, input_img)
                except:
                    pass
                print(f"[*] Checking/Converting sparse image: {file}")
                try:
                    subprocess.run([simg2img, input_img, output_img], check=True, creationflags=0x08000000 if platform.system()=="Windows" else 0)
                    os.remove(input_img)
                    os.rename(output_img, input_img)
                except:
                    pass
