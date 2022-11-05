
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, make_response
from flask import request, session, jsonify
#from io import StringIO
#import csv

rootDir = "/home/lewfer/mysite/"           # pythonanywhere
#rootDir = ""                              # local

#app = Flask(__name__,
#            template_folder='/home/lewfer/mysite/templates/',
#            static_folder='/home/lewfer/mysite/static/')

app = Flask(__name__,
            template_folder=rootDir+'templates/',
            static_folder=rootDir+'static/')

data = {}
data['totalGenerated'] = 0
data['totalUsed'] = 0

#mysql = "gecko101"

# Set the secret key so session encryption works
app.secret_key = b'A]qr>n@2XB"{B;CN'

@app.route('/')
def hello_world():
    return 'Girls into Coding Energy Project'

@app.route('/about')
def about():
    return 'This is my new webappppp' + request.args.get('data')

@app.route('/register')
def register():
    username  = request.args.get('user')
    data[username] = {'wind':0,'solar':0}
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

    # Add to user's total
    if not username in data:
        data[username] = {'wind':0,'solar':0}
    data[username]['wind'] += wind
    data[username]['solar'] += solar

    # Add to total total
    data['totalGenerated'] += wind+solar
    return jsonify(data)

@app.route('/use')
def use():
    energy = request.args.get('energy')
    data['totalUsed'] += int(energy)
    return jsonify(data)

@app.route('/get')
def get():
    return jsonify(data)

@app.route('/getcsvdata')
def getcsvdata():
    c = "generator,wind,solar\r\n"

    for k in data.keys():
        if not k.startswith("total"):
            c += k + "," + str(data[k]["wind"]) + "," + str(data[k]["solar"])+"\r\n"

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


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
   app.run()