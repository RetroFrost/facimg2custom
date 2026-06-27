# facimg2custom

**facimg2custom** is a smart, interactive Python tool designed to simplify the process of porting Google Pixel factory images to other devices (specifically targeting Samsung). It converts official factory images into flashable custom ROM `.ZIP` files, handling the heavy lifting of stability patches, security HAL adaptation, and partition management automatically.

Whether you're working with a modern device using dynamic partitions or a legacy Samsung device, **facimg2custom** aims to make porting convenient and bug-free for general users.

---

## 🚀 Features

- **Smart Porting Logic**: Automatically handles common porting hurdles like `fstab` configurations and partition resizing.
- **Safe by Design**: Explicitly excludes critical partitions like **Bootloader**, **Radio**, and **Recovery** to prevent permanent bricks. Focuses solely on porting the Pixel system.
- **Samsung & Legacy Optimization**:
    - Support for `.tar` and `.tar.md5` Samsung AP files.
    - Automatic extraction of hardware partitions (`prism`, `odm`, `optics`) from Samsung `super.img`.
    - **Neutralization Logic**: Automatically disables conflicting Samsung services in `prism` and adapts `fstab` mount flags (`nofail`, `latemount`) to prevent bootloops.
    - **Security HAL Adaptation**: Prioritizes Samsung-specific Keymaster and Gatekeeper blobs for hardware-backed security.
- **AVB Disabler**: Option to automatically generate and include a blank `vbmeta.img` to bypass Android Verified Boot.
- **Unified Tree Support**: Point the tool at a unified device tree, and it will interactively list and let you select the specific model you're targeting (e.g., beyond0lte, beyond1lte, beyond2lte).
- **Highly Customizable**:
    - **Flash Text**: Personalize the text displayed during the installation process in recovery (obligatory step).
    - **Post-Flash Files**: Easily include additional files or scripts to be executed after the main ROM is flashed.
    - **Update Binary**: Choose between using a dummy (shell script) binary or a compiled `update-binary`.
- **Graphical User Interface (GUI)**: A clean, intuitive Tkinter interface—no complex command lines required.

---

## 🛠️ Requirements

- **Python 3.12+**: Built on Python for cross-platform compatibility (optimized for Windows).
- **Pixel Factory Image**: The official `.zip` from Google for the version of Android you wish to port.
- **Samsung AP File**: The stock Samsung firmware file (`AP_*.tar.md5`) for your device.
- **Device Tree (Optional)**: The device-specific configuration (containing `BoardConfig.mk`, `device.mk`, etc.) for advanced patching.

---

## 📖 How to Use

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/facimg2custom.git
   cd facimg2custom
   ```

2. **Run the tool**:
   ```bash
   python launcher.py
   ```

3. **Select your files**:
   - **Pixel Factory Image**: Select the Google ZIP.
   - **Samsung AP**: Select your firmware `.tar` or `.tar.md5`.
   - **Device Tree**: (Optional) Select the folder if you have a custom tree.

4. **Customize**:
   - Enter your **Flash Text**.
   - Enable/Disable **Blank VBMeta** (Recommended for Samsung).
   - Add any **Post-Flash Files**.

5. **Start Conversion**: Click **START CONVERSION** and wait for the "pixel_port.zip" to be generated.

---

## 🛠️ How it Works

**facimg2custom** follows a rigorous multi-step process to ensure a stable port:

1.  **Dependency Verification**: Automatically downloads necessary binaries like `simg2img`, `magiskboot`, `lz4`, and `lpunpack`.
2.  **Factory Image Extraction**: Unpacks the Pixel ZIP and its nested images.
3.  **Samsung Extraction**: Unpacks the AP file, decompresses LZ4 images, and unpacks `super.img` to extract hardware-specific partitions.
4.  **Smart Patching & Neutralization**:
    - Disables Samsung services in `prism`.
    - Fixes `fstab` mount points for `prism`, `optics`, and `keyrefuge`.
    - Generates a blank `vbmeta.img` disabler.
5.  **Installer Generation**: Creates a customized `updater-script` that flashes partitions in the correct order (Hardware -> Software).
6.  **Final Packaging**: Bundles everything into a flashable `.zip`.

---

## ⚠️ Disclaimer & Status

**Project Status: Alpha / Work In Progress (WIP)**

While **facimg2custom** is designed to prevent bricks, Android porting is inherently risky. Always ensure you have a full backup and a way to restore your device (like Odin) before flashing.

*Use this tool at your own risk. The developers are not responsible for any damage to your hardware.*
