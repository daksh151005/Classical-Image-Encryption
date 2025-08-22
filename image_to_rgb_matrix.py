from PIL import Image
import numpy as np

def image_to_rgb_matrix(image_path):
    """
    Convert an image file to a numpy RGB matrix.
    """
    img = Image.open(image_path).convert('RGB')
    return np.array(img)
