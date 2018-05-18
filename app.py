import os
import subprocess
import sqlite3 as lite
import machine
import docker
from docker import *
from flask import Flask, session, redirect, url_for, escape, request, flash, render_template

app = Flask(__name__)

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
        domain = request.form['domain']

        try:
            client.networks.create(cluster, driver='overlay')
        except:
            pass

        domainLabel = ''
        if domain != '':
            domainLabel = '--label traefik.frontend.rule=Host:' + domain

        os.system('docker-machine ssh manager "docker network create --driver=overlay ' + cluster + '"')
        os.system('docker-machine ssh manager "docker service update --network-add ' + cluster + ' traefik"')
        os.system('docker-machine ssh manager "docker service create \
            --name ' + container + ' \
            ' + domainLabel + '\
            --label traefik.port=80 \
            --network '+ cluster +' \
            --label traefik.backend.loadbalancer.sticky=true \
            '+ image +'"')

        flash('container ' + container + ' on network ' + cluster + ' has been deployed')
        return redirect(url_for('deployment'))

    return render_template('deploy.html')

@app.route('/deployment/scale', methods=['GET', 'POST'])
def scale():
    if request.method == 'POST':
        container_id = request.form['container_id']
        scale_number = request.form['number']

        os.system('docker-machine ssh manager "docker service scale ' + container_id + '=' + scale_number + '"')

        flash('container ' + container_id + ' has been scaled to ' + scale_number)
        return redirect(url_for('deployment'))

    services = manager.services.list()
    return render_template('scale.html', services=services)
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
