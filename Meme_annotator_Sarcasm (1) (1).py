import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# CONFIG
image_folder = r"E:\MEME research of Subbir\meme sent by sabbir\Memes"
excel_path = r"E:\MEME research of Subbir\meme sent by sabbir\Memes\Meme_annotations_Binar.xlsx"
target_column = "Sarcasm_Present"

# Load Excel
df = pd.read_excel(excel_path)

# Ensure column exists
if target_column not in df.columns:
    df[target_column] = None

# Sort numerically by image filename
df = df.sort_values(
    by="Image_Name",
    key=lambda x: x.astype(str).str.extract(r"(\d+)")[0].astype(float)
).reset_index(drop=True)

# Identify unannotated rows
rows_to_annotate = df[df[target_column].isna()].index.tolist()
if not rows_to_annotate:
    print(f"🎉 All '{target_column}' annotations are already completed!")
    exit()

current_index = 0
POSSIBLE_VALUES = [0, 1]  # allowed values (cycles with left/right)

# GUI
root = tk.Tk()
root.title(f"{target_column} Annotation Tool")
root.geometry("900x650")
root.configure(bg="#1e1e1e")

image_label = tk.Label(root, bg="#1e1e1e")
image_label.pack(pady=20)

filename_label = tk.Label(root, text="", fg="white", bg="#1e1e1e", font=("Arial", 14, "bold"))
filename_label.pack(pady=5)

# IntVar holds selection; -1 means nothing selected yet
value_var = tk.IntVar(value=-1)

# Single-field frame — highlight box (style D: thin blue border)
frame = tk.Frame(root, bg="#1e1e1e",
                 highlightthickness=2,
                 highlightbackground="#3b82f6",
                 highlightcolor="#3b82f6")
frame.pack(pady=10)

def load_image():
    """Load current image and reset selection."""
    global current_index
    idx = rows_to_annotate[current_index]
    img_name = df.at[idx, "Image_Name"]
    img_path = os.path.join(image_folder, img_name)

    if not os.path.exists(img_path):
        messagebox.showerror("Image Missing", img_name)
        return

    img = Image.open(img_path)
    img.thumbnail((800, 500))
    tk_img = ImageTk.PhotoImage(img)

    image_label.configure(image=tk_img)
    image_label.image = tk_img
    filename_label.configure(text=f"{current_index+1}/{len(rows_to_annotate)} — {img_name}")

    # Reset selection (unannotated rows should be NaN, but we reset anyway)
    value_var.set(-1)
    update_value_display()

def save_and_next(event=None):
    """Save current selection to excel and move to next image."""
    global current_index
    val = value_var.get()

    if val == -1:
        messagebox.showwarning("Missing", "Please choose 0 or 1 (use ← / → keys or click).")
        return

    idx = rows_to_annotate[current_index]
    df.at[idx, target_column] = int(val)  # store as int
    df.to_excel(excel_path, index=False)

    current_index += 1
    if current_index >= len(rows_to_annotate):
        messagebox.showinfo("Done", f"🎉 All '{target_column}' annotations completed!")
        root.destroy()
        return

    load_image()

# UI inside frame
tk.Label(frame, text=target_column, fg="white", bg="#1e1e1e", font=("Arial", 12)).pack(pady=(8,4))

buttons_row = tk.Frame(frame, bg="#1e1e1e")
buttons_row.pack(pady=(0,8))

# Radiobuttons (still clickable with mouse)
for v in POSSIBLE_VALUES:
    tk.Radiobutton(
        buttons_row,
        text=str(v),
        variable=value_var,
        value=v,
        indicatoron=False,
        width=6,
        font=("Arial", 12),
        bg="#333",
        fg="white",
        selectcolor="#3b82f6",
        relief="ridge"
    ).pack(side="left", padx=6)

# Visual label to show current value (updates on key or click)
value_display = tk.Label(frame, text="Value: -", fg="white", bg="#1e1e1e", font=("Arial", 12))
value_display.pack(pady=(4,8))

def update_value_display():
    v = value_var.get()
    value_display.config(text=f"Value: {v if v != -1 else '-'}")

# Key handlers: Left/Right to change, Enter to save
def change_value(direction):
    """direction: -1 for left, +1 for right"""
    cur = value_var.get()
    if cur == -1:
        # If nothing set: set to first on Right, last on Left
        new = POSSIBLE_VALUES[0] if direction > 0 else POSSIBLE_VALUES[-1]
    else:
        idx = POSSIBLE_VALUES.index(cur)
        new = POSSIBLE_VALUES[(idx + direction) % len(POSSIBLE_VALUES)]
    value_var.set(new)
    update_value_display()

def on_key(event):
    key = event.keysym
    if key == "Left":
        change_value(-1)
    elif key == "Right":
        change_value(1)
    elif key == "Return":
        save_and_next()

# Also update display when user clicks a radiobutton (trace)
def on_var_change(*args):
    update_value_display()

value_var.trace_add("write", on_var_change)

root.bind("<Key>", on_key)

# Save button (mouse-friendly)
tk.Button(
    root, text="Save & Next ➡️",
    command=save_and_next,
    font=("Arial", 14),
    bg="#3b82f6",
    fg="white",
    width=18, height=2
).pack(pady=20)

# Initial load
load_image()
root.mainloop()