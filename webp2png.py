import os
import threading
import time
from tkinter import Tk, Entry, Label, Button, Checkbutton, IntVar, Text, END, filedialog, messagebox
from PIL import Image

# after convert delete original file

running = False

def log(text_widget, message):
    text_widget.insert(END, message + "\n")
    text_widget.see(END)
    lines = text_widget.get("1.0", END).split("\n")
    if len(lines) > 6:
        text_widget.delete("1.0", "2.0")


def browse_folder(path_entry):
    folder = filedialog.askdirectory()
    if folder:
        path_entry.delete(0, END)
        path_entry.insert(0, folder)


def rename_files(path, ext_from, ext_to, text_widget):
    for filename in os.listdir(path):
        if not running:
            break
        if filename.lower().endswith(ext_from):
            old_path = os.path.join(path, filename)
            new_filename = filename[:-len(ext_from)] + ext_to
            new_path = os.path.join(path, new_filename)
            os.rename(old_path, new_path)
            log(text_widget, f"Renamed: {filename} -> {new_filename}")


def convert_files(path, ext_from, ext_to, text_widget):
    for filename in os.listdir(path):
        if not running:
            break
        if filename.lower().endswith(ext_from):
            new_filename = filename[:-len(ext_from)] + ext_to
            new_path = os.path.join(path, new_filename)
            # skip if converted file already exists
            if os.path.exists(new_path):
                continue
            old_path = os.path.join(path, filename)
            try:
                with Image.open(old_path) as img:
                    img.save(new_path, ext_to.replace('.', '').upper())
                log(text_widget, f"Converted: {filename} -> {new_filename}")
                os.remove(old_path)  # remove original to prevent infinite loop
            except Exception as e:
                log(text_widget, f"Error: {filename} ({e})")


def start_stop(path_entry, from_entry, to_entry, convert_var, text_widget, button):
    global running

    ext_from = from_entry.get().strip()
    ext_to = to_entry.get().strip()

    # validate input
    if not ext_from or not ext_from.startswith('.') or not ext_to or not ext_to.startswith('.'):
        messagebox.showerror("Error", "From and To fields must start with a '.' and cannot be empty.")
        return

    if not running:
        running = True
        button.config(text="Stop")

        path = path_entry.get()

        if convert_var.get():
            log(text_widget, f"Started: will convert {ext_from} -> {ext_to} in {path}")
        else:
            log(text_widget, f"Started: will rename {ext_from} -> {ext_to} in {path}")

        def task():
            global running
            while running:
                if convert_var.get():
                    convert_files(path, ext_from, ext_to, text_widget)
                else:
                    rename_files(path, ext_from, ext_to, text_widget)
                time.sleep(1)
            log(text_widget, "Stopped")
            button.config(text="Start")

        threading.Thread(target=task, daemon=True).start()
    else:
        running = False
        log(text_widget, "Stop requested")
        button.config(text="Start")


def create_gui():
    root = Tk()
    root.title("Image Tool")
    root.geometry("750x250")

    # set terminal-like font
    default_font = ("Courier New", 10)

    # grid config
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    root.rowconfigure(2, weight=1)

    default_path = os.getcwd()

    # PATH ROW
    Label(root, text="Path:", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)

    path_entry = Entry(root, font=default_font)
    path_entry.insert(0, default_path)
    path_entry.grid(row=0, column=0, sticky="we", padx=(50,3))

    browse_button = Button(root, text="⋮", command=lambda: browse_folder(path_entry), padx=0, pady=0)
    browse_button.grid(row=0, column=0, sticky="e", padx=(0,3), ipady=0)

    # START BUTTON
    start_button = Button(root, text="Start", width=10, font=default_font)
    start_button.grid(row=0, column=1, rowspan=2, sticky="ns", padx=5, pady=5)

    # SECOND ROW
    Label(root, text="From:", font=default_font).grid(row=1, column=0, sticky="w", padx=5)

    from_entry = Entry(root, width=8, font=default_font)
    from_entry.insert(0, ".webp")
    from_entry.grid(row=1, column=0, padx=(60,5), sticky="w")

    Label(root, text="To:", font=default_font).grid(row=1, column=0, padx=(140,5), sticky="w")

    to_entry = Entry(root, width=8, font=default_font)
    to_entry.insert(0, ".png")
    to_entry.grid(row=1, column=0, padx=(170,5), sticky="w")

    convert_var = IntVar()
    Checkbutton(root, text="Convert", variable=convert_var, font=default_font).grid(row=1, column=0, padx=(250,5), sticky="w")

    # TEXT OUTPUT
    text_widget = Text(root, height=5, font=("Courier New", 9))
    text_widget.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

    start_button.config(command=lambda: start_stop(path_entry, from_entry, to_entry, convert_var, text_widget, start_button))

    root.mainloop()


if __name__ == "__main__":
    create_gui()
