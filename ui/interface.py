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
        self.root.title("facimg2custom - Rufus for Pixel Ports")
        self.root.geometry("500x750")
        self.root.resizable(False, False)

        self.pixel_img_path = tk.StringVar()
        self.samsung_ap_path = tk.StringVar()
        self.device_tree_path = tk.StringVar()
        self.output_zip_path = tk.StringVar(value=os.path.join(os.getcwd(), "pixel_port.zip"))
        self.selected_model = tk.StringVar()
        self.flash_text = tk.StringVar(value="Installing Ported Pixel ROM...")
        self.update_binary_type = tk.StringVar(value="dummy")
        self.use_blank_vbmeta = tk.BooleanVar(value=True)
        self.advanced_fixes = tk.BooleanVar(value=True)
        self.skip_setup = tk.BooleanVar(value=False) # Default to False (functional setup)
        self.post_flash_files = []

        self.msg_queue = queue.Queue()
        self._setup_ui()
        self._check_queue()

    def _setup_ui(self):
        style = ttk.Style()
        style.configure("Big.TButton", font=('', 12, 'bold'), padding=10)

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Pixel Factory Image:", font=('', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        f1 = ttk.Frame(main_frame)
        f1.pack(fill=tk.X)
        ttk.Entry(f1, textvariable=self.pixel_img_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(f1, text="SELECT", command=self._browse_pixel_img).pack(side=tk.RIGHT)

        ttk.Label(main_frame, text="Base Device Firmware (Samsung AP):", font=('', 9, 'bold')).pack(anchor=tk.W, pady=(15,0))
        f2 = ttk.Frame(main_frame)
        f2.pack(fill=tk.X)
        ttk.Entry(f2, textvariable=self.samsung_ap_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(f2, text="SELECT", command=self._browse_samsung_ap).pack(side=tk.RIGHT)

        ttk.Label(main_frame, text="Device Tree (Optional):", font=('', 9, 'bold')).pack(anchor=tk.W, pady=(15,0))
        f3 = ttk.Frame(main_frame)
        f3.pack(fill=tk.X)
        ttk.Entry(f3, textvariable=self.device_tree_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(f3, text="SELECT", command=self._browse_device_tree).pack(side=tk.RIGHT)
        self.model_label = ttk.Label(main_frame, text="Target Model (Unified Tree):")
        self.model_combo = ttk.Combobox(main_frame, textvariable=self.selected_model, state="readonly")

        ttk.Label(main_frame, text="Save Generated ROM to:", font=('', 9, 'bold')).pack(anchor=tk.W, pady=(15,0))
        f4 = ttk.Frame(main_frame)
        f4.pack(fill=tk.X)
        ttk.Entry(f4, textvariable=self.output_zip_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(f4, text="SAVE AS", command=self._browse_output_zip).pack(side=tk.RIGHT)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        ttk.Label(main_frame, text="Format Options:", font=('', 9, 'bold')).pack(anchor=tk.W)

        ttk.Checkbutton(main_frame, text="Use Blank VBMeta (Disabler)", variable=self.use_blank_vbmeta).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(main_frame, text="Apply Advanced Industry Fixes", variable=self.advanced_fixes).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(main_frame, text="Troubleshoot: Skip Setup Wizard (if crashing)", variable=self.skip_setup).pack(anchor=tk.W, pady=2)

        ttk.Label(main_frame, text="Recovery Installation Text:").pack(anchor=tk.W, pady=(10,0))
        ttk.Entry(main_frame, textvariable=self.flash_text).pack(fill=tk.X, pady=(0,10))

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0,5))
        f5 = ttk.Frame(bottom_frame)
        f5.pack(fill=tk.X)
        self.status_label = ttk.Label(f5, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        self.percent_label = ttk.Label(f5, text="0%")
        self.percent_label.pack(side=tk.RIGHT)
        self.start_btn = ttk.Button(bottom_frame, text="START CONVERSION", style="Big.TButton", command=self._run_process)
        self.start_btn.pack(fill=tk.X, pady=10)

    def _browse_pixel_img(self):
        filename = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
        if filename: self.pixel_img_path.set(filename)

    def _browse_samsung_ap(self):
        filename = filedialog.askopenfilename(filetypes=[("Samsung AP", "*.tar *.tar.md5"), ("All files", "*.*")])
        if filename: self.samsung_ap_path.set(filename)

    def _browse_output_zip(self):
        filename = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")])
        if filename: self.output_zip_path.set(filename)

    def _browse_device_tree(self):
        directory = filedialog.askdirectory()
        if directory:
            self.device_tree_path.set(directory)
            models = find_unified_models(directory)
            if models:
                self.model_label.pack(anchor=tk.W, pady=(5,0))
                self.model_combo.pack(fill=tk.X)
                self.model_combo['values'] = models
                self.selected_model.set(models[0])

    def _update_status(self, text, progress=None):
        self.msg_queue.put(("status", (text, progress)))

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
            if not downloader.check_dependencies(): raise Exception("Dependency check failed.")
            work_dir = "work"
            if os.path.exists(work_dir): shutil.rmtree(work_dir, ignore_errors=True)
            os.makedirs(work_dir, exist_ok=True)
            self._update_status("Extracting Pixel Image...", 10)
            ext = Extractor(self.pixel_img_path.get(), work_dir)
            ext.extract_main_zip()
            self._update_status("Extracting partitions...", 30)
            img_dir = ext.extract_nested_zip()
            ext.convert_sparse_images(img_dir)
            base_dir = None
            if self.samsung_ap_path.get():
                self._update_status("Extracting Samsung Base...", 50)
                base_dir = ext.extract_samsung_ap(self.samsung_ap_path.get())
            self._update_status("Applying actual porting fixes...", 75)
            patcher = Patcher(img_dir, self.device_tree_path.get() if self.device_tree_path.get() else None, self.selected_model.get(), base_img_dir=base_dir)
            working_dir = patcher.apply_smart_patches(use_blank_vbmeta=self.use_blank_vbmeta.get(), advanced_fixes=self.advanced_fixes.get(), skip_setup=self.skip_setup.get())
            patcher.generate_updater_script(self.flash_text.get(), self.update_binary_type.get())
            self._update_status("Packaging final ZIP...", 90)
            pkg = Packager(working_dir, self.post_flash_files)
            final_zip = self.output_zip_path.get()
            pkg.create_zip(final_zip)
            self._update_status("Done!", 100)
            self.msg_queue.put(("done", final_zip))
        except Exception as e:
            self._update_status(f"Error: {str(e)}", 0)
            self.msg_queue.put(("error", str(e)))

    def run(self):
        self.root.mainloop()
