## sqlite3 or MS SQL Server database

When playing around with our demo app, the default sqlite3 is plenty. Once moving the app to production,
you'll want to use a "real" database, or Microsoft SQL Server ([as the case may be](#sql-server-workarounds)).

See `training/settings.py` for an example of alternative database settings
that are configured via environment variables.

See [Microsoft instructions](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-2017)
to install the SQL Server ODBC client code. In summary:

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install --no-sandbox msodbcsql17 mssql-tools
```

### database CLI tools

Following are some examples of how to use your database from the command line for [sqlite3](#sqlite3)
or [sqlserver](#sqlcmd). 

#### sqlite3

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
sqlite> 
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

#### sqlcmd

Install sqlcmd with homebrew on MacOS:
```bash
$ brew install mssql-tools
```

Use sqlcmd:

```console
django-training$ sqlcmd -S 127.0.0.1,1433 -d foo -U foo -P 'foobar!'
1> select top(4) * from myapp_course;
2> go
id                               effective_start_date effective_end_date last_mod_user_name                                                               last_mod_date    school_bulletin_prefix_code suffix_two subject_area_code course_number course_identifier course_name                                                                      course_description                                                                                                                                                                                                                                              
-------------------------------- -------------------- ------------------ -------------------------------------------------------------------------------- ---------------- --------------------------- ---------- ----------------- ------------- ----------------- -------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
000f21d9c303426394cc0c8b4bfcd859                 NULL               NULL admin                                                                                  2018-10-07 0                           00         DVSP              87847         BUSI5330K         LEADING PEOPLE                                                                   LEADING PEOPLE                                                                                                                                                                                                                                                  
001f1ec8584a4cecba476f8e75b2cac3                 NULL               NULL admin                                                                                  2018-10-07 B                           00         FINC              24650         FINC8368B         Security Analysis                                                                Security Analysis                                                                                                                                                                                                                                               
0025a7938ae54678bb8598328aecc83f                 NULL               NULL admin                                                                                  2018-10-07 L                           00         LAW               70101         LAW 8941L         C INTERNATIONAL CRIMINAL LAW                                                     C INTERNATIONAL CRIMINAL                                                                                                                                                                                                                                        
002979f72f7042c8a9d56f06c569d8e5                 NULL               NULL admin                                                                                  2018-10-07 GIU                         00         HNUT              71847         NUTR9011G         DOCTORAL RESEARCH IN NUTRITION                                                   DOCTORAL RESEARCH IN NUTR                                                                                                                                                                                                                                       

(4 rows affected)
1> select * from myapp_courseterm where course_id='000f21d9c303426394cc0c8b4bfcd859';
2> go
id                               effective_start_date effective_end_date last_mod_user_name                                                               last_mod_date    term_identifier                                                                                                                                                                                                                                                  audit_permitted_code exam_credit_flag course_id                       
-------------------------------- -------------------- ------------------ -------------------------------------------------------------------------------- ---------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -------------------- ---------------- --------------------------------
fbee2ba9b4d649a2b4e58d13317d65bc                 NULL               NULL admin                                                                                  2018-10-07 20181                                                                                                                                                                                                                                                                               0                0 000f21d9c303426394cc0c8b4bfcd859

(1 rows affected)
```


### Advanced Topic: SQL Server Workarounds

Unforuntately, Microsoft SQL Server (and perhaps its [Transact SQL](https://en.wikipedia.org/wiki/Transact-SQL)-based
variants like Sybase) have a number of implementation deficiences and failures to comply with the
[ANSI SQL](https://en.wikipedia.org/wiki/SQL#SQL_standards_documents) standard or the
[popular database engines](https://docs.djangoproject.com/en/stable/topics/migrations/#backend-support)
used by the Django community (sqlite3, mysql, postgresql). Many of these features are used
by [Django Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/) and will cause problems.
Things we've seen so far and have had to work around after prototyping our app using sqlite3:

- Can't ALTER TABLE to change the primary key's type to an AutoField (e.g. AutoField to BigAutoField).
- TextFields can't be unique. Use CharField.
- [The NULL UNIQUE constraint considers multiple rows containing NULL values to violate uniqueness](https://stackoverflow.com/questions/767657/how-do-i-create-a-unique-constraint-that-also-allows-nulls/767702#767702)
  (even though no two NULL values are equal).
  
#### Reminder: DJANGO_SQLSERVER environnment variables

Because we conditionalized the database in settings.py via environment variables, don't forget to set them
in the environment. I did this with a script which I can either source or use to run one-off commands:
```console
(env) django-training$ cat sqlserver.sh
#!/bin/sh
export DJANGO_SQLSERVER=true
export DJANGO_SQLSERVER_DB=foo
export DJANGO_SQLSERVER_USER=foo
export DJANGO_SQLSERVER_PASS="foo!"
export DJANGO_SQLSERVER_HOST=127.0.0.1,1433
$*
(env) django-training$ source sqlserver.sh
```

See ["Set up Run/Debug Configurations for the Project"](#set-up-rundebug-configurations-for-tests), above, for how
to set environment variables in PyCharm. 

#### Fixing django-oauth-toolkit Migrations

The migrations used by DOT break for SQL Server. One approach to fix this is to fork the project and keep a local
copy with edited migrations that work around the problems. Another is to use the standard package but
override the migrations locally. In both cases, we are "fixing" existing migrations; it's just a matter of
how we keep track of them. Let's look at the latter approach.

1. Override the migrations in settings only for SQL Server.
1. Undo the partial oauth2_provider migrations.
1. Copy the current oauth2_provder migrations to 
   [myapp/migration_overrides/oauth2_provider](../myapp/migration_overrides/oauth2_provider)
1. Manually edit the migrations to squash in later changes that SQL Server can't do (like AutoFields).

##### Override migrations for oauth2_provider

We only want to maintain this kludge if using SQL Server, so conditionalize the overridden migration:

```diff
diff --git a/training/settings.py b/training/settings.py
index 327dafd..c7468b0 100644
--- a/training/settings.py
+++ b/training/settings.py
@@ -83,7 +83,7 @@ WSGI_APPLICATION = 'training.wsgi.application'
 # https://docs.djangoproject.com/en/2.1/ref/settings/#databases
 
 if SQLSERVER:
-    # Use the following if testing with MS SQL:
+    # Use the following if using with MS SQL:
     DATABASES = {
         'default': {
             'ENGINE': 'sql_server.pyodbc',
@@ -97,6 +97,12 @@ if SQLSERVER:
             },
         },
     }
+
+    # override the standard migrations because they break due to SQL Server deficiences.
+    MIGRATION_MODULES = {
+        'oauth2_provider': 'myapp.migration_overrides.oauth2_provider',
+    }
+
 else:
     DATABASES = {
         'default': {
```

Undo any partial migrations (0001-4 worked just fine; 0005 is where things start to break down.)

```console
(env) django-training$ ./manage.py migrate oauth2_provider zero
Operations to perform:
  Unapply all migrations: oauth2_provider
Running migrations:
  Rendering model states... DONE
  Unapplying oauth2_provider.0004_auto_20160525_1623... OK
  Unapplying oauth2_provider.0003_auto_20160316_1503... OK
  Unapplying oauth2_provider.0002_08_updates... OK
  Unapplying oauth2_provider.0001_initial... OK
```


Edit the `0001_initial` migration to make the later schema changes happen at the outset. We have no old
`oauth2_provider` data that we care about so this is not a problem.

```diff
--- a/myapp/migration_overrides/oauth2_provider/0001_initial.py
+++ b/myapp/migration_overrides/oauth2_provider/0001_initial.py
@@ -1,4 +1,5 @@
 from django.conf import settings
+import django.db.models.deletion
 from django.db import migrations, models
 
 import oauth2_provider.generators
@@ -7,7 +8,15 @@ from oauth2_provider.settings import oauth2_settings
 
 
 class Migration(migrations.Migration):
-
+    """
+    The following migrations are squashed here:
+    - 0001_initial.py
+    - 0002_08_updates.py
+    - 0003_auto_20160316_1503.py
+    - 0004_auto_20160525_1623.py
+    - 0005_auto_20170514_1141.py
+    - 0006_auto_20171214_2232.py
+    """
     dependencies = [
         migrations.swappable_dependency(settings.AUTH_USER_MODEL)
     ]
@@ -16,14 +25,17 @@ class Migration(migrations.Migration):
         migrations.CreateModel(
             name='Application',
             fields=[
-                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
+                ('id', models.BigAutoField(serialize=False, primary_key=True)),
                 ('client_id', models.CharField(default=oauth2_provider.generators.generate_client_id, unique=True, max_length=100, db_index=True)),
                 ('redirect_uris', models.TextField(help_text='Allowed URIs list, space separated', blank=True)),
                 ('client_type', models.CharField(max_length=32, choices=[('confidential', 'Confidential'), ('public', 'Public')])),
                 ('authorization_grant_type', models.CharField(max_length=32, choices=[('authorization-code', 'Authorization code'), ('implicit', 'Implicit'), ('password', 'Resource owner password-based'), ('client-credentials', 'Client credentials')])),
                 ('client_secret', models.CharField(default=oauth2_provider.generators.generate_client_secret, max_length=255, db_index=True, blank=True)),
                 ('name', models.CharField(max_length=255, blank=True)),
-                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
+                ('user', models.ForeignKey(related_name="oauth2_provider_application", blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
+                ('skip_authorization', models.BooleanField(default=False)),
+                ('created', models.DateTimeField(auto_now_add=True)),
+                ('updated', models.DateTimeField(auto_now=True)),
             ],
             options={
                 'abstract': False,
@@ -33,12 +45,16 @@ class Migration(migrations.Migration):
         migrations.CreateModel(
             name='AccessToken',
             fields=[
-                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
-                ('token', models.CharField(max_length=255, db_index=True)),
+                ('id', models.BigAutoField(serialize=False, primary_key=True)),
+                ('token', models.CharField(unique=True, max_length=255)),
                 ('expires', models.DateTimeField()),
                 ('scope', models.TextField(blank=True)),
-                ('application', models.ForeignKey(to=oauth2_settings.APPLICATION_MODEL, on_delete=models.CASCADE)),
-                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
+                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=oauth2_settings.APPLICATION_MODEL)),
+                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='oauth2_provider_accesstoken', to=settings.AUTH_USER_MODEL)),
+                ('created', models.DateTimeField(auto_now_add=True)),
+                ('updated', models.DateTimeField(auto_now=True)),
+                # Circular reference. Can't add it here.
+                #('source_refresh_token', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=oauth2_settings.REFRESH_TOKEN_MODEL, related_name="refreshed_access_token")),
             ],
             options={
                 'abstract': False,
@@ -48,13 +64,15 @@ class Migration(migrations.Migration):
         migrations.CreateModel(
             name='Grant',
             fields=[
-                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
-                ('code', models.CharField(max_length=255, db_index=True)),
+                ('id', models.BigAutoField(serialize=False, primary_key=True)),
+                ('code', models.CharField(unique=True, max_length=255)),
                 ('expires', models.DateTimeField()),
                 ('redirect_uri', models.CharField(max_length=255)),
                 ('scope', models.TextField(blank=True)),
                 ('application', models.ForeignKey(to=oauth2_settings.APPLICATION_MODEL, on_delete=models.CASCADE)),
-                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
+                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth2_provider_grant', to=settings.AUTH_USER_MODEL)),
+                ('created', models.DateTimeField(auto_now_add=True)),
+                ('updated', models.DateTimeField(auto_now=True)),
             ],
             options={
                 'abstract': False,
@@ -64,15 +82,24 @@ class Migration(migrations.Migration):
         migrations.CreateModel(
             name='RefreshToken',
             fields=[
-                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
-                ('token', models.CharField(max_length=255, db_index=True)),
-                ('access_token', models.OneToOneField(related_name='refresh_token', to=oauth2_settings.ACCESS_TOKEN_MODEL, on_delete=models.CASCADE)),
+                ('id', models.BigAutoField(serialize=False, primary_key=True)),
+                ('token', models.CharField(max_length=255)),
+                ('access_token', models.OneToOneField(blank=True, null=True, related_name="refresh_token", to=oauth2_settings.ACCESS_TOKEN_MODEL, on_delete=models.SET_NULL)),
                 ('application', models.ForeignKey(to=oauth2_settings.APPLICATION_MODEL, on_delete=models.CASCADE)),
-                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
+                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth2_provider_refreshtoken', to=settings.AUTH_USER_MODEL)),
+                ('created', models.DateTimeField(auto_now_add=True)),
+                ('updated', models.DateTimeField(auto_now=True)),
+                ('revoked', models.DateTimeField(null=True)),
             ],
             options={
                 'abstract': False,
                 'swappable': 'OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL',
+                'unique_together': set([("token", "revoked")]),
             },
         ),
+        migrations.AddField(
+            model_name='AccessToken',
+            name='source_refresh_token',
+            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=oauth2_settings.REFRESH_TOKEN_MODEL, related_name="refreshed_access_token"),
+        ),
     ]
```

```console
(env) django-training$ git rm myapp/migration_overrides/oauth2_provider/000[23456]*
rm 'myapp/migration_overrides/oauth2_provider/0002_08_updates.py'
rm 'myapp/migration_overrides/oauth2_provider/0003_auto_20160316_1503.py'
rm 'myapp/migration_overrides/oauth2_provider/0004_auto_20160525_1623.py'
rm 'myapp/migration_overrides/oauth2_provider/0005_auto_20170514_1141.py'
rm 'myapp/migration_overrides/oauth2_provider/0006_auto_20171214_2232.py'
```

##### Workaround mishandling of NULL UNIQUE indexes 

Since sqlserver is
[broken](https://stackoverflow.com/questions/767657/how-do-i-create-a-unique-constraint-that-also-allows-nulls/767702#767702)
we'll want to work around the NULL UNIQUE constraint. Here's the error that is thrown:

```console
('23000', "[23000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Violation of UNIQUE KEY constraint 'UQ__oauth2_p__A1C69CA6C6465E5D'. Cannot insert duplicate key in object 'dbo.oauth2_provider_accesstoken'. The duplicate key value is (<NULL>). (2627) (SQLExecDirectW)")
``` 

Let's start by seeing what SQL DDL is generated by our migration:

```console
(env) django-training$ ./manage.py sqlmigrate oauth2_provider 0001_initial
```

```tsql
BEGIN TRANSACTION
--
-- Create model Application
--
CREATE TABLE [oauth2_provider_application] ([id] bigint IDENTITY (1, 1) NOT NULL PRIMARY KEY, [client_id] nvarchar(100) NOT NULL UNIQUE, [redirect_uris] nvarchar(max) NOT NULL, [client_type] nvarchar(32) NOT NULL, [authorization_grant_type] nvarchar(32) NOT NULL, [client_secret] nvarchar(255) NOT NULL, [name] nvarchar(255) NOT NULL, [user_id] int NULL, [skip_authorization] bit NOT NULL, [created] datetime2 NOT NULL, [updated] datetime2 NOT NULL);
--
-- Create model AccessToken
--
CREATE TABLE [oauth2_provider_accesstoken] ([id] bigint IDENTITY (1, 1) NOT NULL PRIMARY KEY, [token] nvarchar(255) NOT NULL UNIQUE, [expires] datetime2 NOT NULL, [scope] nvarchar(max) NOT NULL, [application_id] bigint NULL, [user_id] int NULL, [created] datetime2 NOT NULL, [updated] datetime2 NOT NULL);
--
-- Create model Grant
--
CREATE TABLE [oauth2_provider_grant] ([id] bigint IDENTITY (1, 1) NOT NULL PRIMARY KEY, [code] nvarchar(255) NOT NULL UNIQUE, [expires] datetime2 NOT NULL, [redirect_uri] nvarchar(255) NOT NULL, [scope] nvarchar(max) NOT NULL, [application_id] bigint NOT NULL, [user_id] int NOT NULL, [created] datetime2 NOT NULL, [updated] datetime2 NOT NULL);
--
-- Create model RefreshToken
--
CREATE TABLE [oauth2_provider_refreshtoken] ([id] bigint IDENTITY (1, 1) NOT NULL PRIMARY KEY, [token] nvarchar(255) NOT NULL, [access_token_id] bigint NULL UNIQUE, [application_id] bigint NOT NULL, [user_id] int NOT NULL, [created] datetime2 NOT NULL, [updated] datetime2 NOT NULL, [revoked] datetime2 NULL);
--
-- Add field source_refresh_token to AccessToken
--
ALTER TABLE [oauth2_provider_accesstoken] ADD [source_refresh_token_id] bigint NULL UNIQUE;
ALTER TABLE [oauth2_provider_application] ADD CONSTRAINT [oauth2_provider_application_user_id_79829054_fk_auth_user_id] FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
CREATE INDEX [oauth2_provider_application_client_secret_53133678] ON [oauth2_provider_application] ([client_secret]);
CREATE INDEX [oauth2_provider_application_user_id_79829054] ON [oauth2_provider_application] ([user_id]);
ALTER TABLE [oauth2_provider_accesstoken] ADD CONSTRAINT [oauth2_provider_accesstoken_application_id_b22886e1_fk_oauth2_provider_application_id] FOREIGN KEY ([application_id]) REFERENCES [oauth2_provider_application] ([id]);
ALTER TABLE [oauth2_provider_accesstoken] ADD CONSTRAINT [oauth2_provider_accesstoken_user_id_6e4c9a65_fk_auth_user_id] FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
CREATE INDEX [oauth2_provider_accesstoken_application_id_b22886e1] ON [oauth2_provider_accesstoken] ([application_id]);
CREATE INDEX [oauth2_provider_accesstoken_user_id_6e4c9a65] ON [oauth2_provider_accesstoken] ([user_id]);
ALTER TABLE [oauth2_provider_grant] ADD CONSTRAINT [oauth2_provider_grant_application_id_81923564_fk_oauth2_provider_application_id] FOREIGN KEY ([application_id]) REFERENCES [oauth2_provider_application] ([id]);
ALTER TABLE [oauth2_provider_grant] ADD CONSTRAINT [oauth2_provider_grant_user_id_e8f62af8_fk_auth_user_id] FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
CREATE INDEX [oauth2_provider_grant_application_id_81923564] ON [oauth2_provider_grant] ([application_id]);
CREATE INDEX [oauth2_provider_grant_user_id_e8f62af8] ON [oauth2_provider_grant] ([user_id]);
ALTER TABLE [oauth2_provider_refreshtoken] ADD CONSTRAINT [oauth2_provider_refreshtoken_access_token_id_775e84e8_fk_oauth2_provider_accesstoken_id] FOREIGN KEY ([access_token_id]) REFERENCES [oauth2_provider_accesstoken] ([id]);
ALTER TABLE [oauth2_provider_refreshtoken] ADD CONSTRAINT [oauth2_provider_refreshtoken_application_id_2d1c311b_fk_oauth2_provider_application_id] FOREIGN KEY ([application_id]) REFERENCES [oauth2_provider_application] ([id]);
ALTER TABLE [oauth2_provider_refreshtoken] ADD CONSTRAINT [oauth2_provider_refreshtoken_user_id_da837fce_fk_auth_user_id] FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
ALTER TABLE [oauth2_provider_refreshtoken] ADD CONSTRAINT [oauth2_provider_refreshtoken_token_revoked_af8a5134_uniq] UNIQUE ([token], [revoked]);
CREATE INDEX [oauth2_provider_refreshtoken_application_id_2d1c311b] ON [oauth2_provider_refreshtoken] ([application_id]);
CREATE INDEX [oauth2_provider_refreshtoken_user_id_da837fce] ON [oauth2_provider_refreshtoken] ([user_id]);
ALTER TABLE [oauth2_provider_accesstoken] ADD CONSTRAINT [oauth2_provider_accesstoken_source_refresh_token_id_e66fbc72_fk_oauth2_provider_refreshtoken_id] FOREIGN KEY ([source_refresh_token_id]) REFERENCES [oauth2_provider_refreshtoken] ([id]);
COMMIT;
```

Let's start by reproducing the error in sqlcmd so that we can confirm we've fixed it. We'll insert two NULL
`source_refresh_token_id`'s:

```console
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope)
2> values('abc','2018-12-01','2018-11-18','2018-11-18','foo')
3> go

(1 rows affected)
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope)
2> values('def','2018-12-01','2018-11-18','2018-11-18','foo')
3> go
Msg 2627, Level 14, State 1, Server ad864306b113, Line 1
Violation of UNIQUE KEY constraint 'UQ__oauth2_p__A1C69CA698B1DABA'. Cannot insert duplicate key in object 'dbo.oauth2_provider_accesstoken'. The duplicate key value is (<NULL>).
The statement has been terminated.
```

Looks like there's not actually an index but maybe the `bigint NULL UNIQUE` column. Let's try:

1. Undo the migration.
1. Change `accesstoken(source_refresh_token_id)` from 'NULL UNIQUE' to 'NULL' in 0001 by making it a `ForeignKey`.
2. Add a UNIQUE INDEX to enforce uniqueness to get back the `OneToOneField` behavior.

```console
(env) django-training$ ./sqlserver.sh ./manage.py migrate oauth2_provider zero
Operations to perform:
  Unapply all migrations: oauth2_provider
Running migrations:
  Rendering model states... DONE
  Unapplying oauth2_provider.0001_initial... OK
```

We'll add some SQL to remove the NULL UNIQUE from the column attributes and
instead implement proper NULL UNIQUE enforcement by manually adding a "CREATE UNIQUE INDEX ... WHERE ... IS NOT NULL".

Due to the various referential intregrity constraints in the models, we have to do a bit of extra work:
1. Dummy up an Application.
1. Count on a User already existing (via `./manage.py createsuperuser`)
1. Dummy up a RefreshToken.
1. Add a couple of AccessTokens that have NULL `source_refresh_token`.
1. Try to add an AccessToken that references a non-existant RefreshToken id (1).
1. Add an AccessToken that references an existing RefreshToken id (4).
1. Try to add it again and get a duplicate key error.
1. Confirm that we have multiple NULL `source_refresh_token` id's as well as a unique value (4).
1. Drop the unique index to prove we can screw things up with a duplicate.
1. Finally, drop and recreate the database so we have a clean starting point to test our fix.


```console
1> SET QUOTED_IDENTIFIER ON
2> go
1> CREATE UNIQUE INDEX [oauth2_provider_accesstoken_source_refresh_token] ON [oauth2_provider_accesstoken][(source_refresh_token_id)] where [source_refresh_token_id] IS NOT NULL;
2> go
1> insert into oauth2_provider_application(client_id,redirect_uris,client_type,authorization_grant_type,client_secret,name,skip_authorization,created,updated)
2> values('foofoo','http://go.away','foo','foo','secret','name',1,'2018-11-18','2018-11-18')
3> go

(1 rows affected)
1> insert into oauth2_provider_refreshtoken(token,created,updated,application_id,user_id)
2> values('ghi','2018-11-18','2018-11-18',1,1)
3> go

(1 rows affected)
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope)
2> values('123','2018-12-01','2018-11-18','2018-11-18','foo')
3> go

(1 rows affected)
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope)
2> values('321','2018-12-01','2018-11-18','2018-11-18','foo')
3> go

(1 rows affected)
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope,source_refresh_token_id)
2> values('999','2018-12-01','2018-11-18','2018-11-18','foo',1)
3> go
Msg 547, Level 16, State 1, Server ad864306b113, Line 1
The INSERT statement conflicted with the FOREIGN KEY constraint "oauth2_provider_accesstoken_source_refresh_token_id_e66fbc72_fk_oauth2_provider_refreshtoken_id". The conflict occurred in database "proposal", table "dbo.oauth2_provider_refreshtoken", column 'id'.
The statement has been terminated.
1> select id from oauth2_provider_refreshtoken;
2> go
id                  
--------------------
                   4

(1 rows affected)
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope,source_refresh_token_id)
2> values('1010','2018-12-01','2018-11-18','2018-11-18','foo',4)
3> go

(1 rows affected)
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope,source_refresh_token_id)
2> values('111','2018-12-01','2018-11-18','2018-11-18','foo',4)
3> go
Msg 2601, Level 14, State 1, Server ad864306b113, Line 1
Cannot insert duplicate key row in object 'dbo.oauth2_provider_accesstoken' with unique index 'oauth2_provider_accesstoken_source_refresh_token'. The duplicate key value is (4).
The statement has been terminated.
1> select id,token,source_refresh_token_id from oauth2_provider_accesstoken
2> go
id                   token                                                                                                                                                                                                                                                           source_refresh_token_id
-------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -----------------------
                   1 abc                                                                                                                                                                                                                                                                                NULL
                   2 def                                                                                                                                                                                                                                                                                NULL
                   3 ghi                                                                                                                                                                                                                                                                                NULL
                   6 123                                                                                                                                                                                                                                                                                NULL
                   7 321                                                                                                                                                                                                                                                                                NULL
                   9 999                                                                                                                                                                                                                                                                                   4

(6 rows affected)
1> drop index oauth2_provider_accesstoken_source_refresh_token on oauth2_provider_accesstoken
2> go
1> insert into oauth2_provider_accesstoken(token,expires,created,updated,scope,source_refresh_token_id)
2> values('111','2018-12-01','2018-11-18','2018-11-18','foo',4)
3> go

(1 rows affected)
1> select id,token,source_refresh_token_id from oauth2_provider_accesstoken
2> go
id                   token                                                                                                                                                                                                                                                           source_refresh_token_id
-------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -----------------------
                   1 abc                                                                                                                                                                                                                                                                                NULL
                   2 def                                                                                                                                                                                                                                                                                NULL
                   3 ghi                                                                                                                                                                                                                                                                                NULL
                   6 123                                                                                                                                                                                                                                                                                NULL
                   7 321                                                                                                                                                                                                                                                                                NULL
                   9 999                                                                                                                                                                                                                                                                                   4
                  11 111                                                                                                                                                                                                                                                                                   4

(7 rows affected)
1> ^C
(env) django-training$ sqlcmd -S 127.0.0.1,1433  -U foo -P 'foo!' -Q "drop database foo"
(env) django-training$ sqlcmd -S 127.0.0.1,1433  -U foo -P 'foo!' -Q "create database foo"
```

Adding that Raw SQL to the migration was pretty easy.

```diff
--- a/myapp/migration_overrides/oauth2_provider/0001_initial.py
+++ b/myapp/migration_overrides/oauth2_provider/0001_initial.py
@@ -9,14 +9,32 @@ from oauth2_provider.settings import oauth2_settings
 
 class Migration(migrations.Migration):
     """
-    The following migrations are squashed here:
+    This migration is a workaround for django-pyodbc-azure and/or sqlserver deficiencies that cause the
+    standard oauth2_provider migrations to fail, specifically:
+    - changing AutoField to BigAutoField is not implemented
+    - sqlserver botches indexing UNIQUE NULL fields, acting as if two NULLs equal each other.
+
+    To use this, override the standard migrations in settings:
+    .. code-block:: python
+
+        MIGRATION_MODULES = {
+        'oauth2_provider': 'myapp.migration_overrides.oauth2_provider',
+        }
+
+    The following :py:mod:`oauth2_provider.migrations` are squashed here:
     - 0001_initial.py
     - 0002_08_updates.py
     - 0003_auto_20160316_1503.py
     - 0004_auto_20160525_1623.py
     - 0005_auto_20170514_1141.py
     - 0006_auto_20171214_2232.py
+
+    And SQL to work around the UNIQUE NULL issue is added.
     """
+    # TODO: Any future migrations will need to be copied here and the dependencies corrected until such time as
+    #       the django-oauth-toolkit project gets around to squashing migrations with a major release.
+    #       OR, fix django-pyodbc-azure.
+
     dependencies = [
         migrations.swappable_dependency(settings.AUTH_USER_MODEL)
     ]
@@ -97,9 +115,34 @@ class Migration(migrations.Migration):
                 'unique_together': set([("token", "revoked")]),
             },
         ),
+        # trying to change this to ForeignKey triggers a new migration so either:
+        # - add RunSQL to undo the NULL UNIQUE to just NULL and add a UNIQUE index
+        # - use a fixed version of django-pyodbc-azure that does that.
         migrations.AddField(
             model_name='AccessToken',
             name='source_refresh_token',
             field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=oauth2_settings.REFRESH_TOKEN_MODEL, related_name="refreshed_access_token"),
         ),
+        migrations.RunSQL(
+            sql='ALTER TABLE [oauth2_provider_refreshtoken] ALTER COLUMN [access_token_id] bigint NULL',
+            reverse_sql='ALTER TABLE [oauth2_provider_refreshtoken] ALTER COLUMN [access_token_id] bigint NULL UNIQUE'
+        ),
+        migrations.RunSQL(
+            sql='CREATE UNIQUE INDEX [oauth2_provider_refreshtoken_access_token] '
+                'ON [oauth2_provider_refreshtoken]([access_token_id]) '
+                'where [access_token_id] IS NOT NULL',
+            reverse_sql='DROP INDEX [oauth2_provider_refreshtoken_access_token] '
+                        'on [oauth2_provider_refreshtoken]',
+        ),
+        migrations.RunSQL(
+            sql='ALTER TABLE [oauth2_provider_accesstoken] ALTER COLUMN [source_refresh_token_id] bigint NULL',
+            reverse_sql='ALTER TABLE [oauth2_provider_accesstoken] ALTER COLUMN [source_refresh_token_id] bigint NULL UNIQUE'
+        ),
+        migrations.RunSQL(
+            sql='CREATE UNIQUE INDEX [oauth2_provider_accesstoken_source_refresh_token] '
+                'ON [oauth2_provider_accesstoken]([source_refresh_token_id]) '
+                'where [source_refresh_token_id] IS NOT NULL',
+            reverse_sql='DROP INDEX [oauth2_provider_accesstoken_source_refresh_token] '
+                        'on [oauth2_provider_accesstoken]',
+        ),
     ]
```

Here's the difference for the resulting DDL:
```diff
21a22,37
> --
> -- Raw SQL operation
> --
> ALTER TABLE [oauth2_provider_refreshtoken] ALTER COLUMN [access_token_id] bigint NULL;
> --
> -- Raw SQL operation
> --
> CREATE UNIQUE INDEX [oauth2_provider_refreshtoken_access_token] ON [oauth2_provider_refreshtoken]([access_token_id]) where [access_token_id] IS NOT NULL;
> --
> -- Raw SQL operation
> --
> ALTER TABLE [oauth2_provider_accesstoken] ALTER COLUMN [source_refresh_token_id] bigint NULL;
> --
> -- Raw SQL operation
> --
> CREATE UNIQUE INDEX [oauth2_provider_accesstoken_source_refresh_token] ON [oauth2_provider_accesstoken]([source_refresh_token_id]) where [source_refresh_token_id] IS NOT NULL;```
```

And that does it!

Meanwhile, we'll go ahead and research the `django-pyodbc-azure` package and see if there's a fix: 
[#188](https://github.com/michiya/django-pyodbc-azure/pull/188) -- but the AutoField error is still present
so we need to continue using this overridden migration until that gets fixed or DOT squashes the migrations.

---

#### TextField can't be unique

In fact our [update of CourseTerm](#update-courseterm) breaks with SQL Server with this error:

```console
pyodbc.ProgrammingError: ('42000', "[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Column 'term_identifier' in table 'myapp_courseterm' is of a type that is invalid for use as a key column in an index. (1919) (SQLExecDirectW)")
```

In this case, it was probably because we inadvertently used a `TextField` instead of `CharField` in the original model.

Let's fix that:

1. Make the TextField to CharField change happen before making it unique in our manual migration
   (`myapp/migrations/0003_unique_term_identifier.py`).
2. Remove the 0004 automigration that tries to make the TextField a unique index since we've already done it. Make
   sure to fix the dependency for any following migration to skip the removed one.
3. Migrate.

(Note that I also had to specify the CharField length a second time -- that shouldn't be necessary -- probably
due to a bug in the `django-pyodbc-azure` package which passed `None` for the field length to the SQL Server!) 

```diff
diff --git a/myapp/migrations/0003_unique_term_identifier.py b/myapp/migrations/0003_unique_term_identifier.py
index 1e0d26d..04dcda7 100644
--- a/myapp/migrations/0003_unique_term_identifier.py
+++ b/myapp/migrations/0003_unique_term_identifier.py
@@ -34,7 +34,7 @@ class Migration(migrations.Migration):
         migrations.AlterField(
             model_name='courseterm',
             name='term_identifier',
-            field=models.TextField(max_length=14),
+            field=models.CharField(max_length=14),
         ),
         migrations.RunPython(
             fix_term_id,
@@ -43,6 +43,6 @@ class Migration(migrations.Migration):
         migrations.AlterField(
             model_name='courseterm',
             name='term_identifier',
-            field=models.TextField(unique=True),
+            field=models.CharField(max_length=14, unique=True),
         ),
     ]
diff --git a/myapp/migrations/0005_instructor.py b/myapp/migrations/0005_instructor.py
index 93e7de9..ff41366 100644
--- a/myapp/migrations/0005_instructor.py
+++ b/myapp/migrations/0005_instructor.py
@@ -7,7 +7,7 @@ import uuid
 class Migration(migrations.Migration):
 
     dependencies = [
-        ('myapp', '0004_auto_20181109_2050'),
+        ('myapp', '0003_unique_term_identifier'),
     ]
 
     operations = [     
```

```console
(env) django-training$ git rm myapp/migrations/0004_auto_20181109_2050.py 
rm 'myapp/migrations/0004_auto_20181109_2050.py'
(env) django-training$ ./manage.py showmigrations myapp
myapp
 [X] 0001_initial
 [X] 0002_auto_20181019_1821
 [ ] 0003_unique_term_identifier
 [ ] 0005_instructor
 [ ] 0006_auto_20181116_2058
(env) django-training$ ./manage.py migrate myapp
```

The above still now blows up on 0005 but at least 0003 worked:
```console
(env) django-training$ ./manage.py showmigrations myapp
myapp
 [X] 0001_initial
 [X] 0002_auto_20181019_1821
 [X] 0003_unique_term_identifier
 [ ] 0005_instructor
 [ ] 0006_auto_20181116_2058
(env) django-training$ ./manage.py migrate myapp
```
 
Let's move on to the next error:

#### "name" can't be a field name

When we tried the `0005_instructor` migration, this error happened:
```console
django.db.utils.ProgrammingError: ('42000', "[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Column 'name' in table 'myapp_instructor' is of a type that is invalid for use as a key column in an index. (1919) (SQLExecDirectW)")
```
and then (after fixing the above, described below) this error, which is the same problem as earlier: TextField can't be unique:
```console
pyodbc.ProgrammingError: ('42000', "[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Column 'instr_name' in table 'myapp_instructor' is of a type that is invalid for use as a key column in an index. (1919) (SQLExecDirectW)")
```

So I guess we need to fix the model not to use `name` as a field name. I like `name` and don't want to screw up
my Model, serializer, views and so on, so let's use the `db_column` field to fix it.

1. Remove the existing instructor migrations.
2. Fix the model to specify a `db_column` name.
3. Make new migrations for instructor
4. Migrate.

```console
(env) django-training$ git rm myapp/migrations/0005_instructor.py 
rm 'myapp/migrations/0005_instructor.py'
(env) django-training$ git rm myapp/migrations/0006_auto_20181116_2058.py 
rm 'myapp/migrations/0006_auto_20181116_2058.py'
(env) django-training$ ./manage.py showmigrations myapp
myapp
 [X] 0001_initial
 [X] 0002_auto_20181019_1821
 [X] 0003_unique_term_identifier
(env) django-training$ ./manage.py makemigrations myapp
Migrations for 'myapp':
  myapp/migrations/0004_instructor.py
    - Create model Instructor
(env) django-training$ ./manage.py showmigrations myapp
myapp
 [X] 0001_initial
 [X] 0002_auto_20181019_1821
 [X] 0003_unique_term_identifier
 [ ] 0004_instructor
(env) django-training$ ./manage.py migrate myapp
Operations to perform:
  Apply all migrations: myapp
Running migrations:
  Applying myapp.0004_instructor... OK
(env) django-training$ ./manage.py loaddata myapp/fixtures/testcases.yaml
Installed 38 object(s) from 1 fixture(s)  
```

Here's what we fixed in the Instructor Model:
```diff
diff --git a/myapp/models.py b/myapp/models.py
index dbb13e3..aad33d1 100644
--- a/myapp/models.py
+++ b/myapp/models.py
@@ -66,7 +66,9 @@ class Instructor(CommonModel):
     """
     An instructor.
     """
-    name = models.TextField(max_length=100, unique=True)
+    # 'name' is a reserved word in SQL server so just force the db_column name to be different.
+    # TODO: This might be a django-pyodbc-azure bug. Check it.
+    name = models.CharField(db_column='instr_name', max_length=100, unique=True)
     course_terms = models.ManyToManyField('myapp.CourseTerm', related_name='instructors')
 
     class Meta:
```

### Squashing Migrations

If you don't have data in the database that you care about, an easier approach is to
[squash migrations](https://docs.djangoproject.com/en/2.1/topics/migrations/#migration-squashing) or just
remove all the migration scripts and re-do `./manage.py makemigrations`.


### Debugging Migration DDL

If you want to see the SQL DDL statements that are used, use the `./manage.py sqlmigrate` command.

```console
(env) django-training$ ./manage.py sqlmigrate myapp 0004_instructor
```

```sql
BEGIN TRANSACTION
--
-- Create model Instructor
--
CREATE TABLE [myapp_instructor] ([id] char(32) NOT NULL PRIMARY KEY, [effective_start_date] date NULL, [effective_end_date] date NULL, [last_mod_user_name] nvarchar(80) NULL, [last_mod_date] date NOT NULL, [instr_name] nvarchar(100) NOT NULL UNIQUE);
CREATE TABLE [myapp_instructor_course_terms] ([id] int IDENTITY (1, 1) NOT NULL PRIMARY KEY, [instructor_id] char(32) NOT NULL, [courseterm_id] char(32) NOT NULL);
ALTER TABLE [myapp_instructor_course_terms] ADD CONSTRAINT [myapp_instructor_course_terms_instructor_id_c1121f18_fk_myapp_instructor_id] FOREIGN KEY ([instructor_id]) REFERENCES [myapp_instructor] ([id]);
ALTER TABLE [myapp_instructor_course_terms] ADD CONSTRAINT [myapp_instructor_course_terms_courseterm_id_5af9ffbe_fk_myapp_courseterm_id] FOREIGN KEY ([courseterm_id]) REFERENCES [myapp_courseterm] ([id]);
ALTER TABLE [myapp_instructor_course_terms] ADD CONSTRAINT [myapp_instructor_course_terms_instructor_id_courseterm_id_8f50dbb5_uniq] UNIQUE ([instructor_id], [courseterm_id]);
CREATE INDEX [myapp_instructor_course_terms_instructor_id_c1121f18] ON [myapp_instructor_course_terms] ([instructor_id]);
CREATE INDEX [myapp_instructor_course_terms_courseterm_id_5af9ffbe] ON [myapp_instructor_course_terms] ([courseterm_id]);
COMMIT;
```

It's kind of interesting to compare this to what's done for sqlite3:
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
