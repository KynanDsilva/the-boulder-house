from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.now().year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html', current_year=datetime.now().year)

@app.route('/book', methods=['GET', 'POST'])
def book():
    return render_template('book.html', current_year=datetime.now().year)

if __name__ == '__main__':
    app.run(debug=True)