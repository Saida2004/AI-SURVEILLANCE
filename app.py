from flask import Flask, render_template, request, redirect, url_for, flash
import threading
import os
from werkzeug.utils import secure_filename
from detect_live import run_live_monitoring, stop_monitoring
from detect_video import process_uploaded_video

app = Flask(__name__)
app.secret_key = 'asdfghjk23456'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/live')
def live():
    thread = threading.Thread(target=run_live_monitoring)
    thread.start()
    return render_template('live.html')

@app.route('/stop')
def stop():
    stop_monitoring()  # You must define this in detect_live.py
    flash("Live monitoring stopped.", "success")
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['video']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = process_uploaded_video(filepath)
        return render_template('result.html', result=result)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
