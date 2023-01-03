import uuid

from django.core import validators
from django.db import models


class CommonModel(models.Model):
    """
    A common abstract :class:`django.db.models.Model` with common fields for all "real" Models.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="globally unique id (UUID4)",
    )
    """Unique object ID"""
    effective_start_date = models.DateField(
        default=None,
        blank=True,
        null=True,
        help_text="date when this instance becomes valid",
    )
    """Date when this instance becomes valid"""
    effective_end_date = models.DateField(
        default=None,
        blank=True,
        null=True,
        help_text="date when this instance becomes invalid",
    )
    """Date when this instance becomes invalid"""
    last_mod_user_name = models.CharField(
        default=None,
        null=True,
        max_length=80,
        help_text="who last modified this instance",
    )
    """Who last modified this instance"""
    last_mod_date = models.DateField(auto_now=True, help_text="when they modified it")
    """Wheno they modified it"""

    class Meta:
        abstract = True


class Course(CommonModel):
    """
    A course of instruction. e.g. COMSW1002 Computing in Context
    """

    school_bulletin_prefix_code = models.CharField(max_length=10)
    """School bulletin prefix_code"""
    suffix_two = models.CharField(
        max_length=2, help_text="two-character identifier suffix"
    )
    """Two-character inditifier suffix"""
    subject_area_code = models.CharField(max_length=10, help_text="Subject")
    """Subject area code"""
    course_number = models.CharField(
        max_length=10,
        help_text='"Shortcut" identifier (formerly for touch-tone registration)',
    )
    course_identifier = models.CharField(
        max_length=9,
        unique=True,
        help_text="Course identifier (one-character suffix)",
        validators=(
            validators.RegexValidator(regex="[A-Z]{4}[0-9]{4}[A-Z]"),
            validators.MinLengthValidator(limit_value=9),
        ),
    )
    course_name = models.CharField(max_length=80, help_text="Course official title")
    course_description = models.TextField(help_text="Course description")

    class Meta:
        ordering = ["course_number"]

    def __str__(self):
        return "%s,%s,%s,%s" % (
            self.id,
            self.course_number,
            self.course_identifier,
            self.course_name,
        )


class CourseTerm(CommonModel):
    """
    A specific course term (year+semester) instance.
    e.g. 20183COMSW1002
    """

    term_identifier = models.CharField(
        max_length=14,
        unique=True,
        validators=(
            validators.RegexValidator(regex="[0-9]{4}[123][A-Z]{4}[0-9]{4}[A-Z]"),
            validators.MinLengthValidator(limit_value=14),
        ),
    )
    audit_permitted_code = models.PositiveIntegerField(blank=True, default=0)
    exam_credit_flag = models.BooleanField(default=True)
    course = models.ForeignKey(
        "myapp.Course",
        related_name="course_terms",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )

    class Meta:
        ordering = ["term_identifier"]

    def __str__(self):
        return "%s,%s,%s" % (
            self.id,
            self.term_identifier,
            self.course.course_identifier if self.course else "NONE",
        )


class Person(CommonModel):
    """
    A person.
    """

    # 'name' is a reserved word in SQL server so just force the db_column name to be different.
    # TODO: This might be a django-pyodbc-azure bug. Check it.
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "people"

    def __str__(self):
        return "%s,%s" % (self.id, self.name)


class Instructor(CommonModel):
    """
    An instructor.
    """

    person = models.OneToOneField(
        "myapp.Person",
        related_name="instructor",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    course_terms = models.ManyToManyField(
        "myapp.CourseTerm", related_name="instructors"
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return "%s" % (self.id)


class Student(CommonModel):
    """
    A student.
    """

    person = models.OneToOneField(
        "myapp.Person",
        related_name="student",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    #: grades includes all registered classes whether or not they have been completed
    grades = models.ManyToManyField("myapp.Grade", related_name="student")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return "%s" % (self.id)


class Grade(CommonModel):
    """
    A grade for a CourseTerm instance
    """

    person = models.OneToOneField(
        "myapp.Student", on_delete=models.DO_NOTHING, related_name="grade"
    )
    course_term = models.OneToOneField(
        "myapp.CourseTerm", on_delete=models.DO_NOTHING, related_name="grade"
    )
    credits = models.FloatField(help_text="Credits attempted/earned")
    grade_letter = models.CharField(
        max_length=2,
        choices=[(k, k) for k in [None, "A", "B", "C", "D", "F", "P"]],
        default=None,
    )
    grade_value = models.FloatField(
        default=0.0, help_text="grade points (e.g. A is 4.0, F is 0.0)"
    )

    def __str__(self):
        return "%s: %s: %s: %s: %s" % (
            self.id,
            self.person.id,
            self.person.name,
            self.course_term.term_identifier,
            self.grade_letter,
        )


class NonModel(CommonModel):
    """
    Make a concrete model that's not actually got a database under it.
    """

    # TODO: Look at a custom model manager.
    class Meta:
        managed = False

    # id = models.CharField(primary_key=True, max_length=5)
    field1 = models.CharField(max_length=20)
    field2 = models.CharField(max_length=20, default="hi")
    field3 = models.CharField(max_length=10, default="there")

    # def __init__(self, id, field1, field2=None):
    #     self.id = id
    #     self.field1 = field1
    #     self.field2 = field2

    def __str__(self):
        return "%s" % (self.id)
