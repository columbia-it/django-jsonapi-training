from datetime import date, datetime

from django.conf import settings
from django.db.utils import IntegrityError
from django.test import TestCase

from myapp.models import Course, CourseTerm, Instructor, Person


class CourseTestCase(TestCase):

    def setUp(self):
        c1 = Course.objects.create(
            school_bulletin_prefix_code='123',
            suffix_two='11',
            subject_area_code='A101',
            course_number='123',
            course_identifier='ABC123',
            course_name='Corp. Finance',
            course_description='bla bla bla 123',
            last_mod_user_name='Fred Gary')
        c1.save()

        c2 = Course.objects.create(
            school_bulletin_prefix_code='888',
            suffix_two='22',
            subject_area_code='A102',
            course_number='456',
            course_identifier='XYZ321',
            course_name='Data Science III',
            course_description='bla bla bla 456',
            last_mod_user_name='Tom Smith')
        c2.save()

        CourseTerm.objects.create(
            term_identifier='term_id_1',
            audit_permitted_code=123,
            exam_credit_flag=True,
            last_mod_user_name='Fred Gary',
            effective_start_date=datetime.now(),
            effective_end_date=date(2019, 1, 31),
            course=c1
        ).save()

        CourseTerm.objects.create(
            term_identifier='term_id_2',
            audit_permitted_code=222,
            exam_credit_flag=False,
            last_mod_user_name='Tom Frank',
            effective_start_date=datetime.now(),
            effective_end_date=date(2019, 2, 28),
            course=c1
        ).save()

        CourseTerm.objects.create(
            term_identifier='term_id_21',
            audit_permitted_code=321,
            exam_credit_flag=True,
            last_mod_user_name='Fred Gary',
            effective_start_date=datetime.now(),
            effective_end_date=date(2020, 1, 31),
            course=c2
        ).save()

        CourseTerm.objects.create(
            term_identifier='term_id_22',
            audit_permitted_code=422,
            exam_credit_flag=False,
            last_mod_user_name='Tom Frank',
            last_mod_date=datetime.now(),
            effective_start_date=datetime.now(),
            effective_end_date=date(2020, 12, 28),
            course=c2
        ).save()

    def test_str(self):
        courses = Course.objects.all()
        c = courses.get(course_identifier='ABC123')
        self.assertEqual(c.course_identifier, 'ABC123')

    def test_date(self):
        courses = Course.objects.all()
        c = courses.get(course_identifier='ABC123')
        self.assertEqual(c.last_mod_date, date.today())

    def test_num(self):
        cs = Course.objects.all()
        self.assertEqual(2, cs.count())

        terms = CourseTerm.objects.all()
        self.assertEqual(4, terms.count())

        # field look up
        ts = CourseTerm.objects.filter(course__course_identifier='123ABC')
        self.assertEqual(0, ts.count())

        ts = CourseTerm.objects.filter(course__course_identifier='ABC123')
        self.assertEqual(2, ts.count())

        ts = CourseTerm.objects.filter(last_mod_user_name__startswith='Tom')
        self.assertEqual(2, ts.count())

        cs = Course.objects.filter(course_terms__last_mod_user_name__startswith='Tom')
        self.assertEqual(2, cs.count())

    def test_dup_fail(self):
        with self.assertRaises(IntegrityError):
            c1 = Course.objects.create(
                school_bulletin_prefix_code='123',
                suffix_two='11',
                subject_area_code='A101',
                course_number='123',
                course_identifier='ABC123',
                course_name='Corp. Finance',
                course_description='bla bla bla 123',
                last_mod_user_name='Fred Gary')
            c1.save()


class ManyToManyTestCase(TestCase):
    """
    do some performance tests on large numbers of many-to-many relationships
    """
    def setUp(self):
        # make 50 CourseTerms
        self.courseterms = []
        for i in range(50):
            t = CourseTerm.objects.create(term_identifier="term {}".format(i))
            t.save()
            self.courseterms.append(t)
        # make 50 instructors (one-to-one with people)
        self.people = []
        self.instructors = []
        for i in range(100):
            p = Person.objects.create(name="Person {}".format(i))
            p.save()
            self.people.append(p)
            i = Instructor.objects.create(person=p)
            # each instructor teaches all courseterms
            i.course_terms.set(self.courseterms)
            self.instructors.append(i)
            i.save()

    def test_prefetch_related(self):
        """
        Try to understand why prefetch_related does a giant WHERE IN (...) which doesn't scale well as it requires
        a parameter for each **row** of the intermediate myapp_instructor_course_terms table.  This breaks
        databases like MS SQLServer that has a limit of 2100 parameters (which is huge but fewer than mySQL supports).

        I think this is actually a _feature_ and is based on using prefetch with paginated queries.

        However, for a related child, prefetching that Model can break the database if it is not paginated and has a
        large number of objects. This is an
        `issue<https://github.com/django-json-api/django-rest-framework-json-api/issues/178>`_
        raised for DJA that is worked around by
        `skipping the related data<https://github.com/django-json-api/django-rest-framework-json-api/pull/445>`_,
        and leaving only the relationship hyperlink in place.

        According to the JSON:API spec:
        "A relationship object that represents a to-many relationship MAY also contain pagination links under the
        links member, as described below. Any pagination links in a relationship object MUST paginate the relationship
        data, not the related resources." -- https://jsonapi.org/format/#document-resource-object-relationships

        First it gets the list of instructors:

        SELECT [myapp_instructor].[id], [myapp_instructor].[effective_start_date], ...
          FROM [myapp_instructor]
          ORDER BY [myapp_instructor].[id] ASC

        Then uses the ids in a WHERE IN list:

        SELECT ([myapp_instructor_course_terms].[instructor_id])
            AS [_prefetch_related_val_instructor_id], [myapp_courseterm].[id], ...
          FROM [myapp_courseterm] INNER JOIN [myapp_instructor_course_terms]
            ON ([myapp_courseterm].[id] = [myapp_instructor_course_terms].[courseterm_id])
         WHERE [myapp_instructor_course_terms].[instructor_id] IN (%s, %s, ...)

        But if you paginate the query (page size 10), then a 'SELECT TOP 10 ...'
        or 'SELECT ... OFFSET 10 FETCH FIRST 10 ROWS ONLY' happens

        To test this with different database engines, set `DJANGO_MYSQL=true` or `DJANGO_SQLSERVER=true` (see settings)

        Right now the SQL database debug messages just go to the console.
        TODO: Find a way to capture the SQL queries here in the test case so we can do something with them.

        See also https://medium.com/@hansonkd/performance-problems-in-the-django-orm-1f62b3d04785
        https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.Prefetch

        :return:
        """
        # TestCase turns off DEBUG, so turn it back on so we get the SQL queries logged
        olddebug = settings.DEBUG
        settings.DEBUG = True
        instructors = Instructor.objects.all().prefetch_related('course_terms')
        ####
        # For the "master" table (instructors), the prefetch list of parameters is limited to the "page" size.
        # Make a queryset of a "page" of 5 instructors.
        # In the comments below, the SQL debug log output has been cleaned up to be a little more readable.
        # (for added readability I've replaced the list of all selected column names with '*'):
        ####
        first_page = instructors[0:5]
        ####
        # Reference the instructors values. Iterating over the queryset values is what triggers the prefetch query to
        # execute.
        #
        # 1. The first 5 Instructor IDs are selected:
        #
        # SELECT TOP 5 [myapp_instructor].* FROM [myapp_instructor] ORDER BY [myapp_instructor].[id] ASC
        #
        # 2. Prefetch the (Instructor ID, associated CourseTerm.*) tuples for the given 5 Instructor IDs via the
        #    intermediate many-to-many table: instructor_course_terms:
        #
        # SELECT([myapp_instructor_course_terms].[instructor_id]) AS [_prefetch_related_val_instructor_id],
        #        [myapp_courseterm].*
        #   FROM [myapp_courseterm]
        #   INNER JOIN [myapp_instructor_course_terms]
        #           ON ([myapp_courseterm].[id] = [myapp_instructor_course_terms].[courseterm_id])
        #        WHERE [myapp_instructor_course_terms].[instructor_id] IN (...5 instructor ids...)
        #        ORDER BY [myapp_courseterm].[term_identifier] ASC
        #
        ####
        for i in first_page:
            first_instr = i  # noqa F841
            first_instr_terms = i.course_terms.all().prefetch_related('instructors')
            break
        ####
        # Here's a non-paginated child relationship:
        #
        # 1. Get all the CourseTerm IDs for the first instructor:
        #
        # SELECT [myapp_courseterm].* FROM [myapp_courseterm]
        #  INNER JOIN [myapp_instructor_course_terms]
        #          ON ([myapp_courseterm].[id] = [myapp_instructor_course_terms].[courseterm_id])
        #       WHERE [myapp_instructor_course_terms].[instructor_id] = <first instructor id>
        #  ORDER BY [myapp_courseterm].[term_identifier] ASC
        #
        # 2. Prefetch the (CourseTerm ID, associated Instructor.*) tuples for that list of CourseTerm IDs:
        #
        # SELECT ([myapp_instructor_course_terms].[courseterm_id]) AS [_prefetch_related_val_courseterm_id],
        #        [myapp_instructor].*
        #   FROM [myapp_instructor]
        #   INNER JOIN [myapp_instructor_course_terms]
        #      ON ([myapp_instructor].[id] = [myapp_instructor_course_terms].[instructor_id])
        #   WHERE [myapp_instructor_course_terms].[courseterm_id] IN (...long course_term list...)
        ####
        for t in first_instr_terms:
            first_termid = t.term_identifier  # noqa F841
            break
        ####
        # select the next page of Instructors
        ####
        next_page = instructors[5:10]
        ####
        #
        # SELECT [myapp_instructor].* FROM [myapp_instructor] ORDER BY [myapp_instructor].[id] ASC
        #        OFFSET 5 ROWS FETCH FIRST 5 ROWS ONLY
        #
        # SELECT ([myapp_instructor_course_terms].[instructor_id]) AS [_prefetch_related_val_instructor_id],
        #         [myapp_courseterm].*
        #   FROM [myapp_courseterm]
        #   INNER JOIN [myapp_instructor_course_terms]
        #      ON ([myapp_courseterm].[id] = [myapp_instructor_course_terms].[courseterm_id])
        #   WHERE [myapp_instructor_course_terms].[instructor_id] IN (...5 ids...)
        #   ORDER BY [myapp_courseterm].[term_identifier] ASC
        #
        ####
        for i in next_page:
            instr = i  # noqa F841
            break
        settings.DEBUG = olddebug
