# facimg2custom

**facimg2custom** is the "Rufus for Pixel Ports"—an advanced, universal Android porting engine designed to automate the conversion of Google Pixel factory images into flashable custom ROMs. It intelligently merges the software "brain" of a Pixel device with the hardware "skeleton" of your target device, applying industry-standard stability fixes and security neutralization automatically.

Whether you're porting to a Samsung Galaxy with its unique partition layout (Prism, Optics, Keyrefuge) or any other device with Dynamic/AB partitions, **facimg2custom** provides a streamlined, one-click interactive workflow.

---

## 🚀 Key Features

- **Rufus-Style Simplicity**: A compact, easy-to-use GUI that makes porting accessible to everyone.
- **Universal Smart Patching**: Merges Pixel system images with native device hardware partitions (`boot`, `init_boot`, `vendor`, `dtbo`, `pvmfw`, etc.).
- **Advanced Ramdisk Surgery**:
    - Automatically unpacks and repacks `boot.img` using `magiskboot`.
    - **FSTAB Neutralization**: Strips AVB, Verity, and Samsung-proprietary encryption flags.
    - **Service Neutralization**: Automatically disables conflicting hardware services (Vaultkeeper, SCED, Secure Storage).
- **Comprehensive Hardware Support**: Handles "forgotten" partitions and binary blobs like `up_param.bin`, `cm.bin`, and `uh.bin`.
- **Metadata Preservation**: Tracks and restores Unix symlinks and file permissions lost during extraction on Windows using a recovery-side script (`fix_attrs.sh`).
- **Samsung Specialized Logic**:
    - Full support for `.tar` and `.tar.md5` firmware files.
    - Automatic extraction of hardware blobs from Samsung `super.img`.
- **Safe by Design**: Explicitly protects critical partitions (Bootloader, Radio, Recovery) from being touched.

---

## 🛠️ Requirements

- **Python 3.12+** (Windows optimized).
- **Pixel Factory Image**: The official `.zip` from Google.
- **Base Device Firmware**: Your device's stock `AP` file (Samsung) or partition images.
- **Device Tree (Optional)**: Folder containing `BoardConfig.mk` for automated configuration.

---

## 📖 How to Use

1. **Launch**: Run `launcher.py`.
2. **Select Sources**:
    - Select your **Pixel Factory Image**.
    - Select your **Base Device Firmware** (Samsung AP or .img folder).
    - Choose your **Output Path**.
3. **Customize**: Enter your recovery flash text and check "Advanced Industry Fixes".
4. **Convert**: Click the big **START CONVERSION** button and wait for completion.

---

## ⚠️ Disclaimer

Android porting is high-risk. This is an Alpha-stage automated tool. Always maintain a full backup and have restoration tools (Odin/Fastboot) ready. The developers are not responsible for any device damage.
