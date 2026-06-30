# facimg2custom: Rufus for Pixel Ports 📱🛠️

**facimg2custom** is a professional-grade, automated Android porting engine designed to bring the latest Google Pixel factory images to Samsung Galaxy devices. It serves as a "one-click" bridge between the software "brain" of a Pixel and the hardware "skeleton" of a Galaxy, handling the deep system surgery required to make modern Android boot on legacy hardware.

Whether you are porting **Android 17** to a legendary **Samsung Galaxy S10+** or updating a modern S24, `facimg2custom` automates the technical hurdles that previously required hours of manual hex-editing and file manipulation.

---

## 🌟 The "Rufus" Experience for ROMs

Just like Rufus simplified bootable USB creation, `facimg2custom` simplifies Android porting:
- **Interactive GUI**: A thread-safe Windows interface with real-time progress tracking.
- **Automated Dependency Management**: Self-updating binary core and automated python environment setup.
- **Industry-Grade Defaults**: Sensible defaults that protect your device (Bootloader/Radio protection) while applying "Advanced Industry Fixes" automatically.

---

## 🏗️ Technical Architecture: The Hybrid Pipeline

Traditional porting often involves simple partition swapping, which fails on modern Android due to Linker Namespace and VINTF mismatches. `facimg2custom` uses a **Hybrid Patching Pipeline**:

### 1. APEX Flattening (The Signature Solution)
Modern Android uses `.apex` modules—signed, mounted containers for core libraries. Non-Google bootloaders often fail to verify these signatures. Our engine **flattens** these containers into standard directories, stripping signature requirements while maintaining library integrity.

### 2. Linker Shimming (Hardware-Software Mapping)
Pixel software expects Tensor-specific hardware responses. Samsung devices (especially Exynos variants) speak a different language. The tool automatically injects **Linker Shims** to map Pixel system calls to Samsung hardware drivers, resolving the "Linker Namespace" conflicts that cause early bootloops.

### 3. Ramdisk Surgery (Security Neutralization)
Using an integrated `magiskboot` core, the tool performs:
- **FSTAB Patching**: Strips AVB, dm-verity, and force-encrypt flags from `fstab`.
- **Vaultkeeper & SCED Neutralization**: Disables Samsung-proprietary security services that prevent non-OneUI systems from booting.
- **Service Redirection**: Maps hardware-specific services to their AOSP counterparts.

---

## 🗃️ Metadata Tracker: Unix Integrity on Windows

One of the biggest challenges of porting on Windows is the lack of support for Unix symlinks and file permissions (uid/gid).
- `facimg2custom` implements a custom **Metadata Tracker** (`core/metadata.py`).
- During extraction, it records every file's original Unix attributes.
- It generates a `fix_attrs.sh` recovery script that runs during the flash process to restore 100% of the system's structural integrity.

---

## 🚀 How to Port to your S10+ (Example)

1.  **Launch**: Run `launcher.py`.
2.  **Select Pixel Source**: Point to your Android 17 (or latest) Pixel Factory Image `.zip`.
3.  **Select Base**: Point to your Samsung `AP_*.tar.md5` or a folder of extracted images.
4.  **Enable Advanced Industry Fixes**: Ensure the "Hybrid Pipeline" is active for S10+ support.
5.  **Click Start**: The tool will extract, patch, shim, and package your flashable ROM.

---

## 🛠️ Requirements & Compatibility

- **OS**: Windows 10/11 (Optimized).
- **Python**: 3.12+ (Installed automatically via launcher if missing).
- **Devices**:
    - **Source**: Any Google Pixel Factory Image (Tensor or Snapdragon eras).
    - **Target**: Samsung Galaxy S-Series (S10 through S24), A-Series, and Note-Series (Exynos/Snapdragon).

---

## ⚠️ Disclaimer

Android porting is high-risk. This tool is in Alpha. While it includes safety checks to prevent hard-bricks by protecting critical partitions, you use it at your own risk. Always have an Odin-flashable stock firmware ready.
