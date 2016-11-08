import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    render_template, flash, _app_ctx_stack
from contextlib import closing
from werkzeug import generate_password_hash, check_password_hash
import datetime
import config

app = Flask(__name__)
app.config.from_object(config)


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
        Initialize the DB when the app is first run
    '''
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as schema:
            db.cursor().executescript(schema.read())
        db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


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


def get_all_issues():
    '''
        Called when super admin logs in
        Get all issues on the system
    '''
    response = query_db('''SELECT istbl.issue_id,istbl.raised_by,
        istbl.description,istbl.created,usrtbl.forename AS raised_forename,
        usrtbl.surname AS raised_surname
        FROM issues AS istbl INNER JOIN users AS usrtbl ON
        istbl.raised_by = usrtbl.user_id''')
    return response if response else False


def get_department_issues(admin_id):
    '''
        Called when a department admin logs in
        Get all issues tagged for their department
    '''
    department_id = is_department_admin(admin_id)
    if department_id:
        response = query_db('SELECT * FROM issues WHERE department = ?',
                            department_id)
        return response if response else False
    else:
        return False


def get_my_issues(client_id):
    '''
        Called when a client logs in
        Get all issues client raised
    '''
    response = query_db('''SELECT * FROM issues WHERE raised_by = ?''',
                        client_id)
    return response if response else False


def get_assigned_issues(rep_id):
    '''
        Called when a support rep logs in
        Get all issues asisgned to rep
    '''
    response = query_db('''SELECT * FROM issues WHERE assigned_to = ?''',
                        rep_id)
    return response if response else False


def is_department_admin(user_id):
    '''
        Check if a user is a department admin
        If they are, return the department_id
    '''
    response = query_db('''SELECT department_id FROM departments
                        WHERE department_admin = ?''',
                        user_id, one=True)
    return response if response else False


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
        Register a new user
        User defaults to Client user level
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
                                         3, datetime.datetime.utcnow(),
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
            session['user_level'] = user['user_level']
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """
        Logs a user out
    """
    session.pop('user_id', None)
    session.pop('user_level', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    '''
        If the user is a super admin (User Level 1), get all issues
        If the user is a department admin (User Level 2), get their
            department issues
        If the user is a client (User Level 3), get just their raised issues
        If the user is a support rep (User Level 4), view  issues
            asigned to them only

        Load the relevant template
    '''
    issues = None
    if(g.user['user_level'] == 1):
        issues = get_all_issues()
    elif(g.user['user_level'] == 2):
        user_id = int(g.user['user_id'])
        # print g.user['user_id']
        # print g.user['user_level']
        issues = get_department_issues(user_id)
    elif(g.user['user_level'] == 3):
        pass
    elif(g.user['user_level'] == 4):
        pass
    return render_template('dashboard.html', issues=issues)


@app.route('/issues/raise')
def raise_issue():
    return render_template('raise_issue.html')


@app.route('/issues/edit/<issue_id>')
def edit_issue(issue_id):
    pass


@app.route('/issues/delete/<issue_id>')
def delete_issue(issue_id):
    pass


@app.route('/users')
def users():
    users = query_db('''SELECT usrtbl.user_id,usrtbl.forename,usrtbl.surname,
        usrtbl.email,usrtbl.created,
        usrtbl.user_level,ultbl.user_level_name FROM users as usrtbl
        INNER JOIN user_levels AS ultbl
        ON usrtbl.user_level = ultbl.user_level_id''')
    return render_template('users.html', users=users)


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    errors = []
    if request.method == 'POST':
        if not request.form['forename']:
            errors.append('You have to enter a forename')
        if not request.form['surname']:
            errors.append('You have to enter a surname')
        if not request.form['email']:
            errors.append('You have to enter a email address')
        if not request.form['user_level']:
            errors.append('You have to enter a user level')
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            errors.append('You have to enter a valid email address')
        elif not request.form['password']:
            errors.append('You have to enter a password')
        elif request.form['password'] != request.form['confirm_password']:
            errors.append('The two passwords do not match')
        elif user_exists(request.form['email']):
            errors.append('That email address is already taken')
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
                                         request.form['user_level'],
                                         datetime.datetime.utcnow(),
                                         datetime.datetime.utcnow()])
            db.commit()
            # Send flash message
            flash('You have added a new user')
            return redirect(url_for('users'))
    user_levels = query_db('''SELECT * FROM user_levels''')
    return render_template('add_user.html',
                           user_levels=user_levels, errors=errors)


@app.route('/users/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    errors = []
    if request.method == 'POST':
        if not request.form['forename']:
            errors.append('You have to enter a forename')
        if not request.form['surname']:
            errors.append('You have to enter a surname')
        if not request.form['email']:
            errors.append('You have to enter a email address')
        if not request.form['user_level']:
            errors.append('You have to enter a user level')
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            errors.append('You have to enter a valid email address')
        else:
            db = get_db()
            db.execute('''UPDATE users SET
              forename = ?, surname = ?, email = ?, user_level = ?,
              modified = ? WHERE user_id = ?''',
                       [request.form['forename'],
                        request.form['surname'], request.form['email'],
                        request.form['user_level'],
                        datetime.datetime.utcnow(), user_id])
            db.commit()
            # Send flash message
            flash('You have updated the user details')
            return redirect(url_for('users'))
    user_levels = query_db('''SELECT * FROM user_levels''')
    user = query_db('''SELECT * FROM users as usrtbl WHERE user_id = ?''',
                    user_id, one=True)
    return render_template('edit_user.html', user=user,
                           user_levels=user_levels, errors=errors)


@app.route('/users/delete/<user_id>')
def delete_user(user_id):
    pass


if __name__ == "__main__":
    app.run(debug=True)
