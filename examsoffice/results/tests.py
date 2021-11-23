from django.http import response
from django.test import TestCase
from results.models import Student
from django.contrib.auth.models import User

from django.urls import reverse


#a generic class providing an authorized user for views that require login
class LoggedInTestCase(TestCase):

    def setUp(self) -> None:
        user = User.objects.create_user(
                            username='testygen', password='gennyfromtheblock'
                            )
        self.client.login(username='testygen', password='gennyfromtheblock')


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

#views test
class ResultMenuTest(TestCase):

    def test_menu_view(self):
        response = self.client.get(reverse('results:results_menu'))
        self.assertEqual(response.status_code, 200)


class EditResultTest(LoggedInTestCase):
    pass


class FindStudentTest(LoggedInTestCase):

    def test_search_rendering(self):
        response = self.client.get(reverse('results:student_search'))
        self.assertEqual(response.status_code,200)

    def test_actual_search_w_valid_reg_no(self):
        response = self.client.post(reverse('results:student_search'),
                                    {'reg_no': '2010/170254'})
        self.assertEqual(response.status_code, 302)
    
    def test_actual_search_w_invalid_reg_no(self):
        response = self.client.post(reverse('results:student_search'),
                                    {'reg_no': '201022/44170254'})
        self.assertEqual(response.status_code, 200)


# class StudentRecordsTest(LoggedInTestCase):
    
#     def setUp(self):
#         Student.objects.create(student_reg_no='2010/170254')

#     def test_student_records_w_valid_arg(self):
#         response = self.client.get(reverse('results:student_records',
#                                 kwargs={'reg_no': '2010_170254'}))
#         self.assertEqual(response.status_code, 200)
    
#     def test_student_records_w_invalid_arg(self):
#         response = self.client.get(reverse('results:student_records',
#                                 kwargs={'reg_no': '2010/170254'}))
#         self.assertEqual(response.status_code, 500)
