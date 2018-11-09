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
