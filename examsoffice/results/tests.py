from django.test import TestCase
from . import models, views
from django.contrib.auth.models import User

from django.urls import reverse

class LoggedInTestCase(TestCase):

    def setUp(self) -> None:
        user = User.objects.create_user(username='testygen', password='gennyfromtheblock')
        self.client.login(username='testygen', password='gennyfromtheblock')


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