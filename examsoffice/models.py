# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_groups"
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_user_permissions"
        unique_together = (("user", "permission"),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType", models.DO_NOTHING, blank=True, null=True
    )
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class Tbl1Programrequirements(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    modeofadmission = models.IntegerField(
        db_column="ModeOfAdmission"
    )  # Field name made lowercase.
    courseid = models.BigIntegerField(
        db_column="CourseID"
    )  # Field name made lowercase.
    levelofstudy = models.IntegerField(
        db_column="LevelOfStudy"
    )  # Field name made lowercase.
    sessionid = models.BigIntegerField(
        db_column="SessionID"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl1ProgramRequirements"
        unique_together = (("courseid", "modeofadmission", "sessionid"),)


class Tbl1Studentbios(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    studentregno = models.CharField(
        db_column="StudentRegNo", unique=True, max_length=255
    )  # Field name made lowercase.
    lastname = models.CharField(
        db_column="LastName", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    firstname = models.CharField(
        db_column="FirstName", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    othernames = models.CharField(
        db_column="OtherNames", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    email = models.CharField(
        db_column="Email", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    phonenumber = models.CharField(
        db_column="PhoneNumber", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    sex = models.IntegerField(
        db_column="Sex", blank=True, null=True
    )  # Field name made lowercase.
    maritalstatus = models.IntegerField(
        db_column="MaritalStatus", blank=True, null=True
    )  # Field name made lowercase.
    dob = models.DateTimeField(
        db_column="DOB", blank=True, null=True
    )  # Field name made lowercase.
    townoforigin = models.CharField(
        db_column="TownOfOrigin", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    lgaoforigin = models.CharField(
        db_column="LGAOfOrigin", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    stateoforigin = models.CharField(
        db_column="StateOfOrigin", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    nationality = models.CharField(
        db_column="Nationality", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    modeofadmission = models.IntegerField(
        db_column="ModeOfAdmission", blank=True, null=True
    )  # Field name made lowercase.
    leveladmittedto = models.IntegerField(
        db_column="LevelAdmittedTo", blank=True, null=True
    )  # Field name made lowercase.
    modeofstudy = models.IntegerField(
        db_column="ModeOfStudy", blank=True, null=True
    )  # Field name made lowercase.
    yearofadmission = models.CharField(
        db_column="YearOfAdmission", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    expectedyearofgraduation = models.CharField(
        db_column="ExpectedYearOfGraduation",
        max_length=10,
        blank=True,
        null=True,
    )  # Field name made lowercase.
    graduated = models.BooleanField(
        db_column="Graduated", blank=True, null=True
    )  # Field name made lowercase.
    addressline1 = models.CharField(
        db_column="AddressLine1", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    addressline2 = models.CharField(
        db_column="AddressLine2", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    city = models.CharField(
        db_column="City", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    state = models.CharField(
        db_column="State", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    country = models.CharField(
        db_column="Country", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    classrep = models.BooleanField(
        db_column="ClassRep", blank=True, null=True
    )  # Field name made lowercase.
    currentlevelofstudy = models.IntegerField(
        db_column="CurrentLevelOfStudy", blank=True, null=True
    )  # Field name made lowercase.
    cgpa = models.CharField(
        db_column="CGPA", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    studentphoto = models.BinaryField(
        db_column="studentPhoto", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl1StudentBios"


class Tbl1Studentresults(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    course_id = models.IntegerField(
        db_column="Course_ID", blank=True, null=True
    )  # Field name made lowercase.
    semesternumber = models.IntegerField(
        db_column="SemesterNumber", blank=True, null=True
    )  # Field name made lowercase.
    studentregno = models.CharField(
        db_column="StudentRegNo", max_length=25, blank=True, null=True
    )  # Field name made lowercase.
    studentlevel = models.IntegerField(
        db_column="StudentLevel", blank=True, null=True
    )  # Field name made lowercase.
    cascore = models.IntegerField(
        db_column="CAScore", blank=True, null=True
    )  # Field name made lowercase.
    examscore = models.IntegerField(
        db_column="ExamScore", blank=True, null=True
    )  # Field name made lowercase.
    totalscore = models.IntegerField(
        db_column="TotalScore", blank=True, null=True
    )  # Field name made lowercase.
    lettergrade = models.CharField(
        db_column="LetterGrade", max_length=5
    )  # Field name made lowercase.
    uploaddate = models.DateTimeField(
        db_column="UploadDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl1StudentResults"
        unique_together = (("semesternumber", "studentregno", "course_id"),)


class Tbl1Studentsponsorinfo(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    student_id = models.IntegerField(
        db_column="Student_ID", blank=True, null=True
    )  # Field name made lowercase.
    title = models.CharField(
        db_column="Title", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    firstname = models.CharField(
        db_column="FirstName", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    lastname = models.CharField(
        db_column="LastName", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    othernames = models.CharField(
        db_column="OtherNames", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    email = models.CharField(
        db_column="Email", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    phonenumber = models.CharField(
        db_column="PhoneNumber", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    relationship = models.IntegerField(
        db_column="Relationship", blank=True, null=True
    )  # Field name made lowercase.
    occupation = models.CharField(
        db_column="Occupation", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    addressline1 = models.CharField(
        db_column="AddressLine1", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    addressline2 = models.CharField(
        db_column="AddressLine2", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    city = models.CharField(
        db_column="City", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    state = models.CharField(
        db_column="State", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    country = models.CharField(
        db_column="Country", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl1StudentSponsorInfo"


class Tbl2Courses(models.Model):
    courseid = models.BigIntegerField(
        db_column="CourseID", primary_key=True
    )  # Field name made lowercase.
    coursetitle = models.CharField(
        db_column="CourseTitle", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    coursecode = models.CharField(
        db_column="CourseCode", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    coursesemester = models.IntegerField(
        db_column="CourseSemester", blank=True, null=True
    )  # Field name made lowercase.
    courselevel = models.IntegerField(
        db_column="CourseLevel", blank=True, null=True
    )  # Field name made lowercase.
    creditload = models.IntegerField(
        db_column="CreditLoad", blank=True, null=True
    )  # Field name made lowercase.
    elective = models.BooleanField(
        db_column="Elective", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2Courses"
        unique_together = (("coursetitle", "coursecode", "courselevel"),)


class Tbl2Dbusers(models.Model):
    userid = models.BigIntegerField(
        db_column="UserID", primary_key=True
    )  # Field name made lowercase.
    username = models.CharField(
        db_column="Username", max_length=25, blank=True, null=True
    )  # Field name made lowercase.
    password = models.CharField(
        db_column="Password", max_length=25, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2DBUsers"


class Tbl2Lecturerroles(models.Model):
    roleid = models.IntegerField(
        db_column="RoleID", primary_key=True
    )  # Field name made lowercase.
    role = models.CharField(
        db_column="Role", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2LecturerRoles"


class Tbl2Lecturers(models.Model):
    lecturerid = models.BigIntegerField(
        db_column="LecturerID", primary_key=True
    )  # Field name made lowercase.
    staffnumber = models.CharField(
        db_column="StaffNumber",
        unique=True,
        max_length=255,
        blank=True,
        null=True,
    )  # Field name made lowercase.
    title = models.CharField(
        db_column="Title", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    firstname = models.CharField(
        db_column="FirstName", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    lastname = models.CharField(
        db_column="LastName", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    othernames = models.CharField(
        db_column="OtherNames", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    email = models.CharField(
        db_column="Email", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    department = models.CharField(
        db_column="Department", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    faculty = models.CharField(
        db_column="Faculty", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    headofdepartment = models.BooleanField(
        db_column="HeadOfDepartment", unique=True, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2Lecturers"


class Tbl2Levels(models.Model):
    level = models.BigIntegerField(
        db_column="Level", primary_key=True
    )  # Field name made lowercase.
    levelname = models.CharField(
        db_column="LevelName", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    leveldescription = models.CharField(
        db_column="LevelDescription", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2Levels"


class Tbl2Maritalstatuses(models.Model):
    id = models.IntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    maritalstatus = models.CharField(
        db_column="MaritalStatus", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2MaritalStatuses"


class Tbl2Modesofadmission(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    modeofadmission = models.CharField(
        db_column="ModeOfAdmission", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="Description", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2ModesOfAdmission"


class Tbl2Modesofstudy(models.Model):
    id = models.IntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    modeofstudy = models.CharField(
        db_column="ModeOfStudy", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2ModesOfStudy"


class Tbl2Relationships(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    relationship = models.CharField(
        db_column="Relationship", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2Relationships"


class Tbl2Semestercount(models.Model):
    semesternumber = models.BigIntegerField(
        db_column="SemesterNumber", primary_key=True
    )  # Field name made lowercase.
    session = models.CharField(
        db_column="Session", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    semester_id = models.IntegerField(
        db_column="Semester_ID", blank=True, null=True
    )  # Field name made lowercase.
    desc = models.CharField(
        db_column="Desc", max_length=243, blank=True, null=True
    )  # Field name made lowercase.
    sessionid = models.IntegerField(
        db_column="SessionID", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2SemesterCount"
        unique_together = (("session", "semester_id"),)


class Tbl2Semesters(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    semester = models.CharField(
        db_column="Semester", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2Semesters"


class Tbl2Sessions(models.Model):
    sessionid = models.BigIntegerField(
        db_column="SessionID", primary_key=True
    )  # Field name made lowercase.
    session = models.CharField(
        db_column="Session", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2Sessions"


class Tbl2Sexes(models.Model):
    id = models.IntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    sex = models.CharField(
        db_column="Sex", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2Sexes"


class Tbl2Studentprogresshistory(models.Model):
    histid = models.BigIntegerField(
        db_column="histID", primary_key=True
    )  # Field name made lowercase.
    sessionid = models.IntegerField(
        db_column="SessionID", blank=True, null=True
    )  # Field name made lowercase.
    studentregno = models.CharField(
        db_column="StudentRegNo", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    levelofstudy = models.IntegerField(
        db_column="LevelOfStudy", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl2StudentProgressHistory"
        unique_together = (("studentregno", "sessionid"),)


class Tbl3Courseallocations(models.Model):
    id = models.BigIntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    course_id = models.IntegerField(
        db_column="Course_ID", blank=True, null=True
    )  # Field name made lowercase.
    semesternumber = models.IntegerField(
        db_column="SemesterNumber", blank=True, null=True
    )  # Field name made lowercase.
    lecturerid = models.IntegerField(
        db_column="LecturerID", blank=True, null=True
    )  # Field name made lowercase.
    lecturerrole_id = models.IntegerField(
        db_column="LecturerRole_ID", blank=True, null=True
    )  # Field name made lowercase.
    examdate = models.DateTimeField(
        db_column="ExamDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl3CourseAllocations"
        unique_together = (("lecturerid", "course_id", "semesternumber"),)


class Tbl3Uploadholder(models.Model):
    id = models.IntegerField(
        db_column="ID", primary_key=True
    )  # Field name made lowercase.
    studentregno = models.CharField(
        db_column="StudentRegNo", max_length=25, blank=True, null=True
    )  # Field name made lowercase.
    studentlevel = models.IntegerField(
        db_column="StudentLevel", blank=True, null=True
    )  # Field name made lowercase.
    cascore = models.IntegerField(
        db_column="CAScore", blank=True, null=True
    )  # Field name made lowercase.
    examscore = models.IntegerField(
        db_column="ExamScore", blank=True, null=True
    )  # Field name made lowercase.
    totalscore = models.IntegerField(
        db_column="TotalScore", blank=True, null=True
    )  # Field name made lowercase.
    lettergrade = models.CharField(
        db_column="LetterGrade", max_length=5, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tbl3UploadHolder"
