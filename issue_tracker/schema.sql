drop table if exists users;
create table users (
    user_id integer primary key autoincrement,
    forename varchar not null,
    surname varchar not null,
    email varchar not null,
    password varchar not null,
    created datetime not null,
    modified timestamp
);

drop table if exists user_levels;
create table user_levels (
    user_level_id integer primary key autoincrement,
    user_level_name varchar not null
);

drop table if exists issues;
create table issues (
    issue_id integer primary key autoincrement,
    description text,
    department integer,
    assigned_to integer,
    status integer,
    raised_by integer,
    created datetime not null,
    modified timestamp
);

drop table if exists issue_status;
create table issue_status (
    issue_status_id integer primary key autoincrement,
    status_name varchar not null
);

drop table if exists issue_comments;
create table issue_comments (
    comment_id integer primary key autoincrement,
    issue integer not null,
    commenter integer not null,
    comment text not null,
    created datetime,
    modified timestamp
);

drop table if exists departments;
create table departments (
    department_id integer primary key autoincrement,
    department_name varchar not null,
    department_admin integer not null,
    created datetime,
    modified timestamp
);

drop table if exists notifications;
create table notifications (
    notification_id integer primary key autoincrement,
    origin integer not null,
    source integer not null,
    issue integer not null,
    read boolean default 0,
    created datetime,
    modified timestamp
);
