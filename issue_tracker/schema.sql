drop table if exists users;
create table users (
    user_id integer primary key autoincrement,
    forename varchar NOT NULL,
    surname varchar NOT NULL,
    email varchar NOT NULL,
    password varchar NOT NULL,
    user_level integer,
    created datetime DEFAULT CURRENT_TIMESTAMP,
    modified datetime DEFAULT CURRENT_TIMESTAMP
);

drop table if exists user_levels;
create table user_levels (
    user_level_id integer primary key autoincrement,
    user_level_name varchar NOT NULL
);

drop table if exists issues;
create table issues (
    issue_id integer primary key autoincrement,
    description text,
    department integer,
    assigned_to integer,
    status integer,
    raised_by integer,
    created datetime DEFAULT CURRENT_TIMESTAMP,
    modified datetime DEFAULT CURRENT_TIMESTAMP
);

drop table if exists issue_status;
create table issue_status (
    issue_status_id integer primary key autoincrement,
    status_name varchar NOT NULL
);

drop table if exists issue_comments;
create table issue_comments (
    comment_id integer primary key autoincrement,
    issue integer NOT NULL,
    commenter integer NOT NULL,
    comment text NOT NULL,
    created datetime DEFAULT CURRENT_TIMESTAMP,
    modified datetime DEFAULT CURRENT_TIMESTAMP
);

drop table if exists departments;
create table departments (
    department_id integer primary key autoincrement,
    department_name varchar NOT NULL,
    department_admin integer NOT NULL,
    created datetime DEFAULT CURRENT_TIMESTAMP,
    modified datetime DEFAULT CURRENT_TIMESTAMP
);

drop table if exists notifications;
create table notifications (
    notification_id integer primary key autoincrement,
    origin integer NOT NULL,
    source integer NOT NULL,
    issue integer NOT NULL,
    read boolean DEFAULT 0,
    created datetime DEFAULT CURRENT_TIMESTAMP,
    modified datetime DEFAULT CURRENT_TIMESTAMP
);
