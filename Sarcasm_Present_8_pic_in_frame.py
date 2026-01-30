import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# ================= CONFIG =================
image_folder = r"E:\MEME research of Subbir\meme sent by sabbir\Memes"
excel_path = r"E:\MEME research of Subbir\meme sent by sabbir\Memes\Meme_annotations_Binar.xlsx"
target_column = "Sarcasm_Present"

# 8 images per batch
IMAGES_PER_BATCH = 8 
IMG_WIDTH = 480
IMG_HEIGHT = 350
FRAME_WIDTH = 500
# REDUCED from 450 to 400 to save vertical space
FRAME_HEIGHT = 400 

# ================= DATA & RESUME LOGIC =================
df = pd.read_excel(excel_path)

if target_column not in df.columns:
    df[target_column] = None

df = df.sort_values(
    by="Image_Name",
    key=lambda x: x.astype(str).str.extract(r"(\d+)")[0].astype(float)
).reset_index(drop=True)

unlabeled_indices = df[df[target_column].isna()].index.tolist()
if unlabeled_indices:
    current_index = (unlabeled_indices[0] // IMAGES_PER_BATCH) * IMAGES_PER_BATCH
else:
    current_index = 0

# ================= GUI =================
root = tk.Tk()
root.title("Sarcasm Annotation Tool - 8 Photo Grid")
root.state("zoomed")
root.configure(bg="#1e1e1e")

# --- HEADER SECTION (Tightened Padding) ---
header_frame = tk.Frame(root, bg="#1e1e1e")
header_frame.pack(fill="x", padx=20, pady=5) # Reduced pady from 15 to 5

tk.Label(
    header_frame,
    text="sarcasm = কটাক্ষ",
    fg="#fde047",
    bg="#1e1e1e",
    font=("Arial", 22, "bold")
).pack(side="left", padx=(0, 40))

tk.Label(
    header_frame,
    text="Keyboard: [0] All Zero | [⬅️] Prev | [➡️] Next",
    fg="white", bg="#1e1e1e",
    font=("Arial", 14)
).pack(side="left")

progress_label = tk.Label(
    header_frame, text="", fg="#10b981", bg="#1e1e1e", font=("Arial", 14, "bold")
)
progress_label.pack(side="right")

# --- MAIN GRID (Tightened Padding) ---
grid_frame = tk.Frame(root, bg="#1e1e1e")
grid_frame.pack(pady=0) # Removed pady

panels = []

def create_panel(parent):
    panel = {}
    frame = tk.Frame(parent, bg="#1e1e1e", width=FRAME_WIDTH, height=FRAME_HEIGHT)
    frame.pack_propagate(False)

    img_label = tk.Label(frame, bg="#1e1e1e")
    img_label.pack()

    fname = tk.Label(frame, fg="white", bg="#1e1e1e", font=("Arial", 9))
    fname.pack()

    val = tk.IntVar(value=-1)
    btns = {}

    btn_frame = tk.Frame(frame, bg="#1e1e1e")
    btn_frame.pack(pady=0) # Tightened padding

    def set_value(v):
        val.set(v)
        for k, b in btns.items():
            b.config(bg="#3b82f6" if k == v else "#2d2d2d")

    for v in [0, 1]:
        b = tk.Label(
            btn_frame, text=str(v),
            width=5, font=("Arial", 12, "bold"),
            bg="#2d2d2d", fg="white", cursor="hand2"
        )
        b.pack(side="left", padx=8)
        b.bind("<Button-1>", lambda e, x=v: set_value(x))
        btns[v] = b

    panel.update({"frame": frame, "image": img_label, "fname": fname, "value": val, "set": set_value, "buttons": btns})
    return panel

for i in range(IMAGES_PER_BATCH):
    p = create_panel(grid_frame)
    p["frame"].grid(row=i//4, column=i%4, padx=5, pady=2) # Reduced pady from 5 to 2
    panels.append(p)

# ================= LOGIC FUNCTIONS =================
def load_images():
    total = len(df)
    labeled = df[target_column].notna().sum()
    progress_label.config(text=f"{labeled} / {total} Done")

    for p in panels:
        p["image"].config(image="")
        p["fname"].config(text="")
        p["value"].set(-1)
        for b in p["buttons"].values():
            b.config(bg="#2d2d2d")

    for i in range(IMAGES_PER_BATCH):
        idx = current_index + i
        if idx >= len(df): continue

        name = df.at[idx, "Image_Name"]
        path = os.path.join(image_folder, name)
        try:
            img = Image.open(path)
            img.thumbnail((IMG_WIDTH, IMG_HEIGHT))
            tk_img = ImageTk.PhotoImage(img)
            panels[i]["image"].config(image=tk_img)
            panels[i]["image"].image = tk_img
            panels[i]["fname"].config(text=name)

            saved_val = df.at[idx, target_column]
            if pd.notna(saved_val): panels[i]["set"](int(saved_val))
        except:
            panels[i]["fname"].config(text="Load Error")

def set_all_zero():
    for p in panels:
        if p["fname"].cget("text") and "Error" not in p["fname"].cget("text"):
            p["set"](0)

def save_next():
    global current_index
    for i in range(IMAGES_PER_BATCH):
        idx = current_index + i
        if idx >= len(df): continue
        
        if panels[i]["value"].get() == -1:
            messagebox.showwarning("Missing", f"Label required for: {panels[i]['fname'].cget('text')}")
            return
        df.at[idx, target_column] = panels[i]["value"].get()

    df.to_excel(excel_path, index=False)
    current_index += IMAGES_PER_BATCH
    if current_index >= len(df):
        messagebox.showinfo("Done", "All memes labeled!")
        current_index = max(0, len(df) - IMAGES_PER_BATCH)
    load_images()

def go_previous():
    global current_index
    current_index = max(0, current_index - IMAGES_PER_BATCH)
    load_images()

# ================= KEYBINDINGS =================
def on_key(e):
    if e.keysym == "0":
        set_all_zero()
    elif e.keysym in ["Return", "Right"]:
        save_next()
    elif e.keysym == "Left":
        go_previous()

root.bind("<Key>", on_key)

# --- FOOTER SECTION (More compact) ---
footer_frame = tk.Frame(root, bg="#1e1e1e")
footer_frame.pack(side="bottom", fill="x", pady=5) # Reduced pady from 10 to 5

tk.Button(
    footer_frame, text="🔥 ALL ZERO (0)", 
    command=set_all_zero, bg="#ef4444", fg="white", 
    font=("Arial", 11, "bold"), width=15 # Slightly smaller font/width
).pack(side=tk.LEFT, padx=50)

tk.Button(
    footer_frame, text="Save & Next ➡️", 
    command=save_next, bg="#3b82f6", fg="white", 
    font=("Arial", 12, "bold"), width=20 # Slightly smaller font/width
).pack(side=tk.RIGHT, padx=50)

load_images()
root.mainloop()