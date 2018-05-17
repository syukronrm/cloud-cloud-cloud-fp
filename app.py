import os
import subprocess
import sqlite3 as lite
import machine
import docker
from docker import *
from flask import Flask, session, redirect, url_for, escape, request, flash, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/syukronrm/Kuliah/cloud/fp/app/uploads'
ALLOWED_EXTENSIONS = set(['tar.gz'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

con = lite.connect('init.db')

m = machine.Machine(path="/usr/local/bin/docker-machine")
manager = docker.DockerClient(**m.config(machine='manager'))
managerLowLevel = docker.APIClient(**m.config(machine='manager'))

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

@app.route('/deployment', methods=['GET'])
def deployment():
    return render_template('deployment.html')

@app.route('/deployment/deploy', methods=['GET', 'POST'])
def deploy():
    if request.method == 'POST':
        name = session['username']
        cluster = request.form['cluster']
        image = request.form['image']
        container = request.form['container']

        try:
            client.networks.create(cluster, driver='overlay')
        except:
            pass

        os.system('docker-machine ssh manager "docker network create --driver=overlay ' + cluster + '"')
        os.system('docker-machine ssh manager "docker service create \
            --name ' + container + ' \
            --label traefik.port=80 \
            --network '+ cluster +' \
            '+ image +'"')

        flash('container ' + container + ' on network ' + cluster + ' has been deployed')
        return redirect(url_for('deployment'))

    return render_template('deploy.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

