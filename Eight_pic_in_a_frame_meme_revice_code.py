import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# ================= CONFIGURATION =================
IMAGE_FOLDER = r"E:\MEME2222 research of Subbir\Memes 2"
EXCEL_PATH = r"E:\MEME2222 research of Subbir\Excel file\Memes_2.xlsx"
TARGET_COLUMN = "Misogyny_Severity"
IMAGES_PER_BATCH = 8
ROWS = 2
COLS = 4
STATE_FILE = "review_state.txt"

# ================= DATA LOADING =================
try:
    df = pd.read_excel(EXCEL_PATH)
except Exception as e:
    print(f"Error loading Excel: {e}")
    exit()

if "Image_Name" not in df.columns:
    print("Error: 'Image_Name' column not found in Excel.")
    exit()

if TARGET_COLUMN not in df.columns:
    df[TARGET_COLUMN] = None

df = df.reset_index(drop=True)
current_index = 0

# ---------- LOAD PROGRESS ----------
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            current_index = int(f.read().strip())
            if current_index < 0 or current_index >= len(df):
                current_index = 0
    except:
        current_index = 0

# ================= GUI SETUP =================
root = tk.Tk()
root.title("Meme Annotation Reviewer - Misogyny (Auto-Zero Mode)")
root.state("zoomed")
root.configure(bg="#121212")

SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()

IMG_W = (SCREEN_W // COLS) - 40
IMG_H = (SCREEN_H // ROWS) - 220

# ---------- HEADER ----------
header_frame = tk.Frame(root, bg="#121212")
header_frame.pack(fill="x", padx=20, pady=10)

title_label = tk.Label(
    header_frame,
    text=TARGET_COLUMN,
    fg="#3b82f6",
    bg="#121212",
    font=("Arial", 24, "bold")
)
title_label.pack(side="left")

# ---------- SEARCH ----------
search_frame = tk.Frame(header_frame, bg="#121212")
search_frame.pack(side="right")

tk.Label(
    search_frame,
    text="Jump to Image:",
    fg="white",
    bg="#121212"
).pack(side="left", padx=5)

search_entry = tk.Entry(search_frame, font=("Arial", 12), width=20)
search_entry.pack(side="left", padx=5)

# ---------- COUNTER ----------
counter_label = tk.Label(
    root,
    text="",
    fg="#aaaaaa",
    bg="#121212",
    font=("Arial", 12)
)
counter_label.pack(anchor="w", padx=25)

# ---------- GRID ----------
grid_frame = tk.Frame(root, bg="#121212")
grid_frame.pack(expand=True, fill="both", padx=10, pady=10)

panels = []

# ================= FUNCTIONS =================
def save_state():
    with open(STATE_FILE, "w") as f:
        f.write(str(current_index))

def save_to_excel():
    df.to_excel(EXCEL_PATH, index=False)

def update_counter():
    total = len(df)
    completed = df[TARGET_COLUMN].notna().sum()
    counter_label.config(
        text=f"Showing: {current_index + 1} - {min(current_index + IMAGES_PER_BATCH, total)} / {total}    |    Completed: {completed}/{total}"
    )

def update_highlight(panel):
    val = panel["value"].get()
    for v, btn in panel["buttons"].items():
        if val == v:
            btn.config(bg="#3b82f6", fg="white")
        else:
            btn.config(bg="#2d2d2d", fg="#888888")

def set_panel_value(panel_idx, val, save=True):
    data_idx = current_index + panel_idx
    if data_idx < len(df):
        df.at[data_idx, TARGET_COLUMN] = val
        panels[panel_idx]["value"].set(val)
        update_highlight(panels[panel_idx])
        if save:
            save_to_excel()
            update_counter()

def jump_to_image():
    global current_index
    target_name = search_entry.get().strip()
    if target_name:
        matches = df.index[df["Image_Name"].astype(str) == target_name].tolist()
        if matches:
            current_index = (matches[0] // IMAGES_PER_BATCH) * IMAGES_PER_BATCH
            load_images()
            save_state()
        else:
            messagebox.showwarning("Not Found", f"Image '{target_name}' not found.")

search_btn = tk.Button(
    search_frame,
    text="Jump",
    command=jump_to_image,
    bg="#3b82f6",
    fg="white"
)
search_btn.pack(side="left", padx=5)

# ---------- PANEL CREATION ----------
def create_panel(idx):
    p_frame = tk.Frame(grid_frame, bg="#1e1e1e", bd=2, relief="flat")
    p_frame.grid(row=idx // COLS, column=idx % COLS, padx=5, pady=5, sticky="nsew")

    panel = {}
    panel["img_label"] = tk.Label(p_frame, bg="#1e1e1e")
    panel["img_label"].pack(pady=5, expand=True)

    panel["filename"] = tk.Label(
        p_frame, text="", fg="#00ff00", bg="#1e1e1e", font=("Arial", 10, "bold")
    )
    panel["filename"].pack()

    panel["value"] = tk.IntVar(value=-1)
    panel["buttons"] = {}

    btn_row = tk.Frame(p_frame, bg="#1e1e1e")
    btn_row.pack(pady=5)

    for v in [0, 1]:
        btn = tk.Label(
            btn_row, text=str(v), width=8, font=("Arial", 12, "bold"),
            bg="#2d2d2d", fg="white", cursor="hand2", padx=5, pady=2
        )
        btn.pack(side="left", padx=15)
        btn.bind("<Button-1>", lambda e, p_idx=idx, val=v: set_panel_value(p_idx, val))
        panel["buttons"][v] = btn

    return panel

for i in range(IMAGES_PER_BATCH):
    grid_frame.grid_columnconfigure(i % COLS, weight=1)
    grid_frame.grid_rowconfigure(i // COLS, weight=1)
    panels.append(create_panel(i))

# ---------- IMAGE LOADING ----------
def load_images():
    for i in range(IMAGES_PER_BATCH):
        idx = current_index + i
        panel = panels[i]

        panel["img_label"].config(image="")
        panel["img_label"].image = None
        panel["filename"].config(text="")
        panel["value"].set(-1)

        if idx < len(df):
            img_name = str(df.at[idx, "Image_Name"])
            img_path = os.path.join(IMAGE_FOLDER, img_name)
            panel["filename"].config(text=img_name, fg="#00ff00")

            existing_val = df.at[idx, TARGET_COLUMN]
            if pd.notna(existing_val):
                try:
                    panel["value"].set(int(existing_val))
                except:
                    panel["value"].set(-1)

            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((IMG_W, IMG_H))
                    tk_img = ImageTk.PhotoImage(img)
                    panel["img_label"].config(image=tk_img)
                    panel["img_label"].image = tk_img
                except:
                    panel["filename"].config(text="CORRUPT FILE", fg="red")
            else:
                panel["filename"].config(text="FILE MISSING", fg="red")

        update_highlight(panel)
    update_counter()

# ---------- NAVIGATION ----------
def next_batch():
    global current_index
    if current_index + IMAGES_PER_BATCH < len(df):
        current_index += IMAGES_PER_BATCH
        save_state()
        load_images()
        
        # --- AUTO-ZERO LOGIC ---
        # When moving to the next page, set everything to 0 by default
        for i in range(IMAGES_PER_BATCH):
            set_panel_value(i, 0, save=False)
        
        save_to_excel() # Save once for the whole batch
        update_counter()

def prev_batch():
    global current_index
    if current_index - IMAGES_PER_BATCH >= 0:
        current_index -= IMAGES_PER_BATCH
        save_state()
        load_images()

# ---------- KEYBOARD OPTIMIZATION ----------
def on_key(event):
    key = event.keysym.lower()

    if key == "d":
        next_batch()
    elif key == "a":
        prev_batch()
    elif key == "0":
        for i in range(IMAGES_PER_BATCH):
            set_panel_value(i, 0, save=False)
        save_to_excel()
        update_counter()

# ---------- CLOSE ----------
def on_close():
    save_state()
    save_to_excel()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.bind("<Key>", on_key)

# Start
load_images()
root.mainloop()