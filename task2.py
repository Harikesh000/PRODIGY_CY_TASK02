import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import random

WINDOW_TITLE = "Image Encryption/Decryption Tool"
MAX_DISPLAY_SIZE = (480, 360)

# --- Encryption ---
def encrypt_image_pil(img: Image.Image, key: int) -> Image.Image:
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img, dtype=np.uint8)

    h, w, c = arr.shape
    rng = random.Random(key)

    # Step 1: XOR with key
    arr = arr ^ (key % 256)

    # Step 2: Shuffle rows
    row_order = list(range(h))
    rng.shuffle(row_order)
    arr = arr[row_order, :, :]

    # Step 3: Shuffle columns
    col_order = list(range(w))
    rng.shuffle(col_order)
    arr = arr[:, col_order, :]

    return Image.fromarray(arr, mode="RGB")

# --- Decryption ---
def decrypt_image_pil(img: Image.Image, key: int) -> Image.Image:
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img, dtype=np.uint8)

    h, w, c = arr.shape
    rng = random.Random(key)

    # Recreate shuffle orders
    row_order = list(range(h))
    rng.shuffle(row_order)
    col_order = list(range(w))
    rng.shuffle(col_order)

    # Step 3 inverse: unshuffle columns
    inv_col = np.argsort(col_order)
    arr = arr[:, inv_col, :]

    # Step 2 inverse: unshuffle rows
    inv_row = np.argsort(row_order)
    arr = arr[inv_row, :, :]

    # Step 1 inverse: XOR again
    arr = arr ^ (key % 256)

    return Image.fromarray(arr, mode="RGB")

# --- GUI ---
class ImageEncryptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)

        self.input_img = None
        self.output_img = None
        self.input_preview = None
        self.output_preview = None

        self._build_ui()

    def _build_ui(self):
        title = tk.Label(self.root, text=WINDOW_TITLE, font=("Arial", 16, "bold"))
        title.pack(pady=8)

        # Load
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=6, fill=tk.X)
        tk.Label(top_frame, text="Select Image:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(12, 6))
        tk.Button(top_frame, text="select", width=10, command=self.on_load).pack(side=tk.LEFT)

        # Key input
        key_frame = tk.Frame(self.root)
        key_frame.pack(pady=6, fill=tk.X)
        tk.Label(key_frame, text="Key (any integer):", font=("Arial", 11)).pack(side=tk.LEFT, padx=(12, 6))
        self.key_entry = tk.Entry(key_frame, width=15)
        self.key_entry.pack(side=tk.LEFT)
        tk.Label(key_frame, text="(Don't forget the Key. It will be required for Decryption.)", font=("Arial", 11)).pack(side=tk.LEFT, padx=(12, 6))
        # Main panes
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=8, fill=tk.BOTH, expand=True)

        # Left
        left_frame = tk.Frame(main_frame, bd=1, relief=tk.GROOVE, padx=8, pady=8)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        tk.Label(left_frame, text="Input Image:", font=("Arial", 12, "bold")).pack(anchor="w")
        btn_frame_left = tk.Frame(left_frame)
        btn_frame_left.pack(anchor="w", pady=6)
        tk.Button(btn_frame_left, text="Encrypt", width=10, command=self.on_encrypt).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame_left, text="Decrypt", width=10, command=self.on_decrypt).pack(side=tk.LEFT)
        self.input_canvas = tk.Label(left_frame, bg="#f0f0f0", width=60, height=20)
        self.input_canvas.pack(fill=tk.BOTH, expand=True, pady=(8, 4))

        # Right
        right_frame = tk.Frame(main_frame, bd=1, relief=tk.GROOVE, padx=8, pady=8)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        tk.Label(right_frame, text="Encrypted/Decrypted Image:", font=("Arial", 12, "bold")).pack(anchor="w")
        btn_frame_right = tk.Frame(right_frame)
        btn_frame_right.pack(anchor="w", pady=6)
        tk.Button(btn_frame_right, text="Save", width=10, command=self.on_save).pack(side=tk.LEFT)
        self.output_canvas = tk.Label(right_frame, bg="#f0f0f0", width=60, height=20)
        self.output_canvas.pack(fill=tk.BOTH, expand=True, pady=(8, 4))

        self.status = tk.Label(self.root, text="Ready", anchor="w", relief=tk.SUNKEN)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _get_key(self):
        try:
            return int(self.key_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a numeric key.")
            return None

    def on_load(self):
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.webp"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            img = Image.open(path)
            self.input_img = img
            self._update_preview(img, "input")
            self.output_img = None
            self._clear_preview("output")
            self.status.config(text=f"Loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def on_encrypt(self):
        key = self._get_key()
        if key is None or self.input_img is None:
            return
        try:
            out = encrypt_image_pil(self.input_img, key)
            self.output_img = out
            self._update_preview(out, "output")
            self.status.config(text="Encryption complete.")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed:\n{e}")

    def on_decrypt(self):
        key = self._get_key()
        if key is None or (self.input_img is None and self.output_img is None):
            return
        source = self.output_img if self.output_img is not None else self.input_img
        try:
            out = decrypt_image_pil(source, key)
            self.output_img = out
            self._update_preview(out, "output")
            self.status.config(text="Decryption complete.")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed:\n{e}")

    def on_save(self):
        if self.output_img is None:
            messagebox.showinfo("Info", "No processed image to save yet.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if not path:
            return
        try:
            self.output_img.save(path)
            messagebox.showinfo("Saved", f"Image saved to {path}")
            self.status.config(text=f"Saved: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image:\n{e}")

    # def _update_preview(self, img, target):
    #     preview = img.copy()
    #     preview.thumbnail(MAX_DISPLAY_SIZE, Image.LANCZOS)
    #     tk_img = ImageTk.PhotoImage(preview)
    #     if target == "input":
    #         self.input_preview = tk_img
    #         self.input_canvas.config(image=self.input_preview)
    #     else:
    #         self.output_preview = tk_img
    #         self.output_canvas.config(image=self.output_preview)
    def _update_preview(self, img: Image.Image, target: str):
        # Create a fixed canvas size
        canvas_w, canvas_h = 600, 500

        # Copy and resize image to fit inside 800x700
        preview = img.copy()
        preview.thumbnail((canvas_w, canvas_h), Image.LANCZOS)

        # Create a blank background
        bg = Image.new("RGB", (canvas_w, canvas_h), (240, 240, 240))

        # Center the preview
        x = (canvas_w - preview.width) // 2
        y = (canvas_h - preview.height) // 2
        bg.paste(preview, (x, y))

        tk_img = ImageTk.PhotoImage(bg)

        if target == "input":
            self.input_preview = tk_img
            self.input_canvas.config(image=self.input_preview, width=canvas_w, height=canvas_h)
        else:
            self.output_preview = tk_img
            self.output_canvas.config(image=self.output_preview, width=canvas_w, height=canvas_h)


    def _clear_preview(self, target):
        if target == "input":
            self.input_canvas.config(image="")
        else:
            self.output_canvas.config(image="")

# def main():
#     root = tk.Tk()
#     app = ImageEncryptorApp(root)
#     root.geometry("980x600")
#     root.mainloop()
def main():
    root = tk.Tk()
    app = ImageEncryptorApp(root)
    # root.geometry("980x600")   # remove this
    root.state("zoomed")   
    root.resizable(False, False)    # Windows
    # root.attributes("-zoomed", True)  # Linux/macOS alternative
    root.mainloop()


if __name__ == "__main__":
    main()
