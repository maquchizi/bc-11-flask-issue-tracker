# trckr

A simple issue tracking application built with Flask and SQLite

## Specifications

- A user should be able to sign-in / sign-up

- A user should be able to raise an issue and give the following details: Issue description, Priority (low, medium, high), Department (tag the department that is to handle that issue i.e. Operations, Finance, Training, Recruitment, Success, Sales, Marketing)

- Every department has an admin that will be notified once an issue is raised concerning their department. The admin in turn assigns the issue to someone who is supposed to resolve it.

- An admin should be able to mark the issue as resolved (when it is), or mark it as in-progress; and provide comments if any. The person that raised the issue is notified when these changes happen to the issue

- When an issue is not yet, resolved, it is know as an open issue, and once resolved, it’s known as a closed issue

- An admin should be able to see all open and closed issues

## Dependencies

### Back End Dependencies

- [eventlet (0.19.0)](http://eventlet.net/) - Concurrent networking library for Python that allows you to change how you run your code, not how you write it
- [Flask (0.11.1)](http://flask.pocoo.org/) - A microframework for Python based on Werkzeug, Jinja 2 and good intentions
- [Flask-Moment (0.5.1)](https://github.com/miguelgrinberg/Flask-Moment) - Enhances Jinja2 templates with formatting of dates and times using moment.js
- [Flask-SocketIO (2.7.2)](https://github.com/miguelgrinberg/Flask-SocketIO) - Socket.IO integration for Flask applications
- [greenlet (0.4.10)](https://pypi.python.org/pypi/greenlet/0.4.10) - Lightweight in-process concurrent programming
- [itsdangerous (0.24)](https://github.com/pallets/itsdangerous) - Various helpers to pass data to untrusted environments and to get it back safe and sound
- [Jinja2 (2.8)](http://jinja.pocoo.org/) - Jinja2 is a modern and designer-friendly templating language for Python
- [MarkupSafe (0.23)](http://www.pocoo.org/projects/markupsafe/) - Python library for automatic string escaping
- [python-engineio (1.0.3)](https://github.com/miguelgrinberg/python-engineio) - Python implementation of the Engine.IO realtime server
- [python-socketio (1.6.0)](https://github.com/miguelgrinberg/python-socketio) - Python implementation of the Socket.IO realtime server
- [six (1.10.0)](https://pythonhosted.org/six/) - Provides simple utilities for wrapping over differences between Python 2 and Python 3
- [Werkzeug (0.11.11)](http://werkzeug.pocoo.org/) - A WSGI utility library for Python

### Front End Dependencies

- [jQuery (2.2.3)](https://jquery.com/) - Fast, small, and feature-rich JavaScript library
- [Bootstrap (3.3.6)](http://getbootstrap.com/) - A sleek, intuitive, and powerful mobile first front-end framework for faster and easier web development
- [Fontawesome (4.5.0)](http://fontawesome.io/) - Scalable vector icons that can instantly be customized
- [Socket.IO (1.3.6)](http://socket.io/) - Aims to make realtime apps possible in every browser and mobile device, blurring the differences between the different transport mechanisms

## Installation

1. Clone the repository
    ```
    $ git clone git@github.com:maquchizi/bc-11-flask-issue-tracker.git
    ```

2. Create a Virtual Environment for the project
    ```
    $ pip install virtualenv
    $ cd bc-11-flask-issue-tracker
    $ virtualenv venv
    ```

3. Activate Virtual Environment
    ```
    $ . venv/bin/activate
    ```

4. Install requirements
    ```
    $ pip --install requirements.txt
    ```

5. Initialise the sample database
    ```
    $ flask initdb
    ```

6. Run the project
    ```
    $ flask run
    ```
The app should be available at the address: http://127.0.0.1:5000/login

## Usage

Register a new account or log in using the following dummy accounts with pre-populated data:

    super@admin.com / password
    first@client.com / password
    first@support.com / password
