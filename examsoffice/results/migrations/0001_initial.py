# Generated by Django 3.2.7 on 2021-12-03 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lecturer',
            fields=[
                ('id', models.BigAutoField(db_column='LecturerID', primary_key=True, serialize=False)),
                ('staff_number', models.CharField(blank=True, db_column='StaffNumber', max_length=255, null=True, unique=True)),
                ('title', models.CharField(blank=True, db_column='Title', max_length=255, null=True)),
                ('first_name', models.CharField(blank=True, db_column='FirstName', max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, db_column='LastName', max_length=255, null=True)),
                ('other_names', models.CharField(blank=True, db_column='OtherNames', max_length=255, null=True)),
                ('email', models.CharField(blank=True, db_column='Email', max_length=255, null=True)),
                ('department', models.CharField(blank=True, db_column='Department', max_length=255, null=True)),
                ('faculty', models.CharField(blank=True, db_column='Faculty', max_length=255, null=True)),
                ('head_of_dept', models.BooleanField(blank=True, db_column='HeadOfDepartment', null=True)),
            ],
            options={
                'db_table': 'tbl2Lecturers',
            },
        ),
        migrations.CreateModel(
            name='LecturerRole',
            fields=[
                ('id', models.BigAutoField(db_column='RoleID', primary_key=True, serialize=False)),
                ('role', models.CharField(blank=True, db_column='Role', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2LecturerRoles',
            },
        ),
        migrations.CreateModel(
            name='LevelOfStudy',
            fields=[
                ('level', models.BigIntegerField(db_column='Level', primary_key=True, serialize=False)),
                ('level_name', models.CharField(blank=True, db_column='LevelName', max_length=255, null=True)),
                ('level_description', models.CharField(blank=True, db_column='LevelDescription', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2Levels',
            },
        ),
        migrations.CreateModel(
            name='MaritalStatus',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('marital_status', models.CharField(blank=True, db_column='MaritalStatus', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2MaritalStatuses',
            },
        ),
        migrations.CreateModel(
            name='ModeOfAdmission',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('mode_of_admission', models.CharField(blank=True, db_column='ModeOfAdmission', max_length=255, null=True)),
                ('description', models.CharField(blank=True, db_column='Description', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2ModesOfAdmission',
            },
        ),
        migrations.CreateModel(
            name='ModeOfStudy',
            fields=[
                ('id', models.IntegerField(db_column='ID', primary_key=True, serialize=False)),
                ('mode_of_study', models.CharField(blank=True, db_column='ModeOfStudy', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2ModesOfStudy',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('relationship', models.CharField(blank=True, db_column='Relationship', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2Relationships',
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigIntegerField(db_column='ID', primary_key=True, serialize=False)),
                ('semester', models.CharField(blank=True, db_column='Semester', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2Semesters',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(db_column='SessionID', primary_key=True, serialize=False)),
                ('session', models.CharField(db_column='Session', max_length=255, unique=True)),
            ],
            options={
                'db_table': 'tbl2Sessions',
            },
        ),
        migrations.CreateModel(
            name='Sex',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('sex', models.CharField(blank=True, db_column='Sex', max_length=255, null=True)),
            ],
            options={
                'db_table': 'tbl2Sexes',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('student_reg_no', models.CharField(db_column='StudentRegNo', max_length=255, unique=True)),
                ('last_name', models.CharField(blank=True, db_column='LastName', default='--', max_length=255, null=True)),
                ('first_name', models.CharField(blank=True, db_column='FirstName', default='--', max_length=255, null=True)),
                ('other_names', models.CharField(blank=True, db_column='OtherNames', default='--', max_length=255, null=True)),
                ('email', models.CharField(blank=True, db_column='Email', max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, db_column='PhoneNumber', max_length=255, null=True)),
                ('date_of_birth', models.DateTimeField(blank=True, db_column='DOB', null=True)),
                ('town_of_origin', models.CharField(blank=True, db_column='TownOfOrigin', max_length=255, null=True)),
                ('lga_of_origin', models.CharField(blank=True, db_column='LGAOfOrigin', max_length=255, null=True)),
                ('state_of_origin', models.CharField(blank=True, db_column='StateOfOrigin', max_length=255, null=True)),
                ('nationality', models.CharField(blank=True, db_column='Nationality', max_length=255, null=True)),
                ('level_admitted_to', models.IntegerField(blank=True, db_column='LevelAdmittedTo', null=True)),
                ('year_of_admission', models.CharField(blank=True, db_column='YearOfAdmission', max_length=10, null=True)),
                ('expected_yr_of_grad', models.CharField(blank=True, db_column='ExpectedYearOfGraduation', max_length=10, null=True)),
                ('graduated', models.BooleanField(blank=True, db_column='Graduated', null=True)),
                ('address_line1', models.CharField(blank=True, db_column='AddressLine1', max_length=255, null=True)),
                ('address_line2', models.CharField(blank=True, db_column='AddressLine2', max_length=255, null=True)),
                ('city', models.CharField(blank=True, db_column='City', max_length=255, null=True)),
                ('state', models.CharField(blank=True, db_column='State', max_length=255, null=True)),
                ('country', models.CharField(blank=True, db_column='Country', max_length=255, null=True)),
                ('class_rep', models.BooleanField(blank=True, db_column='ClassRep', null=True)),
                ('current_level_of_study', models.IntegerField(blank=True, db_column='CurrentLevelOfStudy', null=True)),
                ('cgpa', models.CharField(blank=True, db_column='CGPA', max_length=255, null=True)),
                ('student_photo', models.ImageField(blank=True, db_column='studentPhoto', null=True, upload_to='')),
                ('marital_status', models.ForeignKey(blank=True, db_column='MaritalStatus', null=True, on_delete=django.db.models.deletion.PROTECT, to='results.maritalstatus')),
                ('mode_of_admission', models.ForeignKey(blank=True, db_column='ModeOfAdmission', null=True, on_delete=django.db.models.deletion.PROTECT, to='results.modeofadmission')),
                ('mode_of_study', models.ForeignKey(blank=True, db_column='ModeOfStudy', null=True, on_delete=django.db.models.deletion.PROTECT, to='results.modeofstudy')),
                ('sex', models.ForeignKey(blank=True, db_column='Sex', null=True, on_delete=django.db.models.deletion.CASCADE, to='results.sex')),
            ],
            options={
                'db_table': 'tbl1StudentBios',
            },
        ),
        migrations.CreateModel(
            name='StudentSponsor',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, db_column='Title', max_length=255, null=True)),
                ('firstname', models.CharField(blank=True, db_column='FirstName', max_length=255, null=True)),
                ('lastname', models.CharField(blank=True, db_column='LastName', max_length=255, null=True)),
                ('othernames', models.CharField(blank=True, db_column='OtherNames', max_length=255, null=True)),
                ('email', models.CharField(blank=True, db_column='Email', max_length=255, null=True)),
                ('phonenumber', models.CharField(blank=True, db_column='PhoneNumber', max_length=255, null=True)),
                ('relationship', models.IntegerField(blank=True, db_column='Relationship', null=True)),
                ('occupation', models.CharField(blank=True, db_column='Occupation', max_length=255, null=True)),
                ('addressline1', models.CharField(blank=True, db_column='AddressLine1', max_length=255, null=True)),
                ('addressline2', models.CharField(blank=True, db_column='AddressLine2', max_length=255, null=True)),
                ('city', models.CharField(blank=True, db_column='City', max_length=255, null=True)),
                ('state', models.CharField(blank=True, db_column='State', max_length=255, null=True)),
                ('country', models.CharField(blank=True, db_column='Country', max_length=255, null=True)),
                ('student', models.ForeignKey(db_column='Student_ID', on_delete=django.db.models.deletion.CASCADE, to='results.student')),
            ],
            options={
                'db_table': 'tbl1StudentSponsorInfo',
            },
        ),
        migrations.CreateModel(
            name='SemesterSession',
            fields=[
                ('id', models.BigAutoField(db_column='SemesterNumber', primary_key=True, serialize=False)),
                ('desc', models.CharField(blank=True, db_column='Desc', max_length=243, null=True)),
                ('semester', models.ForeignKey(db_column='Semester_ID', on_delete=django.db.models.deletion.PROTECT, to='results.semester')),
                ('session', models.ForeignKey(db_column='Session', max_length=255, on_delete=django.db.models.deletion.PROTECT, to='results.session', to_field='session')),
            ],
            options={
                'db_table': 'tbl2SemesterCount',
                'unique_together': {('session', 'semester')},
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(db_column='CourseID', primary_key=True, serialize=False)),
                ('course_title', models.CharField(blank=True, db_column='CourseTitle', max_length=255, null=True)),
                ('course_code', models.CharField(blank=True, db_column='CourseCode', max_length=255, null=True)),
                ('course_level', models.IntegerField(db_column='CourseLevel')),
                ('credit_load', models.IntegerField(blank=True, db_column='CreditLoad', null=True)),
                ('elective', models.BooleanField(db_column='Elective', default=False)),
                ('course_semester', models.ForeignKey(db_column='CourseSemester', on_delete=django.db.models.deletion.CASCADE, to='results.semester')),
            ],
            options={
                'db_table': 'tbl2Courses',
                'unique_together': {('course_title', 'course_code', 'course_level')},
            },
        ),
        migrations.CreateModel(
            name='StudentProgressHistory',
            fields=[
                ('id', models.BigAutoField(db_column='histID', primary_key=True, serialize=False)),
                ('level_of_study', models.ForeignKey(db_column='LevelOfStudy', on_delete=django.db.models.deletion.PROTECT, to='results.levelofstudy')),
                ('session', models.ForeignKey(db_column='SessionID', on_delete=django.db.models.deletion.PROTECT, to='results.session')),
                ('student_reg_no', models.ForeignKey(db_column='StudentRegNo', max_length=255, on_delete=django.db.models.deletion.PROTECT, to='results.student', to_field='student_reg_no')),
            ],
            options={
                'db_table': 'tbl2StudentProgressHistory',
                'unique_together': {('student_reg_no', 'session_id')},
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('student_reg_no', models.CharField(db_column='StudentRegNo', max_length=25)),
                ('student_level', models.IntegerField(blank=True, db_column='StudentLevel', null=True)),
                ('ca_score', models.FloatField(blank=True, db_column='CAScore', null=True)),
                ('exam_score', models.FloatField(blank=True, db_column='ExamScore', null=True)),
                ('total_score', models.FloatField(blank=True, db_column='TotalScore', null=True)),
                ('letter_grade', models.CharField(db_column='LetterGrade', max_length=5)),
                ('upload_date', models.DateTimeField(auto_now=True, db_column='UploadDate', null=True)),
                ('course', models.ForeignKey(db_column='Course_ID', on_delete=django.db.models.deletion.PROTECT, to='results.course')),
                ('semester', models.ForeignKey(db_column='SemesterNumber', on_delete=django.db.models.deletion.PROTECT, to='results.semestersession')),
            ],
            options={
                'db_table': 'tbl1StudentResults',
                'unique_together': {('semester', 'student_reg_no', 'course')},
            },
        ),
        migrations.CreateModel(
            name='ProgramRequirement',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('course', models.ForeignKey(db_column='CourseID', on_delete=django.db.models.deletion.PROTECT, to='results.course')),
                ('level_of_study', models.ForeignKey(db_column='LevelOfStudy', on_delete=django.db.models.deletion.PROTECT, to='results.levelofstudy')),
                ('mode_of_admission', models.ForeignKey(db_column='ModeOfAdmission', on_delete=django.db.models.deletion.PROTECT, to='results.modeofadmission')),
                ('session', models.ForeignKey(db_column='SessionID', on_delete=django.db.models.deletion.PROTECT, to='results.session')),
            ],
            options={
                'db_table': 'tbl1ProgramRequirements',
                'unique_together': {('course', 'mode_of_admission', 'session')},
            },
        ),
    ]
