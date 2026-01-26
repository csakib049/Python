import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# ================= CONFIG =================
image_folder = r"E:\MEME research of Subbir\meme sent by sabbir\Memes"
excel_path = r"E:\MEME research of Subbir\meme sent by sabbir\Memes\Meme_annotations_Binar.xlsx"
target_column = "Humiliation"

# ================= DATA =================
df = pd.read_excel(excel_path)

if target_column not in df.columns:
    df[target_column] = None

df = df.sort_values(
    by="Image_Name",
    key=lambda x: x.astype(str).str.extract(r"(\d+)")[0].astype(float)
).reset_index(drop=True)

rows_to_annotate = df[df[target_column].isna()].index.tolist()
if not rows_to_annotate:
    print("🎉 All annotations done!")
    exit()

current_index = 0

# ================= GUI =================
root = tk.Tk()
root.title("4 Image Annotation Tool")
root.geometry("1400x900")
root.configure(bg="#1e1e1e")

# ---------- SUBJECT (TOP-LEFT) ----------
tk.Label(
    root,
    text=target_column,
    fg="white",
    bg="#1e1e1e",
    font=("Arial", 20, "bold")
).pack(anchor="w", padx=30, pady=10)

# ---------- MAIN GRID ----------
grid_frame = tk.Frame(root, bg="#1e1e1e")
grid_frame.pack()

panels = []

def create_panel(parent):
    panel = {}

    frame = tk.Frame(parent, bg="#1e1e1e", bd=2)
    frame.pack_propagate(False)
    frame.config(width=600, height=350)

    panel["frame"] = frame

    panel["image_label"] = tk.Label(frame, bg="#1e1e1e")
    panel["image_label"].pack()

    panel["filename"] = tk.Label(
        frame, fg="white", bg="#1e1e1e",
        font=("Arial", 11)
    )
    panel["filename"].pack(pady=3)

    panel["value"] = tk.IntVar(value=-1)
    panel["buttons"] = {}

    btn_frame = tk.Frame(frame, bg="#1e1e1e")
    btn_frame.pack(pady=5)

    def set_value(v):
        panel["value"].set(v)
        update_highlight(panel)

    for v in [0, 1]:
        btn = tk.Label(
            btn_frame,
            text=str(v),
            width=4,
            font=("Arial", 14),
            bg="#2d2d2d",
            fg="white",
            padx=8, pady=4
        )
        btn.pack(side="left", padx=5)
        btn.bind("<Button-1>", lambda e, val=v: set_value(val))
        panel["buttons"][v] = btn

    panel["set_value"] = set_value
    return panel

def update_highlight(panel):
    for val, btn in panel["buttons"].items():
        btn.config(
            bg="#3b82f6" if panel["value"].get() == val else "#2d2d2d"
        )

# Create 4 panels (2x2)
for i in range(4):
    p = create_panel(grid_frame)
    p["frame"].grid(row=i//2, column=i%2, padx=20, pady=20)
    panels.append(p)

# ---------- LOAD 4 IMAGES ----------
def load_images():
    for p in panels:
        p["value"].set(-1)
        update_highlight(p)
        p["image_label"].configure(image="")
        p["filename"].configure(text="")

    for i in range(4):
        if current_index + i >= len(rows_to_annotate):
            continue

        idx = rows_to_annotate[current_index + i]
        name = df.at[idx, "Image_Name"]
        path = os.path.join(image_folder, name)

        img = Image.open(path)
        img.thumbnail((500, 260))
        tk_img = ImageTk.PhotoImage(img)

        panels[i]["image_label"].configure(image=tk_img)
        panels[i]["image_label"].image = tk_img
        panels[i]["filename"].configure(text=name)

# ---------- SAVE ----------
def save_next():
    global current_index

    for i in range(4):
        if current_index + i >= len(rows_to_annotate):
            continue
        if panels[i]["value"].get() == -1:
            messagebox.showwarning("Missing", "Please label all visible images")
            return

    for i in range(4):
        if current_index + i >= len(rows_to_annotate):
            continue
        df.at[rows_to_annotate[current_index + i], target_column] = panels[i]["value"].get()

    df.to_excel(excel_path, index=False)

    current_index += 4

    if current_index >= len(rows_to_annotate):
        messagebox.showinfo("Done", "🎉 Annotation Finished!")
        root.destroy()
        return

    load_images()

# ---------- KEYBOARD (OPTIONAL) ----------
def on_key(event):
    key = event.keysym
    mapping = {
        "1": (0, 0), "2": (0, 1),
        "3": (1, 0), "4": (1, 1),
        "5": (2, 0), "6": (2, 1),
        "7": (3, 0), "8": (3, 1),
    }
    if key in mapping:
        panel_id, val = mapping[key]
        panels[panel_id]["set_value"](val)
    elif key == "Return":
        save_next()

root.bind("<Key>", on_key)

# ---------- SAVE BUTTON ----------
tk.Button(
    root,
    text="Save All & Next ➡️",
    command=save_next,
    width=25,
    height=2,
    bg="#3b82f6",
    fg="white",
    font=("Arial", 14)
).pack(pady=20)

load_images()
root.mainloop()
