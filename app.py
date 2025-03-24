from flask import Flask, render_template, request, redirect, url_for, session
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret123'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy user data
users = {'test': {'password': 'test123'}}

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid Credentials. Try Again!"
    return render_template('login.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "User already exists!"
        else:
            users[username] = {'password': password}
            return redirect(url_for('login'))
    return render_template('signup.html')

# Handle AI Suggestions
@app.route('/suggestions', methods=['POST'])
def suggestions():
    skin_tone = request.form['skin_tone']
    body_shape = request.form['body_shape']

    recommendations = generate_recommendations(skin_tone, body_shape)
    return render_template('result.html', recommendations=recommendations)

# Upload Face & Dress Pictures
@app.route('/upload', methods=['POST'])
def upload():
    if 'face' not in request.files or 'dress' not in request.files:
        return "No file uploaded"

    face_file = request.files['face']
    dress_file = request.files['dress']

    if face_file.filename == '' or dress_file.filename == '':
        return "No file selected"

    face_filename = secure_filename(face_file.filename)
    dress_filename = secure_filename(dress_file.filename)

    face_path = os.path.join(app.config['UPLOAD_FOLDER'], face_filename)
    dress_path = os.path.join(app.config['UPLOAD_FOLDER'], dress_filename)

    face_file.save(face_path)
    dress_file.save(dress_path)

    output_image = generate_visual(face_path, dress_path)
    return render_template('result.html', face_path=face_path, dress_path=dress_path, output_image=output_image)

# Generate Dress Suggestions
def generate_recommendations(skin_tone, body_shape):
    suggestions = []
    if skin_tone == 'fair' and body_shape == 'hourglass':
        suggestions.append('A-line dresses in pastel shades')
    elif skin_tone == 'dusky' and body_shape == 'pear':
        suggestions.append('Dark-colored tops with wide skirts')
    else:
        suggestions.append('Neutral shades with structured outfits')
    return suggestions

# 2D Try-On with OpenCV (Basic Simulation)
def generate_visual(face_path, dress_path):
    face_img = cv2.imread(face_path)
    dress_img = cv2.imread(dress_path)
    if face_img is None or dress_img is None:
        return None

    output_image = f'static/uploads/output_{os.path.basename(face_path)}'
    cv2.imwrite(output_image, dress_img)
    return output_image




if __name__ == '__main__':
    app.run(debug=True)
