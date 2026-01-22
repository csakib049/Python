import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# CONFIG
image_folder = r"E:\MEME research of Subbir\meme sent by sabbir\Memes"
excel_path = r"E:\MEME research of Subbir\meme sent by sabbir\Memes\Meme_annotations_Binar.xlsx"
target_column = "Humiliation"

df = pd.read_excel(excel_path)

if target_column not in df.columns:
    df[target_column] = None

df = df.sort_values(
    by="Image_Name",
    key=lambda x: x.astype(str).str.extract(r"(\d+)")[0].astype(float)
).reset_index(drop=True)

rows_to_annotate = df[df[target_column].isna()].index.tolist()
if not rows_to_annotate:
    print(f"🎉 All '{target_column}' annotations are done!")
    exit()

current_index = 0

# GUI SETUP
root = tk.Tk()
root.title(f"{target_column} Annotation")
root.geometry("900x650")
root.configure(bg="#1e1e1e")

image_label = tk.Label(root, bg="#1e1e1e")
image_label.pack(pady=20)

filename_label = tk.Label(root, text="", fg="white",
                          bg="#1e1e1e", font=("Arial", 14, "bold"))
filename_label.pack(pady=5)

value_var = tk.IntVar(value=-1)

# BUTTON FRAME
frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(pady=10)

tk.Label(frame, text=target_column, fg="white",
         bg="#1e1e1e", font=("Arial", 13)).pack(side="left", padx=10)

# --- Highlight Buttons Storage ---
buttons = {}

# Highlight handling
def update_highlight():
    selected = value_var.get()
    for val, btn in buttons.items():
        if val == selected:
            btn.config(bg="#3b82f6", fg="white")
        else:
            btn.config(bg="#2d2d2d", fg="white")

def set_value(v):
    value_var.set(v)
    update_highlight()

# Create custom highlight buttons
for v in [0, 1]:
    btn = tk.Label(
        frame,
        text=str(v),
        width=4,
        font=("Arial", 14),
        bg="#2d2d2d",
        fg="white",
        padx=10, pady=5
    )
    btn.pack(side="left", padx=8)
    btn.bind("<Button-1>", lambda e, val=v: set_value(val))
    buttons[v] = btn


def load():
    idx = rows_to_annotate[current_index]
    name = df.at[idx, "Image_Name"]
    path = os.path.join(image_folder, name)

    img = Image.open(path)
    img.thumbnail((800, 500))
    tk_img = ImageTk.PhotoImage(img)

    image_label.configure(image=tk_img)
    image_label.image = tk_img
    filename_label.configure(text=name)

    value_var.set(-1)
    update_highlight()


def save_next():
    global current_index
    val = value_var.get()

    if val == -1:
        messagebox.showwarning("Missing", "Choose 0 or 1")
        return

    idx = rows_to_annotate[current_index]
    df.at[idx, target_column] = val
    df.to_excel(excel_path, index=False)

    current_index += 1

    if current_index >= len(rows_to_annotate):
        messagebox.showinfo("Done", f"{target_column} Annotation Finished!")
        root.destroy()
        return

    load()

# Keyboard Behavior
def on_key(event):
    key = event.keysym
    curr = value_var.get()

    if key == "Return":
        save_next()

    elif key == "Right":
        new = 0 if curr == -1 else (curr + 1) % 2
        set_value(new)

    elif key == "Left":
        new = 1 if curr == -1 else (curr - 1) % 2
        set_value(new)

root.bind("<Key>", on_key)

# Save Button
tk.Button(
    root, text="Save & Next ➡️",
    command=save_next,
    width=18, height=2,
    bg="#3b82f6", fg="white",
    font=("Arial", 14)
).pack(pady=20)

load()
root.mainloop()