# Modifying our DJA Project

Let's say we've decided that a change needs to be made to our project:
We found a mistake in the CourseTerm Model: The `term_identifier` is supposed to look like `20183COMSW1002`
which is 14 characters (not 10) and unique. What will this involve:

1. Update the CourseTerm Model
2. Make a new migration
3. Fix the data loader client
4. Fix our test and sample fixtures.

## Update CourseTerm

This is pretty simple:
```diff
diff --git a/myapp/models.py b/myapp/models.py
index 524ae40..49ed0d1 100644
--- a/myapp/models.py
+++ b/myapp/models.py
@@ -49,7 +49,7 @@ class CourseTerm(CommonModel):
     A specific course term (year+semester) instance.
     e.g. 20183COMSW1002
     """
-    term_identifier = models.TextField(max_length=10)
+    term_identifier = models.TextField(max_length=14, unique=True)
     audit_permitted_code = models.PositiveIntegerField(blank=True, default=0)
     exam_credit_flag = models.BooleanField(default=True)
     course = models.ForeignKey('myapp.Course', related_name='course_terms', on_delete=models.CASCADE, null=True,
```

## Make a new migration

1. Make the new migration.
2. Show the current status of migrations.
3. Attempt to migrate (and fail).

```console
(env) django-training$ ./manage.py makemigrations
Migrations for 'myapp':
  myapp/migrations/0003_auto_20181109_1923.py
    - Alter field term_identifier on courseterm
(env) django-training$ ./manage.py showmigrations
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
 [X] 0003_logentry_add_action_flag_choices
auth
 [X] 0001_initial
 [X] 0002_alter_permission_name_max_length
 [X] 0003_alter_user_email_max_length
 [X] 0004_alter_user_username_opts
 [X] 0005_alter_user_last_login_null
 [X] 0006_require_contenttypes_0002
 [X] 0007_alter_validators_add_error_messages
 [X] 0008_alter_user_username_max_length
 [X] 0009_alter_user_last_name_max_length
contenttypes
 [X] 0001_initial
 [X] 0002_remove_content_type_name
myapp
 [X] 0001_initial
 [X] 0002_auto_20181019_1821
 [ ] 0003_auto_20181109_1923
oauth2_provider
 [X] 0001_initial
 [X] 0002_08_updates
 [X] 0003_auto_20160316_1503
 [X] 0004_auto_20160525_1623
 [X] 0005_auto_20170514_1141
 [X] 0006_auto_20171214_2232
sessions
 [X] 0001_initial
```

```python
(env) django-training$ cat myapp/migrations/0003_auto_20181109_1923.py 
# Generated by Django 2.1.3 on 2018-11-09 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20181019_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseterm',
            name='term_identifier',
            field=models.TextField(max_length=14, unique=True),
        ),
    ]

```

```console
(env) django-training$ ./manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, myapp, oauth2_provider, sessions
Running migrations:
  Applying myapp.0003_auto_20181109_1923...Traceback (most recent call last):
  File "/Users/alan/src/django-training/env/lib/python3.6/site-packages/django/db/backends/utils.py", line 85, in _execute
    return self.cursor.execute(sql, params)
  File "/Users/alan/src/django-training/env/lib/python3.6/site-packages/django/db/backends/sqlite3/base.py", line 296, in execute
    return Database.Cursor.execute(self, query, params)
sqlite3.IntegrityError: UNIQUE constraint failed: myapp_courseterm.term_identifier

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ... lots of stack trace here ...
```

## Customizing the migration

This migration doesn't "just work" because our test data has a repeated non-unique field
which we have to fix to be unique. We can describe this pretty easily as "Concatentate old non-unique term_identifier
(e.g. '20181') with course.course_identifier('COMSW1002') to create new term_identifier ('20181COMSW1002')".

One approach would be to manually "fix" the data. But a much cooler approach is to 
develop some migration code, which documents what we fixed and is reproducible and _reversible_. See
[this migration how-to](https://docs.djangoproject.com/en/stable/howto/writing-migrations/#migrations-that-add-unique-fields)
for an example.

Let's try it:

1. Change the migration to alter the `term_identifier` field length but not yet make it unique.
2. Run some custom code to fix the `term_identifier`.
3. Alter it to unique now.

### Write a custom migration script

Start by renaming the auto migration to a name that makes it clear this is a custom migration:
```console
(env) django-training$ mv myapp/migrations/0003_auto_20181109_1923.py myapp/migrations/0003_unique_term_identifier.py
``` 

Then edit it to add the forward and reverse migration functions:
```python
from django.db import migrations, models

def fix_term_id(apps, schema_editor):
    """
    Concatentate old non-unique term_identifier (e.g. '20181') with course.course_identifier('COMSW1002')
    to create new term_identifier ('20181COMSW1002')
    """
    CourseTerm = apps.get_model('myapp', 'CourseTerm')
    for row in CourseTerm.objects.all():
        if row.course:  # there's a parent course relationship
            course_id = row.course.course_identifier
            row.term_identifier = row.term_identifier + course_id
            row.save(update_fields=['term_identifier'])
        else:  # there's no parent course so throw this row away
            row.delete()

def undo_fix_term_id(apps, schema_editor):
    """
    Revert fix_term_id().
    """
    CourseTerm = apps.get_model('myapp', 'CourseTerm')
    for row in CourseTerm.objects.all():
        row.term_identifier = row.term_identifier[:5]
        row.save(update_fields=['term_identifier'])


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20181019_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseterm',
            name='term_identifier',
            field=models.TextField(max_length=14),
        ),
        migrations.RunPython(
            fix_term_id,
            reverse_code=undo_fix_term_id
        ),
        migrations.AlterField(
            model_name='courseterm',
            name='term_identifier',
            field=models.TextField(unique=True),
        ),
    ]
```

### Confirm the current database schema and non-unique content 

Let's first take a look at our current database before the migration (noting that `term_identifier` is `text NOT NULL`).
```console
(env) django-training$ sqlite3 db.sqlite3 
-- Loading resources from /Users/ac45/.sqliterc
SQLite version 3.24.0 2018-06-04 14:10:15
Enter ".help" for usage hints.
sqlite> .schema --indent myapp_courseterm
CREATE TABLE IF NOT EXISTS "myapp_courseterm"(
  "term_identifier" text NOT NULL,
  "id" char(32) NOT NULL PRIMARY KEY,
  "effective_start_date" date NULL,
  "effective_end_date" date NULL,
  "last_mod_user_name" varchar(80) NULL,
  "last_mod_date" date NOT NULL,
  "audit_permitted_code" integer unsigned NOT NULL,
  "exam_credit_flag" bool NOT NULL,
  "course_id" char(32) NULL REFERENCES "myapp_course"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "myapp_courseterm_course_id_edb833e8" ON "myapp_courseterm"(
  "course_id"
);
sqlite> select term_identifier from myapp_courseterm;
term_identifier
---------------
20181          
20191          
20181          
20191          
20181          
20191          
20181          
20191          
20181          
20182          
20181          
20183          
20181          
20191          
20181          
20183          
20181          
20192          
sqlite> 
```

### Run the custom migration

```console
(env) django-training$ ./manage.py showmigrations
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
 [X] 0003_logentry_add_action_flag_choices
auth
 [X] 0001_initial
 [X] 0002_alter_permission_name_max_length
 [X] 0003_alter_user_email_max_length
 [X] 0004_alter_user_username_opts
 [X] 0005_alter_user_last_login_null
 [X] 0006_require_contenttypes_0002
 [X] 0007_alter_validators_add_error_messages
 [X] 0008_alter_user_username_max_length
 [X] 0009_alter_user_last_name_max_length
contenttypes
 [X] 0001_initial
 [X] 0002_remove_content_type_name
myapp
 [X] 0001_initial
 [X] 0002_auto_20181019_1821
 [ ] 0003_unique_term_identifier
oauth2_provider
 [X] 0001_initial
 [X] 0002_08_updates
 [X] 0003_auto_20160316_1503
 [X] 0004_auto_20160525_1623
 [X] 0005_auto_20170514_1141
 [X] 0006_auto_20171214_2232
sessions
 [X] 0001_initial
(env) django-training$ ./manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, myapp, oauth2_provider, sessions
Running migrations:
  Applying myapp.0003_unique_term_identifier... OK
```

### Confirm the custom migration did what was expected

`term_identifier` is now `text NOT NULL UNIQUE` and the values are the concatentation of the
prior `term_identifer` and `course_identifier`.

```console
(env) django-training$ sqlite3 db.sqlite3 
-- Loading resources from /Users/ac45/.sqliterc
SQLite version 3.24.0 2018-06-04 14:10:15
Enter ".help" for usage hints.
sqlite> .schema --indent myapp_courseterm
CREATE TABLE IF NOT EXISTS "myapp_courseterm"(
  "id" char(32) NOT NULL PRIMARY KEY,
  "effective_start_date" date NULL,
  "effective_end_date" date NULL,
  "last_mod_user_name" varchar(80) NULL,
  "last_mod_date" date NOT NULL,
  "audit_permitted_code" integer unsigned NOT NULL,
  "exam_credit_flag" bool NOT NULL,
  "course_id" char(32) NULL REFERENCES "myapp_course"("id") DEFERRABLE INITIALLY DEFERRED,
  "term_identifier" text NOT NULL UNIQUE
);
CREATE INDEX "myapp_courseterm_course_id_edb833e8" ON "myapp_courseterm"(
  "course_id"
);
sqlite> select term_identifier from myapp_courseterm;
term_identifier
---------------
20181ACCT7022B 
20181ACCT8122B 
20181AMST3704X 
20181ANTH3160V 
20181APPH9143E 
20181AUPH1010O 
20181BUEC7255B 
20181CIEN3304E 
20181COMS3102W 
20182AUPH1010O 
20183CIEN3304E 
20183COMS3102W 
20191ACCT7022B 
20191ACCT8122B 
20191AMST3704X 
20191ANTH3160V 
20191APPH9143E 
20192BUEC7255B 
sqlite> 
```

### Reverse the migration

And, here's the coolest part: You can reverse a migration to go back to a previous state, assuming
you included a`reverse_code` migration script:
 
```console
(env) django-training$ ./manage.py migrate myapp 0002_auto_20181019_1821
Operations to perform:
  Target specific migration: 0002_auto_20181019_1821, from myapp
Running migrations:
  Rendering model states... DONE
  Unapplying myapp.0003_unique_term_identifier... OK
```

Make migrations reversible allows you to revert to a prior production release of your code just in case
you discover an issue.

### Do another migration

Finally, as an optional exercise, notice that I inadvertently made `term_identifier = models.TextField`
when it should have been `term_identifier = models.CharField`. Fix that.

## Fix the test fixtures.

Assuming the only data in the sqlite3 database was what's in the `myapp/fixtures/testcases.yaml`, dump
out an updated version of those fixtures.

```console
(env) django-training$ ./manage.py dumpdata --format yaml myapp  >myapp/fixtures/testcases.yaml
```

And look at a diff of a small portion of it:
```diff
 - model: myapp.courseterm
   pk: bca761f7-03f6-4ff5-bbb8-b58467ef3970
   fields: {effective_start_date: null, effective_end_date: null, last_mod_user_name: loader,
-    last_mod_date: 2018-08-03, term_identifier: '20181', audit_permitted_code: 0,
+    last_mod_date: 2018-08-03, term_identifier: 20181BUEC7255B, audit_permitted_code: 0,
     exam_credit_flag: false, course: 046741cd-c700-4752-b57a-e37a948ebc44}
```

Here's a hint if the data is _not_ just the testcases:

1. Reverse the migration as above.
2. Delete the content of the `course` and `courseterm` tables:
3. Load the testcases fixture: `./manage.py loaddata myapp/fixtures/testcases.yaml`
4. Migrate forward.
5. Dump the new testcases fixture: `./manage.py dumpdata --format yaml myapp >myapp/fixtures/testcases.yaml`

Now do the same for the big `courseterm.yaml` fixture. This could take a while! Actually, with DEBUG turned off,
it went pretty quickly:

```console
(env) django-training$ ./manage.py migrate myapp 0002_auto_20181019_1821
Operations to perform:
  Target specific migration: 0002_auto_20181019_1821, from myapp
Running migrations:
  Rendering model states... DONE
  Unapplying myapp.0004_auto_20181109_2050... OK
  Unapplying myapp.0003_unique_term_identifier... OK
(env) django-training$ sqlite3 db.sqlite3 
-- Loading resources from /Users/ac45/.sqliterc
SQLite version 3.24.0 2018-06-04 14:10:15
Enter ".help" for usage hints.
sqlite> delete from myapp_courseterm;
sqlite> delete from myapp_course;
sqlite> ^D
(env) django-training$ ./manage.py loaddata myapp/fixtures/courseterm.yaml 
Installed 8944 object(s) from 1 fixture(s)
(env) django-training$ ./manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, myapp, oauth2_provider, sessions
Running migrations:
  Applying myapp.0003_unique_term_identifier... OK
  Applying myapp.0004_auto_20181109_2050... OK
(env) django-training$ ./manage.py dumpdata --format yaml myapp  >myapp/fixtures/courseterm.yaml 
```

