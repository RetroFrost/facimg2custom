import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import threading
import queue
from utils.helpers import find_unified_models, get_bin_path
from core.extractor import Extractor
from core.patcher import Patcher
from core.packager import Packager
from core.downloader import Downloader

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("facimg2custom - Pixel to Custom ROM Converter")
        self.root.geometry("700x850")

        self.pixel_img_path = tk.StringVar()
        self.samsung_ap_path = tk.StringVar()
        self.device_tree_path = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.flash_text = tk.StringVar(value="Installing Ported Pixel ROM...")
        self.update_binary_type = tk.StringVar(value="dummy")
        self.use_blank_vbmeta = tk.BooleanVar(value=True)
        self.post_flash_files = []

        self.msg_queue = queue.Queue()
        self._setup_ui()
        self._check_queue()

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Section 1: Files
        ttk.Label(main_frame, text="1. Select Files", font=('', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=10)

        # Pixel Factory Image
        ttk.Label(main_frame, text="Pixel Factory Image (.zip):").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.pixel_img_path, width=60).grid(row=2, column=0, sticky=tk.W)
        ttk.Button(main_frame, text="Browse", command=self._browse_pixel_img).grid(row=2, column=1, padx=5)

        # Samsung AP File
        ttk.Label(main_frame, text="Samsung AP (.tar/.tar.md5):").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Entry(main_frame, textvariable=self.samsung_ap_path, width=60).grid(row=4, column=0, sticky=tk.W)
        ttk.Button(main_frame, text="Browse", command=self._browse_samsung_ap).grid(row=4, column=1, padx=5)

        # Device Tree Folder
        ttk.Label(main_frame, text="Device Tree Folder (Optional):").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Entry(main_frame, textvariable=self.device_tree_path, width=60).grid(row=6, column=0, sticky=tk.W)
        ttk.Button(main_frame, text="Browse", command=self._browse_device_tree).grid(row=6, column=1, padx=5)

        self.model_label = ttk.Label(main_frame, text="Target Model (Unified Tree):")
        self.model_combo = ttk.Combobox(main_frame, textvariable=self.selected_model, state="readonly", width=57)

        # Section 2: Customization
        ttk.Label(main_frame, text="2. Customization", font=('', 12, 'bold')).grid(row=9, column=0, sticky=tk.W, pady=10)

        ttk.Label(main_frame, text="Flash Text (Obligatory):").grid(row=10, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.flash_text, width=60).grid(row=11, column=0, sticky=tk.W)

        ttk.Checkbutton(main_frame, text="Use Blank/Disabler VBMeta (Recommended for Samsung)", variable=self.use_blank_vbmeta).grid(row=12, column=0, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="Post-Flash Files:").grid(row=13, column=0, sticky=tk.W, pady=(5, 0))
        self.post_flash_listbox = tk.Listbox(main_frame, height=3, width=60)
        self.post_flash_listbox.grid(row=14, column=0, sticky=tk.W)
        ttk.Button(main_frame, text="Add Files", command=self._add_post_flash_files).grid(row=14, column=1, padx=5, sticky=tk.N)

        ttk.Label(main_frame, text="Update Binary:").grid(row=15, column=0, sticky=tk.W, pady=(10, 0))
        binary_frame = ttk.Frame(main_frame)
        binary_frame.grid(row=16, column=0, sticky=tk.W)
        ttk.Radiobutton(binary_frame, text="Dummy (Shell)", variable=self.update_binary_type, value="dummy").pack(side=tk.LEFT)
        ttk.Radiobutton(binary_frame, text="Compiled", variable=self.update_binary_type, value="compiled").pack(side=tk.LEFT, padx=20)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=17, column=0, columnspan=2, sticky=tk.EW, pady=20)

        self.percent_label = ttk.Label(main_frame, text="0%")
        self.percent_label.grid(row=18, column=1, sticky=tk.E, pady=(0, 10))

        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=18, column=0, sticky=tk.W)

        # Run Button
        self.start_btn = ttk.Button(main_frame, text="START CONVERSION", command=self._run_process)
        self.start_btn.grid(row=19, column=0, columnspan=2, pady=10)

    def _browse_pixel_img(self):
        filename = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
        if filename: self.pixel_img_path.set(filename)

    def _browse_samsung_ap(self):
        filename = filedialog.askopenfilename(filetypes=[("Samsung AP", "*.tar *.tar.md5"), ("Tar files", "*.tar"), ("MD5 files", "*.tar.md5"), ("All files", "*.*")])
        if filename: self.samsung_ap_path.set(filename)

    def _browse_device_tree(self):
        directory = filedialog.askdirectory()
        if directory:
            self.device_tree_path.set(directory)
            models = find_unified_models(directory)
            if models:
                self.model_label.grid(row=7, column=0, sticky=tk.W, pady=(10, 0))
                self.model_combo.grid(row=8, column=0, sticky=tk.W)
                self.model_combo['values'] = models
                self.selected_model.set(models[0])
            else:
                self.model_label.grid_forget()
                self.model_combo.grid_forget()
                self.selected_model.set("")

    def _add_post_flash_files(self):
        files = filedialog.askopenfilenames()
        if files:
            for f in files:
                if f not in self.post_flash_files:
                    self.post_flash_files.append(f)
                    self.post_flash_listbox.insert(tk.END, os.path.basename(f))

    def _update_status(self, text, progress=None):
        self.msg_queue.put(("status", (text, progress)))
        print(f"[UI Log] {text} ({int(progress) if progress is not None else ''}%)")

    def _check_queue(self):
        while True:
            try:
                msg_type, data = self.msg_queue.get_nowait()
                if msg_type == "status":
                    text, progress = data
                    self.status_label.config(text=text)
                    if progress is not None:
                        self.progress_var.set(progress)
                        self.percent_label.config(text=f"{int(progress)}%")
                elif msg_type == "done":
                    messagebox.showinfo("Success", f"Conversion complete!\nOutput: {data}")
                    self.start_btn.config(state=tk.NORMAL)
                elif msg_type == "error":
                    messagebox.showerror("Process Error", str(data))
                    self.start_btn.config(state=tk.NORMAL)
            except queue.Empty:
                break
        self.root.after(100, self._check_queue)

    def _run_process(self):
        if not self.pixel_img_path.get() or (not self.device_tree_path.get() and not self.samsung_ap_path.get()):
            messagebox.showerror("Error", "Missing required paths!")
            return

        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._conversion_thread, daemon=True).start()

    def _conversion_thread(self):
        try:
            self._update_status("Checking dependencies...", 5)
            downloader = Downloader(get_bin_path())
            if not downloader.check_dependencies():
                raise Exception("Dependency check failed.")

            work_dir = "work"
            if os.path.exists(work_dir): shutil.rmtree(work_dir, ignore_errors=True)
            os.makedirs(work_dir, exist_ok=True)

            # Step 1: Extract Pixel
            self._update_status("Extracting Pixel Image...", 10)
            ext = Extractor(self.pixel_img_path.get(), work_dir)
            ext.extract_main_zip()
            self._update_status("Extracting partitions...", 30)
            img_dir = ext.extract_nested_zip()
            ext.convert_sparse_images(img_dir)

            # Step 1.1: Extract Samsung Base
            base_dir = None
            if self.samsung_ap_path.get():
                self._update_status("Extracting Samsung Base...", 50)
                base_dir = ext.extract_samsung_ap(self.samsung_ap_path.get())

            # Step 2: Patch
            self._update_status("Applying smart patches...", 75)
            patcher = Patcher(
                img_dir,
                self.device_tree_path.get() if self.device_tree_path.get() else None,
                self.selected_model.get(),
                base_img_dir=base_dir
            )
            working_dir = patcher.apply_smart_patches(use_blank_vbmeta=self.use_blank_vbmeta.get())
            patcher.generate_updater_script(self.flash_text.get(), self.update_binary_type.get())

            # Step 3: Package
            self._update_status("Packaging final ZIP...", 90)
            pkg = Packager(working_dir, self.post_flash_files)
            final_zip = os.path.join(os.getcwd(), "pixel_port.zip")
            if os.path.exists(final_zip): os.remove(final_zip)
            pkg.create_zip(final_zip)

            self._update_status("Done!", 100)
            self.msg_queue.put(("done", final_zip))
        except Exception as e:
            self._update_status(f"Error: {str(e)}", 0)
            self.msg_queue.put(("error", str(e)))

    def run(self):
        self.root.mainloop()
