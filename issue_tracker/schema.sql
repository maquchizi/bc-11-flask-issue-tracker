DROP TABLE if exists users;
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY autoincrement,
    forename VARCHAR NOT NULL,
    surname VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    user_level INTEGER,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE if exists user_levels;
CREATE TABLE user_levels (
    user_level_id INTEGER PRIMARY KEY autoincrement,
    user_level_name VARCHAR NOT NULL
);

DROP TABLE if exists issues;
CREATE TABLE issues (
    issue_id INTEGER PRIMARY KEY autoincrement,
    description TEXT,
    department INTEGER,
    assigned_to INTEGER,
    status INTEGER,
    priority INTEGER,
    raised_by INTEGER,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE if exists issue_status;
CREATE TABLE issue_status (
    issue_status_id INTEGER PRIMARY KEY autoincrement,
    status_name VARCHAR NOT NULL
);

DROP TABLE if exists issue_priorities;
CREATE TABLE issue_priorities (
    priority_id INTEGER PRIMARY KEY autoincrement,
    priority_name VARCHAR
);

DROP TABLE if exists issue_comments;
CREATE TABLE issue_comments (
    comment_id INTEGER PRIMARY KEY autoincrement,
    issue INTEGER NOT NULL,
    commenter INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE if exists departments;
CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY autoincrement,
    department_name VARCHAR NOT NULL,
    department_admin INTEGER,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE if exists notifications;
CREATE TABLE notifications (
    notification_id INTEGER PRIMARY KEY autoincrement,
    origin INTEGER NOT NULL,
    source INTEGER NOT NULL,
    issue INTEGER NOT NULL,
    read BOOLEAN DEFAULT 0,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (user_id, forename, surname, email, password, user_level) VALUES
('1','Super','Admin','super@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','1'),
('2','Operations Department','Admin','operations@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','2'),
('3','Finance Department','Admin','finance@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','2'),
('4','Training Department','Admin','training@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','2'),
('5','Recruitment Department','Admin','recruitment@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','2'),
('6','Sucess Department','Admin','sucess@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','2'),
('7','Sales Department','Admin','sales@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','2'),
('8','Marketing Department','Admin','marketing@admin.com','pbkdf2:sha1:1000$ylsWMEOF$3e6daf9b85463fc42dece581b7bd59242aacb704','2');

INSERT INTO user_levels (user_level_id, user_level_name) VALUES ('1', 'Super Admin'),('2', 'Department Admin'),('3', 'Client'),('4', 'Support Representative');

INSERT INTO issue_priorities (priority_name) VALUES ('Low'),('Medium'),('High');

INSERT INTO issue_status (issue_status_id, status_name) VALUES ('1', 'Open'),('2', 'In-Progress'),('3', 'Closed');

INSERT INTO departments (department_name, department_admin) VALUES ('Operations','2'),('Finance','3'),('Training','4'),('Recruitment','5'),('Success','6'),('Sales','7'),('Marketing','8');
