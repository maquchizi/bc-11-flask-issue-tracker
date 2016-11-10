from flask import Flask, request, session, g, redirect, url_for, \
    render_template, flash
from werkzeug import generate_password_hash, check_password_hash
from flask_moment import Moment
from flask_socketio import *
import datetime
import config
from util import *
from issues_model import *

app = Flask(__name__)
app.config.from_object(config)
moment = Moment(app)
socketio = SocketIO(app)


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


@app.cli.command('initdb')
def initdb_command():
    """
        Creates the database tables
    """
    init_db()
    print('Initialized the database')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
        Register a new user
        User defaults to Client user level
    """
    if g.user:
        return redirect(url_for('dashboard'))
    errors = []
    if request.method == 'POST':
        if not request.form['forename']:
            errors.append('You have to enter a forename')
        elif not request.form['surname']:
            errors.append('You have to enter a surname')
        elif not request.form['email']:
            errors.append('You have to enter an email address')
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
                                         3, datetime.datetime.utcnow(),
                                         datetime.datetime.utcnow()])
            db.commit()
            # Send flash message
            flash('You were successfully registered and can login now')
            return redirect(url_for('dashboard'))
    return render_template('register.html', errors=errors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Logs the user in
    """
    if g.user:
        return redirect(url_for('dashboard'))
    errors = []
    if request.method == 'POST':
        user = query_db('''SELECT * FROM users WHERE
            email = ?''', [request.form['email']], one=True)
        if not request.form['email']:
            errors.append('You have to enter an email address')
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            errors.append('You have to enter a valid email address')
        elif not request.form['password']:
            errors.append('You have to enter a password')
        elif user is None or not check_password_hash(user['password'],
                                                     request.form['password']):
            errors.append('Invalid credentials')
        else:
            session['user_id'] = user['user_id']
            session['user_level'] = user['user_level']
            return redirect(url_for('dashboard'))
    return render_template('login.html', errors=errors)


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
    user_id = g.user['user_id']
    if(g.user['user_level'] == 1):
        issues = get_all_issues()
    elif(g.user['user_level'] == 2):
        issues = get_department_issues(user_id)
    elif(g.user['user_level'] == 3):
        issues = get_my_issues(user_id)
    elif(g.user['user_level'] == 4):
        issues = get_assigned_issues(user_id)
    return render_template('dashboard.html', issues=issues)


@app.route('/issues/raise', methods=['GET', 'POST'])
def raise_issue():
    errors = []
    valid = False
    if request.method == 'POST':
        if not request.form['description']:
            errors.append('You have to enter a description')
        if not request.form['priority']:
            errors.append('You have to select a priority')
        if not request.form['department']:
            errors.append('You have to select a department')
        else:
            valid = True

        if valid:
            db = get_db()
            db.execute('''INSERT INTO issues (
              description, priority, department, raised_by, created, modified)
              VALUES (?, ?, ?, ?, ?, ?)''',
                       [request.form['description'],
                        request.form['priority'],
                        request.form['department'],
                        g.user['user_id'],
                        datetime.datetime.utcnow(),
                        datetime.datetime.utcnow()])
            db.commit()

            '''
                Send notification to department admin
            '''
            department_admin = get_department_admin(department_id)
            socketio.send('A new issue was raised on the system',
                          room=department_admin)

            return redirect(url_for('dashboard'))

    priorities = query_db('''SELECT * FROM issue_priorities''')
    departments = query_db('''SELECT * FROM departments''')
    return render_template('raise_issue.html', priorities=priorities,
                           departments=departments, errors=errors)


@app.route('/issues/update/<issue_id>', methods=['GET', 'POST'])
def update_issue(issue_id):
    errors = []
    issue = query_db('''SELECT * FROM issues WHERE issue_id = ?''',
                     [issue_id], one=True)
    if request.method == 'POST':
        if request.form['status'] < 0:
            status = issue['status']
        else:
            status = request.form['status']
        if not request.form['status']:
            errors.append('You have to select a status')
        else:
            db = get_db()
            db.execute('''UPDATE issues SET assigned_to = ?, status = ?
                    WHERE issue_id = ?''',
                       [request.form['assigned_to'], status, issue_id])
            db.commit()

            '''
                When if the issue status was changed, send a notification
                to the person who raised the issue
            '''
            socketio.send('Issue status changed', room=issue['raised_by'])

            return redirect(url_for('dashboard'))

    priorities = query_db('''SELECT * FROM issue_priorities''')
    departments = query_db('''SELECT * FROM departments''')
    reps = query_db('''SELECT * FROM users WHERE user_level = 4''')
    statuses = query_db('''SELECT * FROM issue_status''')
    return render_template('update_issue.html', issue=issue,
                           priorities=priorities, departments=departments,
                           reps=reps, statuses=statuses, errors=errors)


@app.route('/issues/delete/<issue_id>')
def delete_issue(issue_id):
    pass


@app.route('/users')
def users():
    users = query_db('''SELECT usertbl.user_id,usertbl.forename,
        usertbl.surname,usertbl.email,usertbl.created,
        usertbl.user_level,ultbl.user_level_name FROM users as usertbl
        INNER JOIN user_levels AS ultbl
        ON usertbl.user_level = ultbl.user_level_id''')
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
        elif not request.form['surname']:
            errors.append('You have to enter a surname')
        elif not request.form['email']:
            errors.append('You have to enter a email address')
        elif not request.form['user_level']:
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
            return redirect(url_for('users'))
    user_levels = query_db('''SELECT * FROM user_levels''')
    user = query_db('''SELECT * FROM users as usertbl WHERE user_id = ?''',
                    user_id, one=True)
    return render_template('edit_user.html', user=user,
                           user_levels=user_levels, errors=errors)


@app.route('/users/delete/<user_id>')
def delete_user(user_id):
    pass


@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json, broadcast=True)


@socketio.on('join')
def handle_user_join(json):
    '''
        Join a socket.io room
        Called when a user logs in
        The default name of the room is the user's user_id
    '''
    # print json['data']
    # forename = user[1]
    room = json['data']
    join_room(room)
    send('Someone has entered your room.', room=room)


if __name__ == "__main__":
    socketio.run(debug=True)
