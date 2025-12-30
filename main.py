import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import datetime
import shutil
import json

class ActivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Activity App")
        self.root.geometry("700x450")
        self.root.configure(bg="#f4f6fa")
        self.activity = tk.StringVar(value="scan_videos")
        self.start_folder = tk.StringVar()
        self.log = []
        self.undo_stack = []
        self.seq = 1
        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background="#f4f6fa")
        style.configure('TLabel', background="#f4f6fa", font=("Segoe UI", 11))
        style.configure('TButton', font=("Segoe UI", 11, "bold"), padding=6)
        style.configure('TRadiobutton', background="#f4f6fa", font=("Segoe UI", 11))

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(folder_frame, text="Select Starting Folder:").pack(side=tk.LEFT, padx=(0, 10))
        folder_entry = ttk.Entry(folder_frame, textvariable=self.start_folder, width=40)
        folder_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)

        # Activity selection
        activity_frame = ttk.Frame(main_frame)
        activity_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(activity_frame, text="Select Activity:").pack(side=tk.LEFT, padx=(0, 10))
        activities = [
            ("Scan Videos", "scan_videos"),
            ("Scan Pictures", "scan_pictures"),
            ("Scan Images", "scan_images")
        ]
        for text, value in activities:
            ttk.Radiobutton(activity_frame, text=text, variable=self.activity, value=value).pack(side=tk.LEFT, padx=5)

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        self.run_btn = ttk.Button(button_frame, text="Run", command=self.run_activity)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.undo_btn = ttk.Button(button_frame, text="Undo", command=self.undo)
        self.undo_btn.pack(side=tk.LEFT)

        # Log area
        log_label = ttk.Label(main_frame, text="Activity Log:", font=("Segoe UI", 11, "bold"))
        log_label.pack(anchor=tk.W, pady=(10, 0))
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, height=12, width=80, state=tk.DISABLED, bg="#f9fafc", fg="#222", font=("Consolas", 10))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scroll.set)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.start_folder.set(folder)

    def run_activity(self):
        folder = self.start_folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid starting folder.")
            return
        activity = self.activity.get()
        self.run_btn.state(["disabled"])
        self.undo_btn.state(["disabled"])
        self.root.update_idletasks()
        if activity == "scan_videos":
            changes = self.scan_videos(folder)
        else:
            messagebox.showinfo("Info", f"Activity '{activity}' not implemented yet.")
            self.run_btn.state(["!disabled"])
            self.undo_btn.state(["!disabled"])
            return
        if changes:
            self.undo_stack.append(changes)
        self.seq += 1
        self.run_btn.state(["!disabled"])
        self.undo_btn.state(["!disabled"])

    def load_replacements(self):
        replacements_path = os.path.join(os.path.dirname(__file__), "replacements.json")
        with open(replacements_path, "r") as file:
            return json.load(file)

    def apply_replacements(self, name, replacements):
        for old, new in replacements.items():
            if old != ".":  # Avoid replacing the period before the extension
                name = name.replace(old, new)
        return name

    def scan_videos(self, folder):
        changes = []
        new_folder_path = folder

        # Load replacements from JSON file
        replacements = self.load_replacements()

        # Process files in the starting folder itself
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isfile(path):
                name, ext = os.path.splitext(f)
                new_name = self.apply_replacements(name, replacements) + ext
                if new_name != f:
                    new_path = os.path.join(folder, new_name)
                    os.rename(path, new_path)
                    self.log_action(f"Renamed file: {path} -> {new_path}")
                    changes.append(("file", new_path, path))

        # Recursively process all subfolders and their files
        for dirpath, dirnames, filenames in os.walk(folder):
            # Rename folders with periods (subfolders only)
            for i, d in enumerate(list(dirnames)):
                if "." in d:
                    old_path = os.path.join(dirpath, d)
                    new_name = self.apply_replacements(d, replacements)
                    new_path = os.path.join(dirpath, new_name)
                    os.rename(old_path, new_path)
                    self.log_action(f"Renamed folder: {old_path} -> {new_path}")
                    changes.append(("folder", new_path, old_path))
                    dirnames[i] = new_name  # Update dirnames for os.walk

            # Rename files in the current directory
            for f in filenames:
                name, ext = os.path.splitext(f)
                new_name = self.apply_replacements(name, replacements) + ext
                if new_name != f:
                    old_path = os.path.join(dirpath, f)
                    new_path = os.path.join(dirpath, new_name)
                    os.rename(old_path, new_path)
                    self.log_action(f"Renamed file: {old_path} -> {new_path}")
                    changes.append(("file", new_path, old_path))

        # If the starting folder itself has a period and is being renamed
        if "." in os.path.basename(folder):
            new_folder_path = os.path.join(os.path.dirname(folder), self.apply_replacements(os.path.basename(folder), replacements))
            os.rename(folder, new_folder_path)
            self.log_action(f"Renamed starting folder: {folder} -> {new_folder_path}")
            changes.append(("folder", new_folder_path, folder))

        return changes

    def log_action(self, msg):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{self.seq:04d} [{timestamp}] {msg}\n"
        self.log.append(entry)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, entry)
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def undo(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        self.run_btn.state(["disabled"])
        self.undo_btn.state(["disabled"])
        self.root.update_idletasks()
        changes = self.undo_stack.pop()
        for typ, src, dst in reversed(changes):
            try:
                os.rename(src, dst)
                self.log_action(f"Undo rename: {src} -> {dst}")
            except Exception as e:
                self.log_action(f"Undo failed: {src} -> {dst} ({e})")
        self.run_btn.state(["!disabled"])
        self.undo_btn.state(["!disabled"])

if __name__ == "__main__":
    root = tk.Tk()
    app = ActivityApp(root)
    root.mainloop()