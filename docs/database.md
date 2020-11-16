# Database Backends

When playing around with our demo app, the default sqlite3 is plenty. Before moving the app to production,
you'll want to use a
["real" database](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DATABASE-ENGINE).

**N.B.** We've deprecated use of Microsoft SQL Server due to lack of support for the django database backend library.
You should use MySQL, including the AWS Aurora Serverless MySQL flavor.

## Running a local database server

We want to be able to do all our development in a local environment (mine is MacOS). Fortunately, this is
feasible with all the common databases.

See `training/settings.py` for an example of alternative database settings for sqlite3 and MySQL
that are configured via environment variables.

```python
if os.environ.get('MYSQL_HOST', None):
    password = os.environ.get('MYSQL_PASSWORD', None)
    # unable to pass None/null value in environment
    if password and password.lower() == 'none':
        password = None
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DB','tsc'),
            'USER': os.environ.get('MYSQL_USER','admin'),
            'PASSWORD': password,
            'HOST': os.environ['MYSQL_HOST'],
            'PORT': os.environ.get('MYSQL_PORT','3306'),
            'OPTIONS': {
                # make mysql 5.6 work sort of right
                'init_command': 'SET default_storage_engine=INNODB,character_set_connection=utf8mb4,'
                                'collation_connection=utf8mb4_unicode_ci,'
                                'sql_mode="STRICT_TRANS_TABLES"'
            }
        }
    }
# otherwise, using local sqlite3:
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }
```

### sqlite3 server

sqlite3 is by definition a local database. It's "just there" on MacOS. You may have version compatibility problems
on RHEL, but if you are to the point of running on RHEL, you should be using a MySQL database.

### MySQL server

You can install a MacOS MySQL server and client using homebrew:

```console
(env) django-training$ brew install mysql
(env) django-training$ mysql.server start
(env) django-training$ mysqladmin -u root create foo
(env) django-training$ mysql -uroot foo
```

## database CLI tools

Following are some examples of how to use your database from the command line for [sqlite3](#sqlite3-client),
or [mysql](#mysql-client). 

### sqlite3 client

For the sqlite3 database, use sqlite3. For example:
```console
(env) django-training$ sqlite3 db.sqlite3 
-- Loading resources from /Users/ac45/.sqliterc
SQLite version 3.24.0 2018-06-04 14:10:15
Enter ".help" for usage hints.
sqlite> .tables
auth_group                    django_migrations           
auth_group_permissions        django_session              
auth_permission               myapp_course                
auth_user                     myapp_courseterm            
auth_user_groups              oauth2_provider_accesstoken 
auth_user_user_permissions    oauth2_provider_application 
django_admin_log              oauth2_provider_grant       
django_content_type           oauth2_provider_refreshtoken
sqlite> .schema --indent myapp_course
CREATE TABLE IF NOT EXISTS "myapp_course"(
  "id" char(32) NOT NULL PRIMARY KEY,
  "effective_start_date" date NULL,
  "effective_end_date" date NULL,
  "last_mod_date" date NOT NULL,
  "school_bulletin_prefix_code" varchar(10) NOT NULL,
  "suffix_two" varchar(2) NOT NULL,
  "subject_area_code" varchar(10) NOT NULL,
  "course_number" varchar(10) NOT NULL,
  "course_identifier" varchar(10) NOT NULL UNIQUE,
  "course_name" varchar(80) NOT NULL,
  "course_description" text NOT NULL,
  "last_mod_user_name" varchar(80) NULL
);
sqlite> select * from myapp_course limit 5;
id                                effective_start_date  effective_end_date  last_mod_user_name  last_mod_date  school_bulletin_prefix_code  suffix_two  subject_area_code  course_number  course_identifier  course_name     course_description
--------------------------------  --------------------  ------------------  ------------------  -------------  ---------------------------  ----------  -----------------  -------------  -----------------  --------------  ------------------
000f21d9c303426394cc0c8b4bfcd859                                            admin               2018-10-07     0                            00          DVSP               87847          BUSI5330K          LEADING PEOPLE  LEADING PEOPLE    
001f1ec8584a4cecba476f8e75b2cac3                                            admin               2018-10-07     B                            00          FINC               24650          FINC8368B          Security Analy  Security Analysis 
0025a7938ae54678bb8598328aecc83f                                            admin               2018-10-07     L                            00          LAW                70101          LAW 8941L          C INTERNATIONA  C INTERNATIONAL CR
002979f72f7042c8a9d56f06c569d8e5                                            admin               2018-10-07     GIU                          00          HNUT               71847          NUTR9011G          DOCTORAL RESEA  DOCTORAL RESEARCH 
002b66ce0506447090b609020d763afb                                            admin               2018-10-07     R                            00          FILM               21435          FILM5010W          CINEMA HIST I:  CINEMA HIST I: BEG
sqlite> 
sqlite> select * from myapp_courseterm where course_id='000f21d9c303426394cc0c8b4bfcd859';
id                                effective_start_date  effective_end_date  last_mod_user_name  last_mod_date  term_identifier  audit_permitted_code  exam_credit_flag  course_id                       
--------------------------------  --------------------  ------------------  ------------------  -------------  ---------------  --------------------  ----------------  --------------------------------
fbee2ba9b4d649a2b4e58d13317d65bc                                            admin               2018-10-07     20181            0                     0                 000f21d9c303426394cc0c8b4bfcd859
sqlite> 
```

### MySQL client

```console
(env) django-training$ mysql -uroot foo
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 12
Server version: 8.0.12 Homebrew

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> select * from myapp_course limit 4;
+----------------------------------+----------------------+--------------------+--------------------+---------------+-----------------------------+------------+-------------------+---------------+-------------------+-------------------------------+-------------------------------+
| id                               | effective_start_date | effective_end_date | last_mod_user_name | last_mod_date | school_bulletin_prefix_code | suffix_two | subject_area_code | course_number | course_identifier | course_name                   | course_description            |
+----------------------------------+----------------------+--------------------+--------------------+---------------+-----------------------------+------------+-------------------+---------------+-------------------+-------------------------------+-------------------------------+
| 001b55e09a60438698c74c856bb840b4 | NULL                 | NULL               | loader             | 2018-08-03    | XCEFK9                      | 00         | ANTB              | 04961         | ANTH3160V         | THE BODY AND SOCIETY          | THE BODY AND SOCIETY          |
| 00fb17bbe4a049a0a27e6939e3e04b62 | NULL                 | NULL               | loader             | 2018-08-03    | B                           | 00         | ACCT              | 73272         | ACCT8122B         | Accounting for Consultants    | Accounting for Consultants    |
| 016659e9e29f49b4b85dd25da0724dbb | NULL                 | NULL               | loader             | 2018-08-03    | B                           | 00         | ACCT              | 73290         | ACCT7022B         | Accounting for Value          | Accounting for Value          |
| 01ca197fc00c4f24a743091b62f1d500 | NULL                 | NULL               | loader             | 2018-08-03    | XCEFK9                      | 00         | AMSB              | 00373         | AMST3704X         | SENIOR RESEARCH ESSAY SEMINAR | SENIOR RESEARCH ESSAY SEMINAR |
+----------------------------------+----------------------+--------------------+--------------------+---------------+-----------------------------+------------+-------------------+---------------+-------------------+-------------------------------+-------------------------------+
4 rows in set (0.00 sec)

mysql> show tables;
+-------------------------------+
| Tables_in_foo                 |
+-------------------------------+
| auth_group                    |
| auth_group_permissions        |
| auth_permission               |
| auth_user                     |
| auth_user_groups              |
| auth_user_user_permissions    |
| django_admin_log              |
| django_content_type           |
| django_migrations             |
| django_session                |
| myapp_course                  |
| myapp_courseterm              |
| myapp_instructor              |
| myapp_instructor_course_terms |
| oauth2_provider_accesstoken   |
| oauth2_provider_application   |
| oauth2_provider_grant         |
| oauth2_provider_refreshtoken  |
| test                          |
+-------------------------------+
19 rows in set (0.00 sec)

mysql> describe myapp_course;
+-----------------------------+-------------+------+-----+---------+-------+
| Field                       | Type        | Null | Key | Default | Extra |
+-----------------------------+-------------+------+-----+---------+-------+
| id                          | char(32)    | NO   | PRI | NULL    |       |
| effective_start_date        | date        | YES  |     | NULL    |       |
| effective_end_date          | date        | YES  |     | NULL    |       |
| last_mod_user_name          | varchar(80) | YES  |     | NULL    |       |
| last_mod_date               | date        | NO   |     | NULL    |       |
| school_bulletin_prefix_code | varchar(10) | NO   |     | NULL    |       |
| suffix_two                  | varchar(2)  | NO   |     | NULL    |       |
| subject_area_code           | varchar(10) | NO   |     | NULL    |       |
| course_number               | varchar(10) | NO   |     | NULL    |       |
| course_identifier           | varchar(10) | NO   | UNI | NULL    |       |
| course_name                 | varchar(80) | NO   |     | NULL    |       |
| course_description          | longtext    | NO   |     | NULL    |       |
+-----------------------------+-------------+------+-----+---------+-------+
12 rows in set (0.01 sec)
```

### Reminder: MYSQL environnment variables

Because we conditionalized the database in settings.py via environment variables, don't forget to set them
in the environment. I did this with a script which I can either source or use to run one-off commands:
```console
(env) django-training$ cat mysql.sh
#!/bin/sh
export MYSQL_HOST=127.0.0.1
export MYSQL_USER=root
export MYSQL_PASSWORD="foo!"
export MYSQL_DB=training
$*
(env) django-training$ source mysql.sh
```

If you forget, you'll end up with sqlite3 as the default database.

<!-- TODO: figure out how to do inter-page links with markdown -->

See ["Set up Run/Debug Configurations for the Project"](building.md#set-up-rundebug-configurations-for-tests),
above, for how to set these environment variables in PyCharm.

### Debugging Migration DDL

If you want to see the SQL DDL statements that are used, use the `./manage.py sqlmigrate` command.

Here's what a sqlite3 migration looks like:

```console
(env) django-training$ ./manage.py sqlmigrate myapp 0004_instructor
```
```sql
BEGIN;
--
-- Create model Instructor
--
CREATE TABLE "myapp_instructor" ("id" char(32) NOT NULL PRIMARY KEY, "effective_start_date" date NULL, "effective_end_date" date NULL, "last_mod_user_name" varchar(80) NULL, "last_mod_date" date NOT NULL, "instr_name" varchar(100) NOT NULL UNIQUE);
CREATE TABLE "myapp_instructor_course_terms" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "instructor_id" char(32) NOT NULL REFERENCES "myapp_instructor" ("id") DEFERRABLE INITIALLY DEFERRED, "courseterm_id" char(32) NOT NULL REFERENCES "myapp_courseterm" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "myapp_instructor_course_terms_instructor_id_courseterm_id_8f50dbb5_uniq" ON "myapp_instructor_course_terms" ("instructor_id", "courseterm_id");
CREATE INDEX "myapp_instructor_course_terms_instructor_id_c1121f18" ON "myapp_instructor_course_terms" ("instructor_id");
CREATE INDEX "myapp_instructor_course_terms_courseterm_id_5af9ffbe" ON "myapp_instructor_course_terms" ("courseterm_id");
COMMIT;
```

And here's what a mysql migration looks like:
```console
(env) django-training$ ./mysql.sh ./manage.py sqlmigrate myapp 0004_instructor
```
```sql
BEGIN;
--
-- Create model Instructor
--
CREATE TABLE `myapp_instructor` (`id` char(32) NOT NULL PRIMARY KEY, `effective_start_date` date NULL, `effective_end_date` date NULL, `last_mod_user_name` varchar(80) NULL, `last_mod_date` date NOT NULL, `instr_name` varchar(100) NOT NULL UNIQUE);
CREATE TABLE `myapp_instructor_course_terms` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `instructor_id` char(32) NOT NULL, `courseterm_id` char(32) NOT NULL);
ALTER TABLE `myapp_instructor_course_terms` ADD CONSTRAINT `myapp_instructor_cou_instructor_id_c1121f18_fk_myapp_ins` FOREIGN KEY (`instructor_id`) REFERENCES `myapp_instructor` (`id`);
ALTER TABLE `myapp_instructor_course_terms` ADD CONSTRAINT `myapp_instructor_cou_courseterm_id_5af9ffbe_fk_myapp_cou` FOREIGN KEY (`courseterm_id`) REFERENCES `myapp_courseterm` (`id`);
ALTER TABLE `myapp_instructor_course_terms` ADD CONSTRAINT `myapp_instructor_course__instructor_id_courseterm_8f50dbb5_uniq` UNIQUE (`instructor_id`, `courseterm_id`);
COMMIT;
```

As you can sess, Django's database layer hides the differences between different backend databases, so you can
focus on what's important.
