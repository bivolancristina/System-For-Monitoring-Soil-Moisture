from flask import Flask, render_template, url_for, redirect, request, Response, jsonify, session, flash
from flask_mail import Mail, Message
import psutil
import datetime
import water
import os
import sys
import pyrebase
import jsonconverter as jsonc
from forms import LoginForm

app = Flask(__name__)
app.secret_key = os.urandom(12)

user_email = 'bivolancristina15@gmail.com'
global user_pass
global last_water_value
last_water_value = 99

mail = Mail(app)
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= 465
app.config['MAIL_USE_TLS']= False
app.config['MAIL_USE_SSL']= True
app.config['MAIL_USERNAME']= 'happyplants124@gmail.com'
app.config['MAIL_PASSWORD']= 'Albastru22@'


mail = Mail(app)

config = {
  "apiKey": "AIzaSyB4W8KnKysrPZtZVah-DWYJFTaaWtz1EU8",
  "authDomain": "happyplants-62b64.firebaseapp.com",
  "databaseURL": "https://happyplants-62b64-default-rtdb.firebaseio.com",
  "storageBucket": "happyplants-62b64.appspot.com",
  "serviceAccount": "key.json"
}

firebase = pyrebase.initialize_app(config)

# Get a reference to the database service
db = firebase.database()
auth = firebase.auth()

# signup
@app.route("/signup", methods=['GET', 'POST'])
def signup():
  global user_email
  if session.get('logged_in'):
    return redirect(url_for('dashboard'))
  else:
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_email = form.username.data
            user_pass = form.password.data
            user = auth.create_user_with_email_and_password(user_email,user_pass)
            user_token = user['idToken']
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        except:
          flash('Sign up Unsuccessful. Please check username and password', 'danger')
  return render_template('signup.html', title='Sign Up', form=form)

# login
@app.route("/login", methods=['GET', 'POST'])
def login():
  global user_email
  if session.get('logged_in'):
    return redirect(url_for('dashboard'))
  else:
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_email = form.username.data
            user_pass = form.password.data
            user = auth.sign_in_with_email_and_password(user_email,user_pass)
            user_token = user['idToken']
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        except:
          flash('Login Unsuccessful. Please check username and password', 'danger')
  return render_template('login.html', title='Login', form=form)

# logout
@app.route("/logout")
def logout():
  session.pop('logged_in', None)
  return redirect(url_for('login'))

# pages
@app.route("/")
@app.route("/dashboard")
def dashboard():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  else:
    return render_template('dashboard.html', title='Dashboard', active='dashboard')

@app.route("/graph")
def graph():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  else:
    return render_template('graph.html', title='Graph', active='graph')

# api routes
@app.route("/api/getData", methods=['POST', 'GET'])
def api_getData():
  if request.method == 'POST':
    global last_water_value
    try:
      temperatureAir = water.get_air_temperature()
      temperatureWater = water.get_water_temperature()
      humidity = water.get_air_humidity()
      moisture = water.get_soil_status()
      usedWater = water.return_FlowRate()
      if usedWater == 0 and moisture == 1 and last_water_value != usedWater:
        with app.app_context():
          msg = Message(subject="Alert",
                        sender = app.config.get("MAIL_USERNAME"),
                        recipients = [user_email],
                        body = "Your tank is empty. Please refill!"
                        )
          mail.send(msg)
      if water.get_water_temperature() < 15:
        with app.app_context():
          msg = Message(subject="Alert",
                        sender = app.config.get("MAIL_USERNAME"),
                        recipients = [user_email],
                        body = "Your water is too cold for the plants!Please change it!"
                        )
          mail.send(msg)
      if water.get_water_temperature() > 30:
        with app.app_context():
          msg = Message(subject="Alert",
                        sender = app.config.get("MAIL_USERNAME"),
                        recipients = [user_email],
                        body = "Your water is too hot for the plants!Please change it!"
                        )
          mail.send(msg)
      last_water_value = usedWater
      if (moisture == 1):
        message = "Watering is needed!"
      else:
        message = "No need for watering!"
      time_now = datetime.datetime.now()
      datetime_converted = jsonc.json.dumps(time_now,indent = 4,sort_keys = True, default=str)
      data = {"DateTime": datetime_converted,
              "temperatureAir": temperatureAir,
              "temperatureWater": temperatureWater,
              "humidity": humidity,
              "moisture": message,
              "usedWater": usedWater
              }
      db.child("plants").push(data)
      data_converted = jsonc.data_to_json(db.child("plants").get().val())
      loaded_data = jsonc.json.loads(data_converted)
      print(loaded_data)
      return jsonify(loaded_data)
    except:
      print(sys.exc_info()[0])
      print(sys.exc_info()[1])
      return None
  else:
    return render_template('dashboard.html', title='Dashboard', active='dashboard')

@app.route("/api/getChartData", methods=['POST', 'GET'])
def api_getChartData():
  if request.method == 'POST':
    try:
      data = jsonc.data_to_json(db.child("plants").get().val())
      loaded_data = jsonc.json.loads(data)
      print(loaded_data)
      return jsonify(loaded_data)
    except:
      print(sys.exc_info()[0])
      print(sys.exc_info()[1])
      return None
  else:
    return render_template('graph.html', title='Graph', active='graph')

@app.route("/api/status", methods=['GET', 'POST'])
def status():
  try:
    data = jsonc.data_to_json(db.child("pump").get().val())
    loaded_data = jsonc.json.loads(data)
  
    return jsonify(loaded_data)   
  except:
    print(sys.exc_info()[0])
    print(sys.exc_info()[1])
    return None

@app.route("/changeStatus/<status>")
def changeStatus(status):
  try:
    time_now = datetime.datetime.now()
    datetime_converted = jsonc.json.dumps(time_now,indent = 4,sort_keys = True, default=str)
    data = {"DateTime": datetime_converted,
            "Status": status}
    db.child("pump").push(data)
    if status == 'A':
        running = False
        water.reset_count_water()
        for process in psutil.process_iter():
            try:
                if process.cmdline()[1] == 'auto_water.py':
                    running = True
            except:
                pass
        if not running:
            os.system("sudo python3 auto_water.py")
    elif status == 'M' or status == 'F':
        water.pump_off()
        os.system("pkill -f auto_water.py")
        if water.get_soil_status() == 1 : 
            with app.app_context():
               msg = Message(subject="Alert",
                        sender = app.config.get("MAIL_USERNAME"),
                        recipients = [user_email],
                        body = "Your plants need water!Please turn on automated watering!"
                        )
               mail.send(msg)
    elif status == 'O':
        water.pump_on_manual()
        water.reset_count_water()

    return status
  except:    
    print(sys.exc_info()[0])
    print(sys.exc_info()[1])
    return None

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)