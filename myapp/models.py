import uuid

from django.db import models

# TODO: Add validations


class CommonModel(models.Model):
    """
    Abstract :py:class:`~django.db.models.Model` with common fields for all "real" Models
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text='globally unique id (UUID4)')
    effective_start_date = models.DateField(default=None, blank=True, null=True,
                                            help_text='date when this model instance becomes valid')
    effective_end_date = models.DateField(default=None, blank=True, null=True,
                                          help_text='date when this model instance becomes invalid')
    last_mod_user_name = models.CharField(default=None, null=True, max_length=80,
                                          help_text='who last modified this instance')
    last_mod_date = models.DateField(auto_now=True,
                                     help_text='when they modified it.')

    class Meta:
        abstract = True


class Course(CommonModel):
    """
    A course of instruction. e.g. COMSW1002 Computing in Context
    """
    school_bulletin_prefix_code = models.CharField(max_length=10)
    suffix_two = models.CharField(max_length=2)
    subject_area_code = models.CharField(max_length=10)
    course_number = models.CharField(max_length=10)
    course_identifier = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=80)
    course_description = models.TextField()

    class Meta:
        ordering = ["course_number"]

    def __str__(self):
        return '%s,%s,%s,%s' % (
            self.id,
            self.course_number,
            self.course_identifier,
            self.course_name
        )


class CourseTerm(CommonModel):
    """
    A specific course term (year+semester) instance.
    e.g. 20183COMSW1002
    """
    term_identifier = models.CharField(max_length=14, unique=True)
    audit_permitted_code = models.PositiveIntegerField(blank=True, default=0)
    exam_credit_flag = models.BooleanField(default=True)
    course = models.ForeignKey('myapp.Course', related_name='course_terms', on_delete=models.CASCADE, null=True,
                               default=None)

    class Meta:
        ordering = ["term_identifier"]

    def __str__(self):
        return '%s,%s,%s' % (self.id, self.term_identifier, self.course.course_identifier if self.course else 'NONE')


class Person(CommonModel):
    """
    A person.
    """
    # 'name' is a reserved word in SQL server so just force the db_column name to be different.
    # TODO: This might be a django-pyodbc-azure bug. Check it.
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'people'

    def __str__(self):
        return '%s,%s' % (self.id, self.name)


class Instructor(CommonModel):
    """
    An instructor.
    """
    person = models.OneToOneField('myapp.Person', related_name='instructor', on_delete=models.CASCADE, null=True,
                                  default=None)
    course_terms = models.ManyToManyField('myapp.CourseTerm', related_name='instructors')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return '%s' % (self.id)
