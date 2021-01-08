CREATE TABLE IF NOT EXISTS USERROLE(
  id serial primary key,
  first_name varchar(30) not null,
  last_name varchar(30) not null,
  email varchar(350) not null unique,
  password_hash varchar(100) not null,
  is_admin boolean not null default false,
  is_activated boolean not null default false,
  is_publisher boolean not null default false,
  reg_date timestamp (6) with time zone not null default 'now',
  update_date timestamp (6) with time zone not null default 'now',
  constraint proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

CREATE TABLE IF NOT EXISTS EXAM (
  id serial primary key,
  publisher_id integer references USERROLE(id) ON DELETE CASCADE,
  title varchar(250) not null,
  code varchar(10) not null unique,
  type integer default 0,
  is_active boolean not null default true,
  upload_time timestamp (6) with time zone not null default 'now',
  update_time timestamp (6) with time zone not null default 'now'
);

CREATE TABLE IF NOT EXISTS ANSWERSHEET (
  id serial primary key,
  USERROLE_id integer references USERROLE (id) ON DELETE CASCADE,
  exam_id integer references EXAM (id) ON DELETE SET NULL,
  answers text default '{}',
  upload_time timestamp (6) with time zone not null default 'now'
);

CREATE TABLE IF NOT EXISTS EXAMFIELD (
  id serial primary key,
  exam_id integer references EXAM (id) ON DELETE CASCADE,
  field_name varchar(50) not null,
  num_of_question integer default 0,
  answer_list text not null default '{}'
);

CREATE TABLE IF NOT EXISTS RESULT (
  id serial primary key,
  USERROLE_id integer references USERROLE (id) ON DELETE SET NULL,
  exam_id integer references EXAM (id) ON DELETE NO ACTION,
  sheet_id integer references ANSWERSHEET (id) ON DELETE CASCADE,
  corrects integer not null default 0,
  wrongs integer not null default 0,
  unaswereds integer not null default  0,
  net float not null default 0 CHECK (net <= corrects),
  score float null default 0,
  upload_time timestamp (6) with time zone not null default 'now',
  is_active boolean not null default true
);

CREATE TABLE IF NOT EXISTS FIELDRESULT(
  id serial primary key,
  examfield_id integer references EXAMFIELD(id) ON DELETE SET NULL,
  result_id integer references RESULT(id) ON DELETE SET NULL,
  corrects text not null default '{}',
  wrongs text not null default '{}',
  unanswereds text not null default '{}'
);

CREATE TABLE IF NOT EXISTS roles(
   role_id serial PRIMARY KEY,
   role_name VARCHAR (255) UNIQUE NOT NULL
);
