import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def rgb_to_cmyk(rgb):
    # Normalize RGB values
    r, g, b = rgb / 255.0

    # Convert RGB to CMYK
    k = 1 - np.max(rgb / 255.0)
    if k == 1:
        cmyk = np.array([0, 0, 0, 1])
    else:
        c = (1 - r - k) / (1 - k)
        m = (1 - g - k) / (1 - k)
        y = (1 - b - k) / (1 - k)
        cmyk = np.array([c, m, y, k])

    return cmyk * 100

def cmyk_to_rgb(cmyk):
    c, m, y, k = cmyk / 100.0
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return np.clip([r, g, b], 0, 255).astype(np.uint8)

def increase_subtractive_saturation(image, factor):
    # Convert RGB to CMYK
    cmyk_image = np.apply_along_axis(rgb_to_cmyk, -1, image)

    # Scale CMY channels to increase saturation
    cmyk_image[..., :3] *= factor / 100.0

    # Convert CMYK back to RGB
    increased_saturation_image = np.apply_along_axis(cmyk_to_rgb, -1, cmyk_image)

    return increased_saturation_image

def update_image(value):
    saturation_factor = saturation_slider.get()
    increased_saturation_image = increase_subtractive_saturation(original_image, saturation_factor)
    img = Image.fromarray(increased_saturation_image)
    img.thumbnail((400, 400))
    img = ImageTk.PhotoImage(img)
    label.configure(image=img)
    label.image = img

# Load RGB image
original_image = cv2.imread('images/reference_dslr/Image16.png', cv2.IMREAD_COLOR)
original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

# Create GUI window
root = tk.Tk()
root.title("Adjust Saturation")

# Create a label to display the image
label = ttk.Label(root)
label.pack()

# Create a slider to adjust saturation
saturation_slider = ttk.Scale(root, from_=0, to=200, orient="horizontal", command=update_image)
saturation_slider.pack(padx=10, pady=10)
saturation_slider.set(100)  # Set initial saturation factor to 100%

# Display the original image
update_image(100)

# Run the GUI
root.mainloop()