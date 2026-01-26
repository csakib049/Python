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

# ================= GUI =================
root = tk.Tk()
root.title(f"{target_column} Annotation (Side by Side)")
root.geometry("1300x700")
root.configure(bg="#1e1e1e")

# ---------- MAIN FRAME ----------
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(pady=10)

# ---------- LEFT & RIGHT PANELS ----------
panels = {}

def create_panel(parent, title):
    panel = {}

    frame = tk.Frame(parent, bg="#1e1e1e")
    frame.pack(side="left", padx=20)

    panel["image_label"] = tk.Label(frame, bg="#1e1e1e")
    panel["image_label"].pack()

    panel["filename"] = tk.Label(
        frame, fg="white", bg="#1e1e1e",
        font=("Arial", 12, "bold")
    )
    panel["filename"].pack(pady=5)

    panel["value"] = tk.IntVar(value=-1)

    btn_frame = tk.Frame(frame, bg="#1e1e1e")
    btn_frame.pack(pady=5)

    tk.Label(
        btn_frame, text=title,
        fg="white", bg="#1e1e1e",
        font=("Arial", 12)
    ).pack(side="left", padx=10)

    panel["buttons"] = {}

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
            padx=10, pady=5
        )
        btn.pack(side="left", padx=6)
        btn.bind("<Button-1>", lambda e, val=v: set_value(val))
        panel["buttons"][v] = btn

    panel["set_value"] = set_value
    return panel

def update_highlight(panel):
    selected = panel["value"].get()
    for val, btn in panel["buttons"].items():
        btn.config(
            bg="#3b82f6" if val == selected else "#2d2d2d"
        )

panels["left"] = create_panel(main_frame, "Odd Image")
panels["right"] = create_panel(main_frame, "Even Image")

# ---------- LOAD IMAGES ----------
def load_pair():
    for side in ["left", "right"]:
        panels[side]["value"].set(-1)
        update_highlight(panels[side])

    if current_index >= len(rows_to_annotate):
        return

    # LEFT (ODD)
    idx_left = rows_to_annotate[current_index]
    name_left = df.at[idx_left, "Image_Name"]
    path_left = os.path.join(image_folder, name_left)

    img = Image.open(path_left)
    img.thumbnail((550, 450))
    tk_img = ImageTk.PhotoImage(img)

    panels["left"]["image_label"].configure(image=tk_img)
    panels["left"]["image_label"].image = tk_img
    panels["left"]["filename"].configure(text=name_left)

    # RIGHT (EVEN) — only if exists
    if current_index + 1 < len(rows_to_annotate):
        idx_right = rows_to_annotate[current_index + 1]
        name_right = df.at[idx_right, "Image_Name"]
        path_right = os.path.join(image_folder, name_right)

        img = Image.open(path_right)
        img.thumbnail((550, 450))
        tk_img = ImageTk.PhotoImage(img)

        panels["right"]["image_label"].configure(image=tk_img)
        panels["right"]["image_label"].image = tk_img
        panels["right"]["filename"].configure(text=name_right)
    else:
        panels["right"]["image_label"].configure(image="")
        panels["right"]["filename"].configure(text="")

# ---------- SAVE ----------
def save_next():
    global current_index

    left_val = panels["left"]["value"].get()
    right_val = panels["right"]["value"].get()

    if left_val == -1:
        messagebox.showwarning("Missing", "Choose value for left image")
        return

    df.at[rows_to_annotate[current_index], target_column] = left_val

    if current_index + 1 < len(rows_to_annotate):
        if right_val == -1:
            messagebox.showwarning("Missing", "Choose value for right image")
            return
        df.at[rows_to_annotate[current_index + 1], target_column] = right_val

    df.to_excel(excel_path, index=False)

    current_index += 2

    if current_index >= len(rows_to_annotate):
        messagebox.showinfo("Done", f"{target_column} Annotation Finished!")
        root.destroy()
        return

    load_pair()

# ---------- KEYBOARD ----------
def on_key(event):
    key = event.keysym

    if key == "0":
        panels
    elif key == "1":
        panels
    elif key == "2":
        panels
    elif key == "3":
        panels
    elif key == "Return":
        save_next()

root.bind("<Key>", on_key)

# ---------- SAVE BUTTON ----------
tk.Button(
    root,
    text="Save Both & Next ➡️",
    command=save_next,
    width=25, height=2,
    bg="#3b82f6", fg="white",
    font=("Arial", 14)
).pack(pady=15)

load_pair()
root.mainloop()
