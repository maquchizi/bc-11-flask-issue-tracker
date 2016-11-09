# trckr

A simple issue tracking application built with Flask and SQLite

## Specifications

- As a user, I should be able to sign-in / sign-up

- As a user, I should be able to raise an issue and give the following details: Issue description, Priority (low, medium, high), Department (tag the department that is to handle that issue i.e. Operations, Finance, Training, Recruitment, Success, Sales, Marketing)

- Every department has an admin that will be notified once an issue is raised concerning their department. The admin in turn assigns the issue to someone who is supposed to resolve it.

- As an admin, I should be able to mark the issue as resolved (when it is), or mark it as in-progress; and provide comments if any. The person that raised the issue is notified when these changes happen to the issue.

- When an issue is not yet, resolved, it is know as an open issue, and once resolved, it’s known as a closed issue.

- As admin, I should be able to see all open and closed issues.

## Dependencies

### Back End Dependencies


Flask (0.11.1)
Flask-Moment (0.5.1)
Flask-SocketIO (2.7.2)
eventlet (0.19.0)
greenlet (0.4.10)
itsdangerous (0.24)
Jinja2 (2.8)
MarkupSafe (0.23)
python-engineio (1.0.3)
python-socketio (1.6.0)
Werkzeug (0.11.11)


### Front End Dependencies

jQuery (2.2.3)
Bootstrap (3.3.6)
Fontawesome (4.5.0)
Socket.io (1.3.6)

## Installation

## Usage
