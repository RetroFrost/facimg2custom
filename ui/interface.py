import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import threading
from utils.helpers import find_unified_models, check_dependencies
from core.extractor import Extractor
from core.patcher import Patcher
from core.packager import Packager

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("facimg2custom - Pixel to Custom ROM Converter")
        self.root.geometry("700x650")

        self.pixel_img_path = tk.StringVar()
        self.device_tree_path = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.flash_text = tk.StringVar(value="Installing Ported Pixel ROM...")
        self.update_binary_type = tk.StringVar(value="dummy")
        self.post_flash_files = []

        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Section 1: Files
        ttk.Label(main_frame, text="1. Select Files", font=('', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=10)

        ttk.Label(main_frame, text="Pixel Factory Image (.zip):").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.pixel_img_path, width=60).grid(row=2, column=0, sticky=tk.W)
        ttk.Button(main_frame, text="Browse", command=self._browse_pixel_img).grid(row=2, column=1, padx=5)

        ttk.Label(main_frame, text="Device Tree Folder:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Entry(main_frame, textvariable=self.device_tree_path, width=60).grid(row=4, column=0, sticky=tk.W)
        ttk.Button(main_frame, text="Browse", command=self._browse_device_tree).grid(row=4, column=1, padx=5)

        self.model_label = ttk.Label(main_frame, text="Target Model (Unified Tree):")
        self.model_combo = ttk.Combobox(main_frame, textvariable=self.selected_model, state="readonly", width=57)

        # Section 2: Customization
        ttk.Label(main_frame, text="2. Customization", font=('', 12, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=10)

        ttk.Label(main_frame, text="Flash Text (Obligatory):").grid(row=8, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.flash_text, width=60).grid(row=9, column=0, sticky=tk.W)

        ttk.Label(main_frame, text="Post-Flash Files:").grid(row=10, column=0, sticky=tk.W, pady=(10, 0))
        self.post_flash_listbox = tk.Listbox(main_frame, height=3, width=60)
        self.post_flash_listbox.grid(row=11, column=0, sticky=tk.W)
        ttk.Button(main_frame, text="Add Files", command=self._add_post_flash_files).grid(row=11, column=1, padx=5, sticky=tk.N)

        ttk.Label(main_frame, text="Update Binary:").grid(row=12, column=0, sticky=tk.W, pady=(10, 0))
        binary_frame = ttk.Frame(main_frame)
        binary_frame.grid(row=13, column=0, sticky=tk.W)
        ttk.Radiobutton(binary_frame, text="Dummy (Shell)", variable=self.update_binary_type, value="dummy").pack(side=tk.LEFT)
        ttk.Radiobutton(binary_frame, text="Compiled", variable=self.update_binary_type, value="compiled").pack(side=tk.LEFT, padx=20)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=14, column=0, columnspan=2, sticky=tk.EW, pady=20)

        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=15, column=0, columnspan=2)

        # Run Button
        self.start_btn = ttk.Button(main_frame, text="START CONVERSION", command=self._run_process)
        self.start_btn.grid(row=16, column=0, columnspan=2, pady=10)

    def _browse_pixel_img(self):
        filename = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
        if filename: self.pixel_img_path.set(filename)

    def _browse_device_tree(self):
        directory = filedialog.askdirectory()
        if directory:
            self.device_tree_path.set(directory)
            models = find_unified_models(directory)
            if models:
                self.model_label.grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
                self.model_combo.grid(row=6, column=0, sticky=tk.W)
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
        self.status_label.config(text=text)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()

    def _run_process(self):
        if not self.pixel_img_path.get() or not self.device_tree_path.get():
            messagebox.showerror("Error", "Missing paths!")
            return

        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._conversion_thread, daemon=True).start()

    def _conversion_thread(self):
        try:
            self._update_status("Checking dependencies...", 5)
            check_dependencies()

            work_dir = "work"
            if os.path.exists(work_dir): shutil.rmtree(work_dir)
            os.makedirs(work_dir)

            # Step 1: Extract
            self._update_status("Extracting Pixel Image...", 10)
            ext = Extractor(self.pixel_img_path.get(), work_dir)
            nested_zip = ext.extract_main_zip()
            self._update_status("Extracting partitions...", 30)
            img_dir = ext.extract_nested_zip()
            ext.convert_sparse_images(img_dir)

            # Step 2: Patch
            self._update_status("Applying smart patches...", 60)
            patcher = Patcher(img_dir, self.device_tree_path.get(), self.selected_model.get())
            working_dir = patcher.apply_smart_patches()
            patcher.generate_updater_script(self.flash_text.get(), self.update_binary_type.get())

            # Step 3: Package
            self._update_status("Packaging final ZIP...", 90)
            pkg = Packager(working_dir, self.post_flash_files)
            final_zip = os.path.join(os.getcwd(), "pixel_port.zip")
            pkg.create_zip(final_zip)

            self._update_status("Done!", 100)
            messagebox.showinfo("Success", f"Conversion complete!\nOutput: {final_zip}")
        except Exception as e:
            self._update_status(f"Error: {str(e)}", 0)
            messagebox.showerror("Process Error", str(e))
        finally:
            self.start_btn.config(state=tk.NORMAL)

    def run(self):
        self.root.mainloop()
