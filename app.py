import os
import subprocess
import MySQLdb
from flask import Flask, session, redirect, url_for, escape, request, flash, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/syukronrm/Kuliah/cloud/fp/app/uploads'
ALLOWED_EXTENSIONS = set(['tar.gz'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db = MySQLdb.connect("localhost", "root", "sandi", "cloud" )

@app.route('/')
def index():
    name = None
    if 'username' in session:
        name = session['username']
    return render_template('hello.html', name=name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/deploy', methods=['GET'])
def deployment():
    return render_template('deployment.html')

@app.route('/deploy/deploy', methods=['GET', 'POST'])
def deploy():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')

            return redirect(request.url)
        if file:
            flash('file uploaded')

            filename = secure_filename(file.filename)
            foldername = filename.split('.')[0]

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            command = '/bin/tar -xzf ' + filename + ' --directory ' + foldername

            os.chdir(UPLOAD_FOLDER)
            subprocess.check_output(['mkdir', foldername])
            subprocess.check_output(command.split(' '))

            return redirect(url_for('deploy', filename=filename))

        flash('file not uploaded')
        return redirect(request.url)

    name = session['username']
    return render_template('upload.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

