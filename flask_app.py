
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, redirect, make_response, url_for
from flask import request, session, jsonify
from random import randint
#from io import StringIO
#import csv

#rootDir = "/home/lewfer/mysite/"           # pythonanywhere
rootDir = ""                              # local


app = Flask(__name__,
            template_folder=rootDir+'templates/',
            static_folder=rootDir+'static/')
            
# Not thread-safe, but should be ok in single-threaded developer Flask
data = {}
data['stations'] = {}
data['totalGenerated'] = 0
data['totalWind'] = 0
data['totalSolar'] = 0
data['totalUsed'] = 0
data['consumptionRate'] = 1/5  # proportion of device power used on each call
data['yellowZone'] = 10000     # total energy below which bar goes yellow
data['redZone'] = 5000         # total energy below which bar goes red
data['on'] = 1                 # is national grid on or off?




#mysql = "gecko101"

# Set the secret key so session encryption works
app.secret_key = b'A]qr>n@2XB"{B;CN'

# -------------------------------------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------------------------------------
def resetEverything():
    """Reset all the data"""
    global data
    data = {}
    data['stations'] = {}
    data['totalGenerated'] = 0
    data['totalWind'] = 0
    data['totalSolar'] = 0
    data['totalUsed'] = 0
    data['consumptionRate'] = 1/5  # proportion of device power used on each call
    data['yellowZone'] = 10000     # total energy below which bar goes yellow
    data['redZone'] = 5000         # total energy below which bar goes red
    data['on'] = 1                 # is national grid on or off?

def addEnergy(stationName, wind, solar):
    """Add energy from the power station"""

    # Add to station's total
    if not stationName in data["stations"]:
        data["stations"][stationName] = {'wind':0,'solar':0}
    data["stations"][stationName]['wind'] += wind
    data["stations"][stationName]['solar'] += solar

    # Add to total total
    data['totalWind'] += wind
    data['totalSolar'] += solar
    data['totalGenerated'] += wind+solar

def useEnergy(energy):
    """Use energy from the power station"""

    # Add to used energy, applying consumption rate
    data['totalUsed'] += int(energy * data['consumptionRate'])




# -------------------------------------------------------------------------------------------------
# Route handlers
# -------------------------------------------------------------------------------------------------

@app.route('/add')
def add():
    """Add energy from the power station"""

    if data['on']:
        # Get request arguments
        stationName = request.args.get('stationName')
        wind = request.args.get('wind')
        solar = request.args.get('solar')
        wind = int(wind)
        solar = int(solar)

        # Add energy to grid
        addEnergy(stationName, wind, solar)

    # Return data in response
    return jsonify(data)


@app.route('/use')
def use():
    """Use energy from the power station"""

    if data['on']:
        # Get request arguments
        energy = int(request.args.get('energy'))

        # Add to used energy, applying consumption rate
        useEnergy(energy)

    # Return data in response
    return jsonify(data)


@app.route('/status')
def status():
    """Get the current status"""

    return jsonify(data)


@app.route('/getcsvdata')
def getCsvData():
    """Get the station data as a csv"""

    c = "station,wind,solar\r\n"

    # Add station data
    for k in data["stations"].keys():
        #if not k.startswith("total"):
            c += k + "," + str(data["stations"][k]["wind"]) + "," + str(data["stations"][k]["solar"])+"\r\n"

    output = make_response(c)
    #output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/getavailableenergy')
def getAvailableEnergy():
    """Get the total energy available"""

    return jsonify(data['totalGenerated']-data['totalUsed'])


@app.route('/reset')
def reset():
    """Reset everything"""

    resetEverything()
    return jsonify(data)


# -------------------------------------------------------------------------------------------------
# Dashboard

@app.route('/dashboard')
def dashboard():
    """Show the dashboard, with charts"""
    return render_template('dashboard.html', appData=data)


# -------------------------------------------------------------------------------------------------
# Control Page and Control Page form handlers

@app.route('/control')
def control():
    """Show the control centre page"""
    return render_template('control.html', appData=data) 

@app.route('/controlOnOff')
def controlOnOff():
    """Turn grid on or off"""
    on = request.args.get('gridOn')
    data["on"] = 1 if on else 0

    # Redirect to control page
    return redirect(url_for('control'))


@app.route('/controlAddEnergy')
def controlAddEnergy():
    """Handle import and add energy forms"""

    if data['on']:
        # Get args
        station = request.args.get('station')
        wind = request.args.get('wind')
        solar = request.args.get('solar')
        wind = int(wind)
        solar = int(solar)

        # Add energy
        addEnergy(station, wind, solar)

    # Redirect to control page
    return redirect(url_for('control'))


@app.route('/controlResetZero')
def controlResetZero():
    """Handle Reset form.  Reset everything to 0"""
    resetEverything()
    return redirect(url_for('control'))

@app.route('/controlUseEnergy')
def controlUseEnergy():
    """Handle Use Energy form"""

    if data['on']:    
        # Get args
        energy = int(request.args.get('energy'))

        # Use energy from power station
        useEnergy(energy)

    return redirect(url_for('control'))

@app.route('/controlSettings')
def controlSettings():
    """Handle Settings form"""
    global consumptionRate, yellowZone, redZone
    data["consumptionRate"] = float(request.args.get('consumptionRate'))
    data["yellowZone"] = float(request.args.get('yellowZone'))
    data["redZone"] = float(request.args.get('redZone'))
    return redirect(url_for('control'))

@app.route('/controlTestData')
def controlTestData():
    """Add test data"""    
    addEnergy("Panda Power", randint(0,100), randint(0,100))
    addEnergy("Eagle Energy", randint(0,100), randint(0,100))
    addEnergy("Rhino Renewables", randint(0,100), randint(0,100))
    addEnergy("Swan Sustainables", randint(0,100), randint(0,100))
    addEnergy("Gecko Green Energy", randint(0,100), randint(0,100))
    addEnergy("Possum Power", randint(0,100), randint(0,100))
    addEnergy("Emu Energy", randint(0,100), randint(0,100))
    addEnergy("Robin Renewables", randint(0,100), randint(0,100))
    addEnergy("Stingray Sustainables", randint(0,100), randint(0,100))
    addEnergy("Gazelle Green Energy", randint(0,100), randint(0,100))
    return redirect(url_for('control'))

if __name__ == '__main__':
   app.run(threaded=False, host="0.0.0.0", port=8000)