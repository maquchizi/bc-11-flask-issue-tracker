import sqlite3
from flask import Flask, _app_ctx_stack
from contextlib import closing
import config

app = Flask(__name__)
app.config.from_object(config)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    '''
        Initialize the DB when the app is first run
    '''
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as schema:
            db.cursor().executescript(schema.read())
        db.commit()


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
    response = query_db('''SELECT user_id FROM users WHERE email = ?''',
                        [email], one=True)
    return response[0] if response else False
