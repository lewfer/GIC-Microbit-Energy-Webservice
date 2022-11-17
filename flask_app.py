
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, redirect, make_response, url_for
from flask import request, session, jsonify
#from io import StringIO
#import csv

#rootDir = "/home/lewfer/mysite/"           # pythonanywhere
rootDir = ""                              # local


app = Flask(__name__,
            template_folder=rootDir+'templates/',
            static_folder=rootDir+'static/')
            

data = {}
data['users'] = {}
data['totalGenerated'] = 0
data['totalWind'] = 0
data['totalSolar'] = 0
data['totalUsed'] = 0
data['consumptionRate'] = 1/5  # proportion of device power used on each call
data['yellowZone'] = 10000     # total energy below which bar goes yellow
data['redZone'] = 5000         # total energy below which bar goes red

consumptionRate = 1/5  # proportion of device power used on each call
yellowZone = 10000     # total energy below which bar goes yellow
redZone = 5000         # total energy below which bar goes red


#mysql = "gecko101"

# Set the secret key so session encryption works
app.secret_key = b'A]qr>n@2XB"{B;CN'

# -------------------------------------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------------------------------------


def addEnergy(username, wind, solar):
    # Add to user's total
    if not username in data:
        data["users"][username] = {'wind':0,'solar':0}
    data["users"][username]['wind'] += wind
    data["users"][username]['solar'] += solar

    # Add to total total
    data['totalWind'] += wind
    data['totalSolar'] += solar
    data['totalGenerated'] += wind+solar



# -------------------------------------------------------------------------------------------------
# Route handlers
# -------------------------------------------------------------------------------------------------

@app.route('/')
def hello_world():
    return 'Girls into Coding Energy Project'


@app.route('/register')
def register():
    username  = request.args.get('user')
    data["users"][username] = {'wind':0,'solar':0}
    return 'Succeeded'

@app.route('/whoami')
def whoami():
    return session['username']

@app.route('/add')
def add():
    username = request.args.get('username')
    wind = request.args.get('wind')
    solar = request.args.get('solar')
    wind = int(wind)
    solar = int(solar)
    addEnergy(username, wind, solar)
    return jsonify(data)

@app.route('/use')
def use():
    energy = int(request.args.get('energy'))
    data['totalUsed'] += int(energy * consumptionRate)
    return jsonify(data)

@app.route('/get')
def get():
    return jsonify(data)

@app.route('/getcsvdata')
def getcsvdata():
    c = "generator,wind,solar\r\n"

    # Add total data
    c += "total" + "," + str(data["totalWind"]) + "," + str(data["totalSolar"])+"\r\n"

    # Add total generated/used (hack!!)
    c += "used" + "," + str(data['totalGenerated']) + "," + str(data['totalUsed'])+"\r\n"

    # Add yellow/red zone (hack!!)
    c += "yr" + "," + str(yellowZone) + "," + str(redZone)+"\r\n"

    # Add user data
    for k in data["users"].keys():
        #if not k.startswith("total"):
            c += k + "," + str(data["users"][k]["wind"]) + "," + str(data["users"][k]["solar"])+"\r\n"

    output = make_response(c)
    #output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

    #return csv


@app.route('/gettotalenergy')
def gettotalenergy():
    #totalEnergy = 0
    #for i, value in enumerate(data):
    #    totalEnergy += data[value]["wind"]+data[value]["solar"]
    return jsonify(data['totalGenerated']-data['totalUsed'])

@app.route('/reset')
def reset():
    global data
    data = {}
    data['totalGenerated'] = 0
    data['totalUsed'] = 0
    return jsonify(data)


# -------------------------------------------------------------------------------------------------
# Dashboard

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')#, appData=data)


# -------------------------------------------------------------------------------------------------
# Control Page and Control Page form handlers

@app.route('/control')
def control():
    return render_template('control.html', consumptionRate=consumptionRate, yellowZone=yellowZone, redZone=redZone)

@app.route('/import')
def importEnergy():
    username = request.args.get('username')
    wind = request.args.get('wind')
    solar = request.args.get('solar')
    wind = int(wind)
    solar = int(solar)
    addEnergy(username, wind, solar)

    return redirect(url_for('control'))

@app.route('/resetzero')
def resetZero():
    global data
    data = {}
    data['totalGenerated'] = 0
    data['totalUsed'] = 0
    return redirect(url_for('control'))

@app.route('/useenergy')
def useEnergy():
    energy = int(request.args.get('energy'))
    data['totalUsed'] += int(energy * consumptionRate)
    return redirect(url_for('control'))

@app.route('/settings')
def settings():
    global consumptionRate, yellowZone, redZone
    consumptionRate = float(request.args.get('consumptionRate'))
    yellowZone = float(request.args.get('yellowZone'))
    redZone = float(request.args.get('redZone'))
    return redirect(url_for('control'))


if __name__ == '__main__':
   app.run()