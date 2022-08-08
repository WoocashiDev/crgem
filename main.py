from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/templates')
def templates():
    return render_template('message-templates.html')

@app.route('/templates/new')
def new_template():
    return render_template('create-template.html')

if __name__ == "__main__":
    app.run(debug=True)