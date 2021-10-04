from flask import Flask,render_template,request

app = Flask(__name__)

@app.route("/")
def landing():
    return render_template('landing.html')

@app.route("/home")
def home():
    return render_template('home.html')
