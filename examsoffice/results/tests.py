import io

import pandas as pd
from django.http import response
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User

from results import models as ex
from results.forms import ResultFileUploadForm
from results.models import Student


# a generic class providing an authorized user for views that require login
class LoggedInTestCase(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(
            username="testygen", password="gennyfromtheblock"
        )
        self.client.login(username="testygen", password="gennyfromtheblock")


# #models test

# this project uses a pre-existing database, writing passing tests
# for the models is yet to be addressed.
# the issue is that the Meta class of the pre-existing models have their
# managed field field set to False.
# Actively looking for a solve for this.


# class StudentModelTestCase(TestCase):
#     def setUp(self):
#         Student.objects.create(student_reg_no='2010/170254',
#                                 first_name='John',
#                                 last_name='Doe')

#     def test_student_object(self):
#         response = Student.objects.get(student_reg_no='2010/170254')
#         self.assertEqual(response.last_name,'Doe')
#         self.assertEqual(response.first_name,'John')


class EditResultTest(LoggedInTestCase):
    pass


class FindStudentTest(LoggedInTestCase):
    def test_search_rendering(self):
        response = self.client.get(reverse("students:search"))
        self.assertEqual(response.status_code, 200)

    def test_actual_search_w_valid_reg_no(self):
        response = self.client.post(
            reverse("students:search"), {"reg_no": "2010/170254"}
        )
        self.assertEqual(response.status_code, 302)

    def test_actual_search_w_invalid_reg_no(self):
        response = self.client.post(
            reverse("students:search"), {"reg_no": "201022/44170254"}
        )
        self.assertEqual(response.status_code, 200)


# class StudentRecordsTest(LoggedInTestCase):

#     def setUp(self):
#         Student.objects.create(student_reg_no='2010/170254')

#     def test_student_records_w_valid_arg(self):
#         response = self.client.get(reverse('student-records',
#                                 kwargs={'reg_no': '2010_170254'}))
#         self.assertEqual(response.status_code, 200)

#     def test_student_records_w_invalid_arg(self):
#         response = self.client.get(reverse('student-records',
#                                 kwargs={'reg_no': '2010/170254'}))
#         self.assertEqual(response.status_code, 500)

class ResultUploadFormViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass123")
        self.client = Client()
        self.client.login(username="tester", password="pass123")
        self.level_of_study = ex.LevelOfStudy.objects.create(
            level="100", level_name="100 Level", level_description="Freshman"
        )
        self.session = ex.Session.objects.create(
            session="2020/2021"
        )
        self.actual_semester = ex.Semester.objects.create(
            semester="First"
        )
        self.course = ex.Course.objects.create(
            course_code="GSP 111",
            course_title="Library Jargon",
            course_level_id=100,
            course_semester_id="First",
            credit_load=3,
        )
        self.semester = ex.SemesterSession.objects.create(
            session=self.session, semester=self.actual_semester
        )

        self.url.reverse("results:upload_results")
    
    def make_excel_file(self, rows):
        """Helper to create an in-memory Excel file.
        :arg rows: List of rows, where each row is a list of cell values.
        """
        df = pd.DataFrame(rows)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, header=False)
        buffer.seek(0)
        return buffer
    
    def test_valid_upload_creates_results(self):
        file = self.make_excel_file([
            ["Student Registration Number", "Grade"],
            ["2010/170254", "A"],
            ["2010/170255", "A"],
        ])
        response = self.client.post(
            self.url,
            {
                "course": self.course.pk,
                "semester": self.semester.pk,
                "skip_existing_rows": True,
                "result_file": file,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Upload complete", response.json()["message"])
        self.assertEqual(ex.Result.objects.count(), 2)
    
    def test_invalid_excel_file_returns_error(self):
        file = io.BytesIO(b"not an excel file")
        file.name = "invalid.xlsx"

        response = self.client.post(
            self.url,
            {
                "course": self.course.pk,
                "semester": self.semester.pk,
                "skip_existing_rows": True,
                "result_file": file,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Problem reading excel file", response.json()["error"])

    def test_invalid_registration_number(self):
        file = self.make_excel_file([
            ["Student Registration Number", "Grade"],
            ["2010/170254", "A"],
            ["2010/170255.", "A"],
        ])

        response = self.client.post(
            self.url,
            {
                "course": self.course.pk,
                "semester": self.semester.pk,
                "skip_existing_rows": True,
                "result_file": file,
            }
        )
        self.assertEqual(response.status_code, 207)
        data = response.json()
        self.assertIn("invalid_rows", data)
        self.assertEqual(len(data["invalid_rows"]), 1)
    
    def test_existing_result_skipped_if_flag_true(self):
        ex.Result.objects.create(
            student_reg_no="2019/123456",
            course=self.course,
            semester=self.semester,
            letter_grade="B",
        )

        file = self.make_excel_file([
            ["Student Registration Number", "Grade"],
            ["2019/123456", "A"]
        ])
        response = self.client.post(
            self.url,
            {
                "course": self.course.pk,
                "semester": self.semester.pk,
                "skip_existing_rows": True,
                "result_file": file,
            }
        )
        self.assertEqual(response.status_code, 207)
        self.assertIn("invalid_rows", response.json())

    def test_existing_result_updated_if_flag_false(self):
        result = ex.Result.objects.create(
            student_reg_no="2019/123456",
            course=self.course,
            semester=self.semester,
            letter_grade="A",
        )
        
        file = self.make_excel_file([
            ["Student Registration Number", "Grade"],
            ["2019/123456", "B"]
        ])
        response = self.client.post(
            self.url,
            {
                "course": self.course.pk,
                "semester": self.semester.pk,
                "skip_existing_rows": False,
                "result_file": file,
            }
        )
        self.assertEqual(response.status_code, 200)
        result.refresh_from_db()
        self.assertEqual(result.letter_grade, "B")