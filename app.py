import os
from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from arnold_cat_map import arnold_cat_map, logistic_map_scramble, logistic_map_descramble, inverse_arnold_cat_map, save_image_from_matrix
from image_to_rgb_matrix import image_to_rgb_matrix
import numpy as np

UPLOAD_FOLDER = 'uploads'
ENCRYPTED_FOLDER = 'encrypted'
DECRYPTED_FOLDER = 'decrypted'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENCRYPTED_FOLDER'] = ENCRYPTED_FOLDER
app.config['DECRYPTED_FOLDER'] = DECRYPTED_FOLDER

for folder in [UPLOAD_FOLDER, ENCRYPTED_FOLDER, DECRYPTED_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    print("Files received:", request.files)
    if 'image' not in request.files:
        print("No image part in request.files")
        return jsonify({'error': 'No image part'}), 400
    file = request.files['image']
    print("Received file:", file.filename)
    if file.filename == '':
        print("Empty filename")
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        print(f"Saved file to {upload_path}")
        return jsonify({'filename': filename}), 200
    else:
        print("File type not allowed")
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/encrypt', methods=['POST'])
def encrypt_image():
    data = request.json
    filename = data.get('filename')
    x = data.get('x')
    r = data.get('r')
    if not filename or x is None or r is None:
        return jsonify({'error': 'Missing parameters'}), 400

    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(upload_path):
        return jsonify({'error': 'Uploaded image not found'}), 400

    try:
        x = float(x)
        r = float(r)
    except ValueError:
        return jsonify({'error': 'Invalid numeric values for x or r'}), 400

    rgb_matrix = image_to_rgb_matrix(upload_path)
    if rgb_matrix.shape[0] != rgb_matrix.shape[1]:
        return jsonify({'error': 'Image must be square (NxN) for Arnold Cat Map'}), 400

    scrambled_matrix = arnold_cat_map(rgb_matrix)
    doubly_scrambled_matrix = logistic_map_scramble(scrambled_matrix, x, r)

    # Save encrypted image as PNG
    base_name = os.path.splitext(filename)[0]
    encrypted_filename = f'encrypted_{base_name}.png'
    encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
    save_image_from_matrix(doubly_scrambled_matrix, encrypted_path)

    return jsonify({'encrypted_image': encrypted_filename}), 200

@app.route('/decrypt', methods=['POST'])
def decrypt_image():
    data = request.json
    encrypted_filename = data.get('encrypted_filename')
    x = data.get('x')
    r = data.get('r')
    if not encrypted_filename or x is None or r is None:
        return jsonify({'error': 'Missing parameters'}), 400

    encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
    if not os.path.exists(encrypted_path):
        return jsonify({'error': 'Encrypted image not found'}), 400

    try:
        x = float(x)
        r = float(r)
    except ValueError:
        return jsonify({'error': 'Invalid numeric values for x or r'}), 400

    rgb_matrix = image_to_rgb_matrix(encrypted_path)
    if rgb_matrix.shape[0] != rgb_matrix.shape[1]:
        return jsonify({'error': 'Encrypted image must be square (NxN) for Arnold Cat Map'}), 400

    descrambled_matrix = logistic_map_descramble(rgb_matrix, x, r)
    decrypted_matrix = inverse_arnold_cat_map(descrambled_matrix)

    # Save decrypted image as PNG
    base_name = os.path.splitext(encrypted_filename)[0]
    decrypted_filename = f'decrypted_{base_name}.png'
    decrypted_path = os.path.join(app.config['DECRYPTED_FOLDER'], decrypted_filename)
    save_image_from_matrix(decrypted_matrix, decrypted_path)

    return jsonify({'decrypted_image': decrypted_filename}), 200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/encrypted/<filename>')
def encrypted_file(filename):
    return send_from_directory(app.config['ENCRYPTED_FOLDER'], filename)

@app.route('/decrypted/<filename>')
def decrypted_file(filename):
    return send_from_directory(app.config['DECRYPTED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
