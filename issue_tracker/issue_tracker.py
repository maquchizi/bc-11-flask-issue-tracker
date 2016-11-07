import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    render_template, flash, _app_ctx_stack
from contextlib import closing
from werkzeug import generate_password_hash
import datetime
from os import path

# configuration
ROOT = path.dirname(path.realpath(__file__))
DATABASE = path.join(ROOT, "issue_tracker.db")

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/hello")
def hello():
    return "Hello World!"


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
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(email):
    """Convenience method to look up the id for a email."""
    rv = query_db('select user_id from users where email = ?',
                  [email], one=True)
    return rv[0] if rv else None


@app.route("/register", methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('hello'))
    error = None
    if request.method == 'POST':
        if not request.form['forename']:
            error = 'You have to enter a forename'
        if not request.form['surname']:
            error = 'You have to enter a surname'
        if not request.form['email']:
            error = 'You have to enter a email'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['confirm_password']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['email']) is not None:
            error = 'The email is already taken'
        else:
            db = get_db()
            db.execute('''INSERT INTO users (
              forename, surname, email, password, created) VALUES
              (?, ?, ?, ?, ?)''', [request.form['forename'],
                                   request.form['surname'],
                                   request.form['email'],
                                   generate_password_hash(
                                       request.form['password']),
                                   datetime.datetime.utcnow()])
            db.commit()
            # Send flash message
            flash('You were successfully registered and can login now')
            return redirect(url_for('hello'))
    return render_template('register.html', error=error)


@app.route("/login", methods=['POST'])
def login():
    pass


@app.before_request
def before_request():
    ''' Check if user is logged in on every request '''
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from users where user_id = ?',
                          [session['user_id']], one=True)


@app.teardown_request
def teardown_request(exception):
    ''' Destroy DB connection after every request '''
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    '''Initialize the DB when the app if first run'''
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as schema:
            db.cursor().executescript(schema.read())
        db.commit()


if __name__ == "__main__":
    app.run(debug=True)
