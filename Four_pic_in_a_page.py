import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# ================= CONFIG =================
image_folder = r"E:\MEME research of Subbir\meme sent by sabbir\Memes"
excel_path = r"E:\MEME research of Subbir\meme sent by sabbir\Memes\Meme_annotations_Binar.xlsx"
target_column = "Humiliation"
IMAGES_PER_BATCH = 6  # Changed to 6 images

# ================= DATA =================
df = pd.read_excel(excel_path)

if target_column not in df.columns:
    df[target_column] = None

# Sort by number in filename
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
root.title("6 Image Annotation Tool")
root.state('zoomed')  # Auto-maximize window
root.configure(bg="#1e1e1e")

# ---------- SUBJECT (TOP-LEFT) ----------
tk.Label(
    root,
    text=f"{target_column} (Press 0 for ALL 0s)",
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

    # Width reduced to 450 to fit 3 columns
    frame = tk.Frame(parent, bg="#1e1e1e", bd=2)
    frame.pack_propagate(False)
    frame.config(width=450, height=350)

    panel["frame"] = frame

    panel["image_label"] = tk.Label(frame, bg="#1e1e1e")
    panel["image_label"].pack()

    panel["filename"] = tk.Label(
        frame, fg="white", bg="#1e1e1e",
        font=("Arial", 10)
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

# Create 6 panels (2 rows x 3 columns)
for i in range(IMAGES_PER_BATCH):
    p = create_panel(grid_frame)
    # Logic: i//3 gives row (0,1), i%3 gives col (0,1,2)
    p["frame"].grid(row=i//3, column=i%3, padx=10, pady=10)
    panels.append(p)

# ---------- SET ALL TO 0 FUNCTION ----------
def set_all_to_zero():
    """Set all visible panels to 0"""
    for panel in panels:
        # Only set if panel has an image loaded
        if panel["filename"].cget("text") != "":
            panel["set_value"](0)
    print("✅ All visible images set to 0")

# ---------- LOAD IMAGES ----------
def load_images():
    for p in panels:
        p["value"].set(-1)
        update_highlight(p)
        p["image_label"].configure(image="")
        p["filename"].configure(text="")

    for i in range(IMAGES_PER_BATCH):
        if current_index + i >= len(rows_to_annotate):
            continue

        idx = rows_to_annotate[current_index + i]
        name = df.at[idx, "Image_Name"]
        path = os.path.join(image_folder, name)

        try:
            img = Image.open(path)
            # Resize logic for smaller panels
            img.thumbnail((420, 240))
            tk_img = ImageTk.PhotoImage(img)

            panels[i]["image_label"].configure(image=tk_img)
            panels[i]["image_label"].image = tk_img
            panels[i]["filename"].configure(text=name)
        except Exception as e:
            panels[i]["filename"].configure(text="Error loading img")

# ---------- SAVE ----------
def save_next():
    global current_index

    # Check for missing values
    for i in range(IMAGES_PER_BATCH):
        if current_index + i >= len(rows_to_annotate):
            continue
        if panels[i]["value"].get() == -1:
            messagebox.showwarning("Missing", "Please label all visible images")
            return

    # Save
    for i in range(IMAGES_PER_BATCH):
        if current_index + i >= len(rows_to_annotate):
            continue
        df.at[rows_to_annotate[current_index + i], target_column] = panels[i]["value"].get()

    df.to_excel(excel_path, index=False)

    current_index += IMAGES_PER_BATCH

    if current_index >= len(rows_to_annotate):
        messagebox.showinfo("Done", "🎉 Annotation Finished!")
        root.destroy()
        return

    load_images()

# ---------- KEYBOARD SHORTCUTS ----------
def on_key(event):
    key = event.keysym.lower()
    
    # 0 = All Zero
    if key == "0":
        set_all_to_zero()
        return
    
    # Enter = Save
    if key == "return":
        save_next()
        return

    # Spatial Mapping (QWERTY rows match visual rows)
    # Row 1: Q/W, E/R, T/Y
    # Row 2: A/S, D/F, G/H
    mapping = {
        "q": (0, 0), "w": (0, 1),  # Panel 1
        "e": (1, 0), "r": (1, 1),  # Panel 2
        "t": (2, 0), "y": (2, 1),  # Panel 3
        "a": (3, 0), "s": (3, 1),  # Panel 4
        "d": (4, 0), "f": (4, 1),  # Panel 5
        "g": (5, 0), "h": (5, 1),  # Panel 6
    }
    
    if key in mapping:
        panel_id, val = mapping[key]
        if panel_id < len(panels):
            if panels[panel_id]["filename"].cget("text") != "":
                panels[panel_id]["set_value"](val)

root.bind("<Key>", on_key)

# ---------- BUTTONS ----------
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="🔥 ALL 0 (Key: 0)",
    command=set_all_to_zero,
    width=20, height=1,
    bg="#ef4444", fg="white",
    font=("Arial", 12, "bold")
).pack(side=tk.LEFT, padx=10)

tk.Button(
    button_frame,
    text="Save All & Next ➡️ (Enter)",
    command=save_next,
    width=25, height=2,
    bg="#3b82f6", fg="white",
    font=("Arial", 14)
).pack(side=tk.LEFT, padx=10)

load_images()
root.mainloop()