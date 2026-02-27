import easyocr
import cv2
import numpy as np
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# =========================
# EASY OCR INITIALIZATION
# =========================
reader = easyocr.Reader(['en'], gpu=False)

# =========================
# UI COLORS
# =========================
BG_MAIN = "#f4f6f8"
BG_CARD = "#ffffff"
PRIMARY = "#2563eb"
TEXT_DARK = "#111827"
TEXT_LIGHT = "#6b7280"

# =========================
# IMAGE PREPROCESSING
# =========================
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    return thresh

# =========================
# FILE SELECTION
# =========================
def select_file():
    file_path = filedialog.askopenfilename(
        title="Select Image or PDF",
        filetypes=[
            ("Images", "*.png *.jpg *.jpeg *.bmp"),
            ("PDF Files", "*.pdf")
        ]
    )
    if file_path:
        image_label.config(text=file_path)
        process_file(file_path)

# =========================
# OCR PROCESSING
# =========================
def process_file(path):
    extracted_text = ""
    try:
        if path.lower().endswith(".pdf"):
            pages = convert_from_path(path)
            for i, page in enumerate(pages):
                page_np = np.array(page)
                page_np = preprocess_image(page_np)

                results = reader.readtext(
                    page_np,
                    paragraph=True,
                    contrast_ths=0.1,
                    adjust_contrast=0.7
                )

                extracted_text += f"\n--- Page {i+1} ---\n"
                for item in results:
                    text = item[1]   # ONLY text exists here
                    extracted_text += text + " "

        else:
            img = cv2.imread(path)
            processed = preprocess_image(img)

            show_image(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))

            results = reader.readtext(
                processed,
                paragraph=True,
                contrast_ths=0.1,
                adjust_contrast=0.7
            )

            texts = [item[1] for item in results]
            extracted_text = " ".join(texts)

        extracted_text = extracted_text.strip()
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, extracted_text)

        save_json(path, extracted_text)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# =========================
# SAVE JSON
# =========================
def save_json(source, text):
    filename = simpledialog.askstring("Save JSON", "Enter JSON filename:")
    if not filename:
        return
    if not filename.endswith(".json"):
        filename += ".json"

    os.makedirs("output", exist_ok=True)

    data = {
        "source_file": source,
        "extracted_text": text,
        "text_length": len(text),
        "ocr_engine": "EasyOCR (Deep Learning)",
        "mode": "paragraph"
    }

    with open(f"output/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    messagebox.showinfo("Success", f"JSON saved as output/{filename}")

# =========================
# IMAGE PREVIEW
# =========================
def show_image(img):
    img.thumbnail((220, 220))
    img_tk = ImageTk.PhotoImage(img)
    image_preview.config(image=img_tk)
    image_preview.image = img_tk

# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("AI OCR Image & PDF to JSON")
root.geometry("950x650")
root.configure(bg=BG_MAIN)

header = tk.Label(
    root,
    text="📄 AI OCR Image & PDF to JSON",
    font=("Segoe UI", 22, "bold"),
    bg=BG_MAIN,
    fg=TEXT_DARK
)
header.pack(pady=(20, 5))

subtitle = tk.Label(
    root,
    text="Deep Learning OCR • Supports Stylized & Artistic Text",
    font=("Segoe UI", 11),
    bg=BG_MAIN,
    fg=TEXT_LIGHT
)
subtitle.pack(pady=(0, 20))

card = tk.Frame(root, bg=BG_CARD, bd=1, relief="solid")
card.pack(padx=30, pady=10, fill="both", expand=True)

btn = tk.Button(
    card,
    text="Select Image / PDF",
    command=select_file,
    bg=PRIMARY,
    fg="white",
    font=("Segoe UI", 11, "bold"),
    padx=20,
    pady=8,
    relief="flat"
)
btn.pack(pady=15)

image_label = tk.Label(
    card,
    text="No file selected",
    bg=BG_CARD,
    fg=TEXT_LIGHT,
    wraplength=700
)
image_label.pack(pady=5)

image_preview = tk.Label(card, bg=BG_CARD)
image_preview.pack(pady=10)

result_text = tk.Text(
    card,
    height=15,
    width=100,
    font=("Consolas", 10),
    bg="#f9fafb",
    fg=TEXT_DARK,
    bd=1,
    relief="solid"
)
result_text.pack(padx=20, pady=15)

footer = tk.Label(
    root,
    text="✔ EasyOCR (AI)  •  ✔ Image & PDF OCR  •  ✔ JSON Export",
    bg=BG_MAIN,
    fg=TEXT_LIGHT,
    font=("Segoe UI", 10)
)
footer.pack(pady=10)

root.mainloop()
