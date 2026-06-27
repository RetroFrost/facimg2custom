# facimg2custom

**facimg2custom** is the "Rufus for Pixel Ports"—a professional-grade, universal Android porting engine designed to automate the conversion of Google Pixel factory images into flashable custom ROMs. It intelligently merges the software "brain" of a Pixel device with the hardware "skeleton" of your target device, applying actual porting fixes like APEX flattening and ramdisk surgery automatically.

Whether you're targeting a Samsung Galaxy (S10 to S24) or any other device using Dynamic/AB partitions, **facimg2custom** provides a streamlined, one-click interactive workflow that goes beyond simple image merging.

---

## 🚀 Key Features

- **Actual Porting Engine**: Automatically handles complex hurdles like **APEX Flattening** and **Linker Shimming** to ensure the Pixel system boots on non-Google hardware.
- **Advanced Ramdisk Surgery**:
    - Automatically unpacks and repacks `boot.img` using `magiskboot`.
    - **FSTAB Neutralization**: Strips AVB, Verity, and Samsung-proprietary encryption flags.
    - **Service Neutralization**: Automatically disables conflicting hardware services (Vaultkeeper, SCED, Secure Storage).
- **Comprehensive Partition Support**: Merges all critical partitions including `boot`, `init_boot`, `vendor_boot`, `dtbo`, `pvmfw`, and Samsung-specific binary blobs (`up_param`, `cm.bin`).
- **Metadata Preservation**: Tracks and restores Unix symlinks and file permissions lost during extraction on Windows using a recovery-side script (`fix_attrs.sh`).
- **Samsung Specialized Logic**: Full support for `.tar` and `.tar.md5` firmware with automated hardware blob extraction from Samsung `super.img`.
- **Safe by Design**: Explicitly protects critical partitions (Bootloader, Radio, Recovery) to prevent hard bricks.
- **Rufus-Style Simplicity**: A compact, easy-to-use GUI for Windows with real-time percentage progress tracking.

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

## ⚙️ Technical Deep Dive

**facimg2custom** uses a professional "System-Merge" porting method:

1.  **Attribute Management**: Because Windows does not support Unix file permissions or symlinks, the tool records these attributes during extraction and generates a `fix_attrs.sh` script. This script runs in recovery to restore the system's structural integrity.
2.  **Ramdisk Patching**: The kernel's ramdisk is unpacked to modify the `fstab`. By removing `avb` and `verify` flags and adding `nofail,latemount`, the tool ensures the device can boot even if hardware-specific partitions (like Samsung's Prism) fail initial security checks.
3.  **APEX Flattening**: Modern Android systems use signed `.apex` containers. This tool extracts these modules into regular directories, allowing the system to boot without failing Google-specific signature verification.
4.  **Hardware Shimming**: The tool automatically maps target-device hardware blobs (like the linker and security HALs) into the Pixel system to ensure the software can communicate with the hardware.

---

## ⚠️ Disclaimer

Android porting is high-risk. This is an Alpha-stage automated tool. Always maintain a full backup and have restoration tools (Odin/Fastboot) ready. The developers are not responsible for any device damage.
