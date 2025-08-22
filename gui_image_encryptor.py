import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from arnold_cat_map import arnold_cat_map, logistic_map_scramble, logistic_map_descramble, inverse_arnold_cat_map, save_image_from_matrix
from image_to_rgb_matrix import image_to_rgb_matrix

class ImageEncryptorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Encryptor / Decryptor")

        self.image_path = None
        self.encrypted_image_path = "encrypted_image_gui.png"
        self.decrypted_image_path = "decrypted_image_gui.png"

        # UI Elements
        self.select_button = tk.Button(root, text="Select Image", command=self.select_image)
        self.select_button.pack(pady=5)

        self.label_x = tk.Label(root, text="Logistic Map Private Key x (e.g. 0.5888):")
        self.label_x.pack()
        self.entry_x = tk.Entry(root)
        self.entry_x.pack()

        self.label_r = tk.Label(root, text="Logistic Map Parameter r (e.g. 3.98888):")
        self.label_r.pack()
        self.entry_r = tk.Entry(root)
        self.entry_r.pack()

        self.encrypt_button = tk.Button(root, text="Encrypt Image", command=self.encrypt_image)
        self.encrypt_button.pack(pady=5)

        self.decrypt_button = tk.Button(root, text="Decrypt Image", command=self.decrypt_image)
        self.decrypt_button.pack(pady=5)

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

    def select_image(self):
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp")]
        path = filedialog.askopenfilename(title="Select Image", filetypes=filetypes)
        if path:
            self.image_path = path
            self.show_image(path)

    def show_image(self, path):
        img = Image.open(path)
        img.thumbnail((400, 400))
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)

    def encrypt_image(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return
        try:
            x = float(self.entry_x.get())
            r = float(self.entry_r.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for x and r.")
            return

        rgb_matrix = image_to_rgb_matrix(self.image_path)
        if rgb_matrix.shape[0] != rgb_matrix.shape[1]:
            messagebox.showerror("Error", "Image must be square (NxN) for Arnold Cat Map.")
            return

        scrambled_matrix = arnold_cat_map(rgb_matrix)
        doubly_scrambled_matrix = logistic_map_scramble(scrambled_matrix, x, r)
        save_image_from_matrix(doubly_scrambled_matrix, self.encrypted_image_path)
        self.show_image(self.encrypted_image_path)
        messagebox.showinfo("Success", f"Encrypted image saved as {self.encrypted_image_path}")

    def decrypt_image(self):
        if not os.path.exists(self.encrypted_image_path):
            messagebox.showerror("Error", "No encrypted image found. Please encrypt an image first.")
            return
        try:
            x = float(self.entry_x.get())
            r = float(self.entry_r.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for x and r.")
            return

        rgb_matrix = image_to_rgb_matrix(self.encrypted_image_path)
        if rgb_matrix.shape[0] != rgb_matrix.shape[1]:
            messagebox.showerror("Error", "Encrypted image must be square (NxN) for Arnold Cat Map.")
            return

        descrambled_matrix = logistic_map_descramble(rgb_matrix, x, r)
        decrypted_matrix = inverse_arnold_cat_map(descrambled_matrix)
        save_image_from_matrix(decrypted_matrix, self.decrypted_image_path)
        self.show_image(self.decrypted_image_path)
        messagebox.showinfo("Success", f"Decrypted image saved as {self.decrypted_image_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEncryptorGUI(root)
    root.mainloop()
