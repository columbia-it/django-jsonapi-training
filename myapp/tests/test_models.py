from datetime import date, datetime

from django.db.utils import IntegrityError
from django.test import TestCase

from myapp.models import Course, CourseTerm


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
        self.assertEquals(c.course_identifier, 'ABC123')

    def test_date(self):
        courses = Course.objects.all()
        c = courses.get(course_identifier='ABC123')
        self.assertEquals(c.last_mod_date, date.today())

    def test_num(self):
        cs = Course.objects.all()
        self.assertEquals(2, cs.count())

        terms = CourseTerm.objects.all()
        self.assertEquals(4, terms.count())

        # field look up
        ts = CourseTerm.objects.filter(course__course_identifier='123ABC')
        self.assertEquals(0, ts.count())

        ts = CourseTerm.objects.filter(course__course_identifier='ABC123')
        self.assertEquals(2, ts.count())

        ts = CourseTerm.objects.filter(last_mod_user_name__startswith='Tom')
        self.assertEquals(2, ts.count())

        cs = Course.objects.filter(course_terms__last_mod_user_name__startswith='Tom')
        self.assertEquals(2, cs.count())

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
