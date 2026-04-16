import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

folder_path = ""
output_folder = ""
file_list = []

# ---------- Core functions ----------
def select_input_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    input_label.config(text=f"Input Folder: {folder_path}")
    refresh_file_list()

def select_output_folder():
    global output_folder
    output_folder = filedialog.askdirectory()
    output_label.config(text=f"Output Folder: {output_folder}")

def refresh_file_list():
    global file_list
    file_list.clear()
    preview_box.delete(0, tk.END)
    if not folder_path:
        return
    for root, dirs, files in os.walk(folder_path) if subfolder_var.get() else [(folder_path, [], os.listdir(folder_path))]:
        for f in files:
            file_list.append(os.path.join(root, f))
    for f in file_list:
        preview_box.insert(tk.END, os.path.basename(f))

def get_new_name(filename, mode, idx):
    new_name = filename
    if mode == "regex_remove":
        pattern = regex_remove_entry.get()
        if pattern:
            try:
                new_name = re.sub(pattern, "", new_name)
            except re.error:
                messagebox.showerror("Error", "Invalid regex pattern.")
    elif mode == "regex_add":
        add_text = regex_add_text_entry.get()
        position = regex_add_position_var.get()
        if add_text:
            if position == "start":
                new_name = add_text + new_name
            elif position == "end":
                name, ext = os.path.splitext(new_name)
                new_name = name + add_text + ext
    elif mode == "replace":
        search_text = replace_search_entry.get()
        replace_text = replace_replace_entry.get()
        if search_text:
            new_name = new_name.replace(search_text, replace_text)
    elif mode == "number":
        ext = os.path.splitext(new_name)[1]
        new_name = f"{number_prefix_entry.get()}{idx+1}{ext}"
    return new_name

def get_unique_path(dest_path):
    """Ensure unique filename in output folder by appending (1), (2), etc."""
    base, ext = os.path.splitext(dest_path)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = f"{base}({counter}){ext}"
        counter += 1
    return dest_path

def preview_changes(mode):
    preview_box.delete(0, tk.END)
    if not file_list:
        messagebox.showwarning("Warning", "No files to rename.")
        return

    # Temporary output folder for preview
    temp_output_folder = output_folder
    if not temp_output_folder:
        temp_output_folder = os.path.join(folder_path, "Renamed_Files")
    
    for idx, file_path in enumerate(file_list):
        filename = os.path.basename(file_path)
        new_name = get_new_name(filename, mode, idx)
        dest_path = get_unique_path(os.path.join(temp_output_folder, new_name))
        preview_box.insert(tk.END, f"{filename} → {os.path.basename(dest_path)}")

def rename_files(mode):
    global output_folder
    if not file_list:
        messagebox.showwarning("Warning", "No files to rename.")
        return

    # Auto-create output folder if not specified
    if not output_folder:
        output_folder = os.path.join(folder_path, "Renamed_Files")
        os.makedirs(output_folder, exist_ok=True)
        output_label.config(text=f"Output Folder: {output_folder}")

    count = 0
    for idx, file_path in enumerate(file_list):
        filename = os.path.basename(file_path)
        new_name = get_new_name(filename, mode, idx)
        dest_path = get_unique_path(os.path.join(output_folder, new_name))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(file_path, dest_path)
        count += 1

    messagebox.showinfo("Done", f"{count} files copied to output folder.")

# ---------- GUI ----------
root = tk.Tk()
root.title("Safe Batch Renamer with Full Copy and Unique Names")
root.geometry("780x700")

tk.Label(root, text="Safe Tabbed Batch Renamer (Copies all files)", font=("Arial", 16)).pack(pady=10)

input_btn = tk.Button(root, text="Select Input Folder", command=select_input_folder)
input_btn.pack()
input_label = tk.Label(root, text="No input folder selected")
input_label.pack(pady=2)

output_btn = tk.Button(root, text="Select Output Folder (optional)", command=select_output_folder)
output_btn.pack()
output_label = tk.Label(root, text="No output folder selected")
output_label.pack(pady=2)

subfolder_var = tk.BooleanVar()
tk.Checkbutton(root, text="Include Subfolders", variable=subfolder_var, command=refresh_file_list).pack()

tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill="both")

# ---------- Regex Remove Tab ----------
regex_remove_tab = ttk.Frame(tab_control)
tab_control.add(regex_remove_tab, text="Regex Remove")
tk.Label(regex_remove_tab, text="Regex Pattern to REMOVE:").pack()
regex_remove_entry = tk.Entry(regex_remove_tab, width=40)
regex_remove_entry.pack(pady=2)
tk.Button(regex_remove_tab, text="Preview", command=lambda: preview_changes("regex_remove")).pack(pady=5)
tk.Button(regex_remove_tab, text="Rename / Copy Files", command=lambda: rename_files("regex_remove")).pack(pady=5)

# ---------- Regex Add Tab ----------
regex_add_tab = ttk.Frame(tab_control)
tab_control.add(regex_add_tab, text="Regex Add")
tk.Label(regex_add_tab, text="Text to Add:").pack()
regex_add_text_entry = tk.Entry(regex_add_tab, width=40)
regex_add_text_entry.pack(pady=2)
regex_add_position_var = tk.StringVar(value="start")
tk.Radiobutton(regex_add_tab, text="Start of filename", variable=regex_add_position_var, value="start").pack()
tk.Radiobutton(regex_add_tab, text="End of filename", variable=regex_add_position_var, value="end").pack()
tk.Button(regex_add_tab, text="Preview", command=lambda: preview_changes("regex_add")).pack(pady=5)
tk.Button(regex_add_tab, text="Rename / Copy Files", command=lambda: rename_files("regex_add")).pack(pady=5)

# ---------- Replace Tab ----------
replace_tab = ttk.Frame(tab_control)
tab_control.add(replace_tab, text="Replace Mode")
tk.Label(replace_tab, text="Text to find:").pack()
replace_search_entry = tk.Entry(replace_tab, width=40)
replace_search_entry.pack(pady=2)
tk.Label(replace_tab, text="Replace with:").pack()
replace_replace_entry = tk.Entry(replace_tab, width=40)
replace_replace_entry.pack(pady=2)
tk.Button(replace_tab, text="Preview", command=lambda: preview_changes("replace")).pack(pady=5)
tk.Button(replace_tab, text="Rename / Copy Files", command=lambda: rename_files("replace")).pack(pady=5)

# ---------- Auto Numbering Tab ----------
number_tab = ttk.Frame(tab_control)
tab_control.add(number_tab, text="Auto Numbering")
tk.Label(number_tab, text="Numbering Prefix:").pack()
number_prefix_entry = tk.Entry(number_tab, width=20)
number_prefix_entry.insert(0, "File_")
number_prefix_entry.pack(pady=2)
tk.Button(number_tab, text="Preview", command=lambda: preview_changes("number")).pack(pady=5)
tk.Button(number_tab, text="Rename / Copy Files", command=lambda: rename_files("number")).pack(pady=5)

# ---------- Preview Box ----------
preview_box = tk.Listbox(root, width=100, height=25)
preview_box.pack(pady=10)

root.mainloop()
 
