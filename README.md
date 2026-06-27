# facimg2custom

**facimg2custom** is a smart, interactive Python tool designed to simplify the process of porting Google Pixel factory images to other devices. It converts official factory images into flashable custom ROM `.ZIP` files, handling the heavy lifting of stability patches and partition management automatically.

Whether you're working with a modern device using dynamic partitions or a legacy Samsung device, **facimg2custom** aims to make porting convenient and bug-free for general users.

---

## 🚀 Features

- **Smart Porting Logic**: Automatically handles common porting hurdles like `fstab` configurations and partition resizing.
- **Legacy & Modern Support**: Built-in compatibility for Samsung-style legacy partition schemes as well as modern A/B and Dynamic Partition schemes.
- **Unified Tree Support**: Point the tool at a unified device tree, and it will interactively list and let you select the specific model you're targeting (e.g., beyond0lte, beyond1lte, beyond2lte).
- **Highly Customizable**:
    - **Flash Text**: Personalize the text displayed during the installation process in recovery (obligatory step).
    - **Post-Flash Files**: Easily include additional files or scripts to be executed after the main ROM is flashed.
    - **Update Binary**: Choose between using a dummy (new) binary or a compiled `update-binary` for maximum compatibility.
- **Interactive CLI**: No complex configuration files required—the tool guides you through the process step-by-step.

---

## 🛠️ Requirements

- **Python 3.x**: The core tool is built on Python for cross-platform compatibility (works great on Windows!).
- **Pixel Factory Image**: The official `.zip` from Google for the version of Android you wish to port.
- **Device Tree**: The device-specific configuration (containing `BoardConfig.mk`, `device.mk`, etc.) for your target hardware.

---

## 📖 How to Use

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/facimg2custom.git
   cd facimg2custom
   ```

2. **Run the tool**:
   ```bash
   python main.py
   ```

3. **Follow the interactive prompts**:
   - Provide the path to your **Pixel Factory Image**.
   - Provide the path to your **Device Tree** folder.
   - If a unified tree is detected, select your model from the list (1, 2, 3...).
   - Customize your `updater-script` flash text.
   - Choose between a raw script or one with custom flash text.
   - Select your `update-binary` type.
   - Add any optional post-flash files.

4. **Flash**: Once the process completes, you'll have a flashable `.zip` ready for your device's recovery.

---

## ⚠️ Disclaimer & Status

**Project Status: Work In Progress (WIP)**

While **facimg2custom** is designed to be "smart" and prevent bricks, Android porting is inherently risky. Always ensure you have a full backup of your data and a way to restore your device to a functional state (like Odin for Samsung or Fastboot for others) before flashing.

*Use this tool at your own risk. The developers are not responsible for any damage to your hardware.*

---

## 🤝 Contributing

This is an open-source project! If you have ideas for better stability patches or support for more legacy devices, feel free to open a Pull Request or an Issue.
