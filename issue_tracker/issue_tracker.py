import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    render_template, flash, _app_ctx_stack
from contextlib import closing
from werkzeug import generate_password_hash, check_password_hash
import datetime
from os import path

# configuration
ROOT = path.dirname(path.realpath(__file__))
DATABASE = path.join(ROOT, "issue_tracker.db")
SECRET_KEY = 'f0rtkn0x'

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/dashboard')
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


def get_db():
    """
        Opens a new database connection if there is none yet for the current
        application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


def query_db(query, args=(), one=False):
    """
        Queries the database and returns a list of dictionaries.
    """
    cur = get_db().execute(query, args)
    response = cur.fetchall()
    return (response[0] if response else None) if one else response


def user_exists(email):
    """
        Check if a user exists given their email address
        If they do, return their user_id
        If not return False
    """
    response = query_db('SELECT user_id FROM users WHERE email = ?',
                        [email], one=True)
    return response[0] if response else False


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
        Register a new user
    """
    if g.user:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        if not request.form['forename']:
            error = 'You have to enter a forename'
        if not request.form['surname']:
            error = 'You have to enter a surname'
        if not request.form['email']:
            error = 'You have to enter a email address'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['confirm_password']:
            error = 'The two passwords do not match'
        elif user_exists(request.form['email']):
            error = 'That email address is already taken'
        else:
            db = get_db()
            db.execute('''INSERT INTO users (
              forename, surname, email, password, user_level,
              created, modified) VALUES
              (?, ?, ?, ?, ?, ?, ?)''', [request.form['forename'],
                                         request.form['surname'],
                                         request.form['email'],
                                         generate_password_hash(
                                             request.form['password']),
                                         1, datetime.datetime.utcnow(),
                                         datetime.datetime.utcnow()])
            db.commit()
            # Send flash message
            flash('You were successfully registered and can login now')
            return redirect(url_for('dashboard'))
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Logs the user in
    """
    if g.user:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        user = query_db('''SELECT * FROM users WHERE
            email = ?''', [request.form['email']], one=True)
        if not request.form['email']:
            error = 'You have to enter a email address'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif user is None or not check_password_hash(user['password'],
                                                     request.form['password']):
            error = 'Invalid credentials'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """
        Logs a user out
    """
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.before_request
def before_request():
    '''
        Check if user is logged in on every request
    '''
    g.user = None
    if 'user_id' in session:
        g.user = query_db('SELECT * FROM users WHERE user_id = ?',
                          [session['user_id']], one=True)


@app.teardown_request
def teardown_request(exception):
    '''
        Destroy DB connection after every request
    '''
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    '''
        Initialize the DB when the app if first run
    '''
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as schema:
            db.cursor().executescript(schema.read())
        db.commit()


if __name__ == "__main__":
    app.run(debug=True)
