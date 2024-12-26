from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import validators
import os
import pickle
import newspaper
from newspaper import Article
import urllib
import nltk
import requests


from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# nltk.download('punkt_tab')

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = 'fk_news'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Database connection
DATABASE = 'fk_news.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure database and tables are created
def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            result TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')

# Initialize the database
init_db()


@app.route('/')
def home():
    return render_template('landing.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('predict'))

    if request.method == 'POST':

        username = request.form['username'].strip()
        name = request.form['name'].strip()
        password = request.form['password'].strip()

        # Input validation
        if not username or not password or not name:
            flash('Name, Username and password are required.', 'danger')
            return render_template('login.html')
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (name, username, password) VALUES (?, ?, ?)', (name, username, hashed_password))
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.commit()
            conn.close()

            # flash('Registration successful, please login.', 'success')
            session['user_id'] = user['id']
            return redirect(url_for('predict'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('predict'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            # flash('Login successful.', 'success')
            return redirect(url_for('predict'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    # flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    result = None
    input_text = ''

    if request.method == 'POST':
        input_text = request.form['input']

        with open('model.pickle', 'rb') as handle:
            model = pickle.load(handle)

        if validators.url(input_text):
            
            url = urllib.parse.unquote(input_text)
            article = Article(str(url))
            article.download()
            article.parse()
            article.nlp()
            news = article.summary

            print(news)
            pred = model.predict([news])
            result = format(pred[0])
        else:
            pred = model.predict([input_text])
            result = format(pred[0])

        # Save prediction to database
        user_id = session['user_id']
        conn = get_db_connection()
        conn.execute('INSERT INTO predictions (user_id, text, result) VALUES (?, ?, ?)', 
                     (user_id, input_text, result))
        conn.commit()
        conn.close()

    return render_template('predict.html', result=result, input_text=input_text)


@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    predictions = conn.execute('SELECT * FROM predictions WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
    conn.close()

    return render_template('history.html', predictions=predictions)

@app.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    result = None
    input_text = ''
    receipient = ''

    if request.method == 'POST':
        input_text = request.form['input']
        receipient = request.form['receipient']

        with open('model.pickle', 'rb') as handle:
            model = pickle.load(handle)

        if validators.url(input_text):
            
            url = urllib.parse.unquote(input_text)
            article = Article(str(url))
            article.download()
            article.parse()
            article.nlp()
            news = article.summary

            print(news)
            pred = model.predict([news])
            result = format(pred[0])
        else:
            pred = model.predict([input_text])
            result = format(pred[0])
        
        if result == 'REAL':
            # try:
                api_key='mgoZrsEVxmGH'
                url = f"https://api.textmebot.com/send.php?recipient={receipient}&apikey={api_key}&text={input_text}"
                response = requests.get(url)
                
                # Check if the message was sent successfully
                if response.status_code == 200:
                    flash("Message sent successfully!", "success")
                else:
                    flash(f"Failed to send message: Error with WhatsApp connection", "error")
            
            # except Exception as e:
            #     flash(f"An error occurred: {e}", "error")
        else:
            flash(f"Message not sent: Fake news detected", "danger")

        # Save prediction to database
        user_id = session['user_id']
        conn = get_db_connection()
        conn.execute('INSERT INTO predictions (user_id, text, result) VALUES (?, ?, ?)', 
                     (user_id, input_text, result))
        conn.commit()
        conn.close()

    return render_template('whatsapp.html', result=result, input_text=input_text, receipient=receipient)



if __name__ == '__main__':
    # Ensure 'static' folder exists
    if not os.path.exists('static'):
        os.makedirs('static')

    app.run(debug=True)
