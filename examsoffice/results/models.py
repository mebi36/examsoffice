from django.db import models
from django.db.models.deletion import CASCADE, PROTECT

import re

from django.urls.base import reverse

# the managed attribute of the model's meta classes needs
# to be set to False after initial migrations are run as this 
# will adversely impact the use of forms in the project if left
# as false

# Create your models here.

class LecturerRole(models.Model):
    id = models.BigAutoField(db_column='RoleID', primary_key=True)
    role = models.CharField(db_column='Role', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2LecturerRoles'


class Lecturer(models.Model):
    id = models.BigAutoField(db_column='LecturerID', primary_key=True)
    staff_number = models.CharField(db_column='StaffNumber', unique=True, max_length=255, blank=True, null=True)
    title = models.CharField(db_column='Title', max_length=255, blank=True, null=True)
    first_name = models.CharField(db_column='FirstName', max_length=255, blank=True, null=True)
    last_name = models.CharField(db_column='LastName', max_length=255, blank=True, null=True)
    other_names = models.CharField(db_column='OtherNames', max_length=255, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)
    department = models.CharField(db_column='Department', max_length=255, blank=True, null=True)
    faculty = models.CharField(db_column='Faculty', max_length=255, blank=True, null=True)
    head_of_dept = models.BooleanField(db_column='HeadOfDepartment', null=True, blank=True)
    class Meta:
        db_table = 'tbl2Lecturers'

    @property
    def full_name(self):
        return f"{self.title or ''} {self.first_name[0] if self.first_name != None else ''} {self.other_names[0] if self.other_names != None else ''} {self.last_name}"
    
    def __str__(self) -> str:
        return self.full_name
    
    @staticmethod
    def is_valid_staff_no(staff_no):
        if re.search(r"^[S]{2}.", staff_no) != None:
            return True
        else:
            return False

class LevelOfStudy(models.Model):
    level = models.BigIntegerField(db_column='Level', primary_key=True)
    level_name = models.CharField(db_column='LevelName', max_length=255, blank=True, null=True)
    level_description = models.CharField(db_column='LevelDescription', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2Levels'
    
    def __str__(self):
        return self.level_name


class MaritalStatus(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    marital_status = models.CharField(db_column='MaritalStatus', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2MaritalStatuses'

    def __str__(self):
        return self.marital_status


class ModeOfAdmission(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    mode_of_admission = models.CharField(db_column='ModeOfAdmission', max_length=255, blank=True, null=True)
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2ModesOfAdmission'
    
    def __str__(self) -> str:
        return self.mode_of_admission


class ModeOfStudy(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    mode_of_study = models.CharField(db_column='ModeOfStudy', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2ModesOfStudy'

    def __str__(self):
        return self.mode_of_study

class Relationship(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    relationship = models.CharField(db_column='Relationship', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2Relationships'

    def __str__(self):
        return self.relationship


class Semester(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)
    semester = models.CharField(db_column='Semester', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2Semesters'

    def __str__(self):
        return self.semester

class Session(models.Model):
    id = models.BigAutoField(db_column='SessionID', primary_key=True)
    session = models.CharField(db_column='Session', max_length=255, blank=False,
                             null=False, unique=True)

    class Meta:
        db_table = 'tbl2Sessions'


    def __str__(self):
        return self.session


class Sex(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    sex = models.CharField(db_column='Sex', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl2Sexes'

    def __str__(self):
        return self.sex

class SemesterSession(models.Model):
    id = models.BigAutoField(db_column='SemesterNumber', 
                                            primary_key=True)
    session = models.ForeignKey(db_column='Session', max_length=255, 
                                to='Session', to_field='session',on_delete=PROTECT)
    semester = models.ForeignKey(db_column='Semester_ID',to='Semester',on_delete=PROTECT)
    desc = models.CharField(db_column='Desc', max_length=243, blank=True, null=True)

    class Meta:
        db_table = 'tbl2SemesterCount'
        unique_together = (('session', 'semester'),)


    def __str__(self):
        return self.desc


class Course(models.Model):
    id = models.BigAutoField(db_column='CourseID', primary_key=True)
    course_title = models.CharField(db_column='CourseTitle', max_length=255, blank=True, null=True)
    course_code = models.CharField(db_column='CourseCode', max_length=255, blank=True, null=True)
    course_semester = models.ForeignKey(db_column='CourseSemester', to='Semester',
                                        on_delete=CASCADE)
    course_level = models.IntegerField(db_column='CourseLevel')
    credit_load = models.IntegerField(db_column='CreditLoad', blank=True, null=True)
    elective = models.BooleanField(db_column='Elective', default=False)

    class Meta:
        db_table = 'tbl2Courses'
        unique_together = (('course_title', 'course_code', 'course_level'),)


class ProgramRequirement(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    mode_of_admission = models.ForeignKey(db_column='ModeOfAdmission',
                                            to='ModeOfAdmission',
                                            on_delete=PROTECT)
    course = models.ForeignKey(db_column='CourseID',to='Course',
                                    on_delete=PROTECT)
    level_of_study = models.ForeignKey(db_column='LevelOfStudy',
                                        to='LevelOfStudy',on_delete=PROTECT)
    session = models.ForeignKey(db_column='SessionID',to='Session',
                                    on_delete=PROTECT)

    class Meta:
        db_table = 'tbl1ProgramRequirements'
        unique_together = (('course', 'mode_of_admission', 'session'),)


class Student(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    student_reg_no = models.CharField(db_column='StudentRegNo', unique=True, max_length=255)
    last_name = models.CharField(db_column='LastName', max_length=255, blank=True, null=True, default='--')
    first_name = models.CharField(db_column='FirstName', max_length=255, blank=True, null=True, default='--')
    other_names = models.CharField(db_column='OtherNames', max_length=255, blank=True, null=True, default='--')
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)
    phone_number = models.CharField(db_column='PhoneNumber', max_length=255, blank=True, null=True)
    sex = models.ForeignKey(db_column='Sex', blank=True, null=True,to='Sex',on_delete=CASCADE)
    marital_status = models.ForeignKey(db_column='MaritalStatus', blank=True, null=True,
                                        to='MaritalStatus', on_delete=PROTECT)
    date_of_birth = models.DateTimeField(db_column='DOB', blank=True, null=True)
    town_of_origin = models.CharField(db_column='TownOfOrigin', max_length=255, blank=True, null=True)
    lga_of_origin = models.CharField(db_column='LGAOfOrigin', max_length=255, blank=True, null=True)
    state_of_origin = models.CharField(db_column='StateOfOrigin', max_length=255, blank=True, null=True)
    nationality = models.CharField(db_column='Nationality', max_length=255, blank=True, null=True)
    mode_of_admission = models.ForeignKey(db_column='ModeOfAdmission', blank=True, null=True,
                                            to='ModeOfAdmission', on_delete=PROTECT)
    level_admitted_to = models.IntegerField(db_column='LevelAdmittedTo', blank=True, null=True)
    mode_of_study = models.ForeignKey(db_column='ModeOfStudy', blank=True, null=True,
                                      to='ModeOfStudy',on_delete=PROTECT)
    year_of_admission = models.CharField(db_column='YearOfAdmission', max_length=10, blank=True, null=True)
    expected_yr_of_grad = models.CharField(db_column='ExpectedYearOfGraduation', max_length=10, blank=True, null=True)
    graduated = models.BooleanField(db_column='Graduated', blank=True, null=True)
    address_line1 = models.CharField(db_column='AddressLine1', max_length=255, blank=True, null=True)
    address_line2 = models.CharField(db_column='AddressLine2', max_length=255, blank=True, null=True)
    city = models.CharField(db_column='City', max_length=255, blank=True, null=True)
    state = models.CharField(db_column='State', max_length=255, blank=True, null=True)
    country = models.CharField(db_column='Country', max_length=255, blank=True, null=True)
    class_rep = models.BooleanField(db_column='ClassRep', blank=True, null=True)
    current_level_of_study = models.IntegerField(db_column='CurrentLevelOfStudy', blank=True, null=True)
    cgpa = models.CharField(db_column='CGPA', max_length=255, blank=True, null=True)
    # student_photo = models.ImageField(db_column='studentPhoto', blank=True, null=True)
    jamb_number = models.CharField(db_column='JambNumber', max_length=20, blank=True, null=True)


    class Meta:
        db_table = 'tbl1StudentBios'


    def get_reg_no_for_url(self):
        return self.student_reg_no.replace("/", "_")

    def get_absolute_url(self):
        return reverse('students:edit_bio',
                        kwargs={'reg_no': self.get_reg_no_for_url()})

    def get_records_url(self):
        return reverse('results:student_records',
                        kwargs={'reg_no': self.get_reg_no_for_url()})
    
    def get_record_creation_url(self):
        return reverse('results:add',
                        kwargs={'reg_no': self.get_reg_no_for_url()})

    def get_progress_history_url(self):
        return reverse('students:progress_history',
                        args=[self.get_reg_no_for_url()])

    @staticmethod
    def is_valid_reg_no(reg_no):
        if re.search("^[0-9]{4}\/[0-9]{6}$", reg_no) != None:
            return True
        else:
            return False
    
    @staticmethod
    def get_weight_col(df, credit_col='credit_load',grade_col='grade'):
        df['weight'] = df.get(credit_col) * [5 if x == 'A' else 4 
                                    if x == 'B' else 3 if 
                                    x == 'C' else 2 if x == 'D'
                                    else 1 if x == 'E' else 0 
                                    for x in df.get(grade_col)]
        return df

    @property
    def full_name(self):
            full_name = ''
            if self.last_name:
                full_name += (self.last_name + ", ")
            if self.first_name:
                full_name += (self.first_name + " ")
            if self.other_names:
                full_name += (self.other_names)
            return full_name.upper() or "N/A"
    
    def get_level_of_study(self):
        return f"{self.current_level_of_study}/5" or "N/A"


class Result(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    course = models.ForeignKey(db_column='Course_ID',
                                to=Course,
                                on_delete=PROTECT
                                )
    semester = models.ForeignKey(
                                SemesterSession,
                                on_delete=models.PROTECT,
                                db_column='SemesterNumber'
                                )
    student_reg_no = models.CharField(db_column='StudentRegNo', max_length=25)
    student_level = models.IntegerField(db_column='StudentLevel', 
                                        blank=True, null=True)
    ca_score = models.FloatField(db_column='CAScore', blank=True, null=True)
    exam_score = models.FloatField(db_column='ExamScore', blank=True, 
                                                                null=True)
    total_score = models.FloatField(db_column='TotalScore', blank=True,
                                                                null=True)
    letter_grade = models.CharField(db_column='LetterGrade', max_length=5)
    upload_date = models.DateTimeField(db_column='UploadDate', blank=True,
                                                    null=True, auto_now=True)

    class Meta:
        db_table = 'tbl1StudentResults'
        unique_together = (('semester', 'student_reg_no', 'course'),)

    def get_edit_url(self):
        return reverse('results:result_edit', kwargs={'pk': self.id})


class StudentSponsor(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    student = models.ForeignKey(Student, db_column='Student_ID', on_delete=models.CASCADE)
    title = models.CharField(db_column='Title', max_length=255, blank=True, null=True)
    firstname = models.CharField(db_column='FirstName', max_length=255, blank=True, null=True)
    lastname = models.CharField(db_column='LastName', max_length=255, blank=True, null=True)
    othernames = models.CharField(db_column='OtherNames', max_length=255, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)
    phonenumber = models.CharField(db_column='PhoneNumber', max_length=255, blank=True, null=True)
    relationship = models.IntegerField(db_column='Relationship', blank=True, null=True)
    occupation = models.CharField(db_column='Occupation', max_length=255, blank=True, null=True)
    addressline1 = models.CharField(db_column='AddressLine1', max_length=255, blank=True, null=True)
    addressline2 = models.CharField(db_column='AddressLine2', max_length=255, blank=True, null=True)
    city = models.CharField(db_column='City', max_length=255, blank=True, null=True)
    state = models.CharField(db_column='State', max_length=255, blank=True, null=True)
    country = models.CharField(db_column='Country', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tbl1StudentSponsorInfo'


class StudentProgressHistory(models.Model):
    id = models.BigAutoField(db_column='histID', primary_key=True)
    session = models.ForeignKey(db_column='SessionID',to='Session',
                                    on_delete=PROTECT)
    student_reg_no = models.ForeignKey(db_column='StudentRegNo', max_length=255,
                                        to='Student',to_field='student_reg_no',
                                        on_delete=PROTECT)
    level_of_study = models.ForeignKey(db_column='LevelOfStudy',to='LevelOfStudy',
                                        on_delete=PROTECT)

    class Meta:
        db_table = 'tbl2StudentProgressHistory'
        unique_together = (('student_reg_no', 'session_id'),)


    def get_update_url(self):
        return reverse('students:progress_history_edit',args=[self.id])