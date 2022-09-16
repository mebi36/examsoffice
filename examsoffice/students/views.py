import csv
from django.db import IntegrityError
import pandas as pd
from datetime import datetime, timezone
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required

from .forms import (
    ProgressHistoryFormSet,
    StudentBioForm,
)
from .serializers import StudentSerializer
from results.serializers import ResultSerializer
from results.models import (
    LevelOfStudy,
    ModeOfAdmission,
    ModeOfStudy,
    Result,
    Student,
    Sex,
    StudentProgressHistory,
    Session,
)

STUDENT_BIO_FIELDS = [
    "student_reg_no",
    "last_name",
    "first_name",
    "other_names",
    "email",
    "phone_number",
    "sex",
    "marital_status",
    "date_of_birth",
    "town_of_origin",
    "lga_of_origin",
    "state_of_origin",
    "nationality",
    "mode_of_admission",
    "level_admitted_to",
    "mode_of_study",
    "year_of_admission",
    "expected_yr_of_grad",
    "graduated",
    "address_line1",
    "address_line2",
    "city",
    "state",
    "country",
    "class_rep",
    "current_level_of_study",
    "jamb_number",
]
# Create your views here.
def students_menu(request):
    return render(request, "students/menu.html", {})


@login_required
def search(request):
    context = {}

    if request.method == "POST":
        if Student.is_valid_reg_no(request.POST["reg_no"]):
            reg_no = request.POST["reg_no"]
            try:
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                messages.add_message(
                    request,
                    messages.INFO,
                    """No student bio data found. 
                                    Please provide student details.""",
                    extra_tags="text-primary",
                )
                return HttpResponseRedirect(
                    reverse(
                        "students:create_bio",
                        kwargs={"reg_no": reg_no.replace("/", "_")},
                    )
                )
            else:
                return HttpResponseRedirect(student.get_absolute_url())
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Invalid Student Registration Number",
                extra_tags="text-danger",
            )
            return HttpResponseRedirect(reverse("students:search"))
    else:
        if "next" in request.GET.keys():
            context = {"next": request.GET["next"]}
    return render(request, "students/reg_no_search.html", context)


@never_cache
@login_required
def edit_bio_data(request, reg_no):
    """
    This view is supposed to enable the editing of student
    bio data.
    """
    context = {}
    reg_no = reg_no.replace("_", "/")
    if request.method == "GET":
        if Student.is_valid_reg_no(reg_no):
            try:
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                messages.add_message(
                    request,
                    messages.INFO,
                    """Student not found. 
                                    Provide student info for registration
                                    """,
                    extra_tags="text-info",
                )
                return HttpResponseRedirect(
                    reverse(
                        "students:create_bio",
                        kwargs={"reg_no": reg_no.replace("/", "_")},
                    )
                )
            else:
                form = StudentBioForm(instance=student)
                context["reg_no"] = reg_no
                context["form"] = form
                context["action_url"] = reverse(
                    "students:edit_bio",
                    kwargs={"reg_no": reg_no.replace("/", "_")},
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Invalid student registration number",
                extra_tags="text-danger",
            )
            return HttpResponseRedirect(reverse("students:search"))

        if "next" in request.GET.keys():
            context.update(next=request.GET["next"])
            # print(request.GET['next'])

    # process form submission
    if request.method == "POST":
        if Student.is_valid_reg_no(reg_no):
            try:
                student = Student.objects.get(student_reg_no=reg_no)
            except:
                print("an exception occured")
            else:
                form = StudentBioForm(request.POST, instance=student)
            finally:
                if form.is_valid():
                    form.save()
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        "Student bio data update successful",
                        extra_tags="text-success",
                    )
                    if "next" in request.POST:
                        return HttpResponseRedirect(request.POST["next"])
                    return HttpResponseRedirect(reverse("students:search"))
        else:
            form = StudentBioForm(request.POST, request.FILES)
            messages.add_message(
                request,
                messages.ERROR,
                "Invalid student registration number",
                extra_tags="text-danger",
            )
    return render(request, "bio_data.html", context)


@login_required
def update_progress_history(request, reg_no):
    """This view updates a student's academic progress history."""
    context = {}
    reg_no = reg_no.replace("_", "/")

    # begin by checking validity of student reg number
    if not Student.is_valid_reg_no(reg_no):
        messages.add_message(
            request,
            messages.ERROR,
            "Invalid Student Registration Number",
            extra_tags="text-danger",
        )
        return HttpResponseRedirect(reverse("index:general_messages"))

    # also check to ensure that student has been duly registered in Student model
    try:
        student = Student.objects.get(student_reg_no=reg_no)
    except:
        messages.add_message(
            request,
            messages.ERROR,
            """No existing record found for student.
                            Provide student info for registration
                            """,
            extra_tags="text-danger",
        )
        return HttpResponseRedirect(
            reverse("students:edit_bio", args=[reg_no.replace("/", "_")])
            + "?next=%s"
            % (
                reverse(
                    "students:progress_history", args=[reg_no.replace("/", "_")]
                )
            )
        )
    else:
        context.update(student=student)

    if request.method == "GET":
        prog_hist_qs = StudentProgressHistory.objects.all().filter(
            student_reg_no=student
        )
        formset = ProgressHistoryFormSet(queryset=prog_hist_qs)

        # #some on-the-fly modifications to the form
        for form in formset:
            form.fields["student_reg_no"].initial = student

        context["formset"] = formset
        return render(request, "students/progress_history.html", context)
    elif request.method == "POST":
        formset = ProgressHistoryFormSet(request.POST)
        for form in formset:
            # don't save invalid forms
            if not form.is_valid():
                print("invalid form found!!")
                continue

            # skip empty forms
            if form.cleaned_data == {}:
                continue

            if form.cleaned_data.get("DELETE"):
                # print(form.cleaned_data.get('id').id)
                try:
                    obj = StudentProgressHistory.objects.get(
                        pk=form.cleaned_data.get("id").id
                    )
                except:
                    print("problem fetching model instance")
                else:
                    obj.delete()
                continue

            try:
                form.save()
            except IntegrityError:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Student already has an entry for selected session",
                    extra_tags="text-danger",
                )
                return HttpResponseRedirect(
                    reverse(student.get_progress_history_url())
                )
            except:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Unknown error. Try again",
                    extra_tags="text-danger",
                )
                return HttpResponseRedirect(
                    reverse(student.get_progress_history_url())
                )
            else:
                print("save successful")

        if request.POST["submit"] == "Finish":
            return HttpResponse("Formset has been validated!")
        elif request.POST["submit"] == "Save and Continue":
            return HttpResponseRedirect(student.get_progress_history_url())


@login_required
def create_bio_data(request, reg_no):

    """This view updates a student's academic progress history."""
    context = {}
    reg_no = reg_no.replace("_", "/")
    template = "bio_data.html"

    if request.method == "GET":
        form = StudentBioForm(initial={"student_reg_no": reg_no})
        try:
            Student.objects.get(student_reg_no=reg_no)
        except:
            context = {
                "form": form,
                "action_url": reverse(
                    "students:create_bio",
                    kwargs={"reg_no": reg_no.replace("/", "_")},
                ),
            }
            return render(request, template, context)
        else:
            messages.add_message(
                request,
                messages.INFO,
                "Student Bio Records Already Exists",
                extra_tags="text-primary",
            )
            return HttpResponseRedirect(
                reverse(
                    "students:edit_bio",
                    kwargs={"reg_no": reg_no.replace("/", "_")},
                )
            )
    elif request.method == "POST":
        if Student.is_valid_reg_no(reg_no):
            student = Student(student_reg_no=reg_no)
            student.save()
            student = Student.objects.get(student_reg_no=reg_no)
            form = StudentBioForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Student bio data saved",
                    extra_tags="text-success",
                )
            else:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Error processing form entries",
                    extra_tags="text-danger",
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Registration Number is invalid",
                extra_tags="text-danger",
            )
        return HttpResponseRedirect(reverse("students:search"))


def bio_update_format(request):

    if request.method == "GET":
        template = "students/bio_update_bulk.html"
        return render(request, template, {})
    if request.method == "POST":
        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="bio_update_form.csv"'
            },
        )
        writer = csv.writer(response)
        writer.writerow(STUDENT_BIO_FIELDS)
        return response


def upload_bio_file(request):
    template = "students/upload_bio_file.html"
    if request.method == "GET":
        return render(request, template, {})

    elif request.method == "POST" and request.FILES:
        # begin by checking if uploaded file is a csv file
        try:
            df = pd.read_csv(
                request.FILES["result_file"], skipinitialspace=True
            )
            # you can define a chunksize parameter in the read_csv method
            # to handle large file sizes [chunksize=1000]
        except:
            messages.add_message(
                request,
                messages.ERROR,
                "Invalid File. File must be a non-empty CSV file.",
                extra_tags="text-danger",
            )
            return HttpResponseRedirect(reverse("students:bio_update_format"))
        else:
            invalid_student_index_list = []
            # strip whitespaces from dataframe
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            df = df.astype(str)
            updated_fields = {}
            if len(df) > 0:
                # ensure all column headings are valid
                if not set(df.columns.to_list()).issubset(
                    set(STUDENT_BIO_FIELDS)
                ):
                    messages.add_message(
                        request,
                        messages.ERROR,
                        """Invalid column heading(s). 
                                        Please use the bio format without 
                                        modifying the column headings""",
                    )
                    return HttpResponseRedirect(
                        reverse("students:bio_update_format")
                    )

                for index, row in df.iterrows():
                    if Student.is_valid_reg_no(row["student_reg_no"]):
                        for field in STUDENT_BIO_FIELDS:
                            # skip student_reg_no and cells with NaN
                            if (
                                pd.isna(row[field])
                                or field == "student_reg_no"
                                or row[field] == "nan"
                            ):
                                continue
                            else:
                                col_entry = row[field]
                                if field == "sex":
                                    try:
                                        col_entry = Sex.objects.get(
                                            sex__istartswith=row[field]
                                        )
                                    except:
                                        continue
                                if field == "phone_number":
                                    col_entry = col_entry.split(".", 1)[0]
                                if field == "date_of_birth":
                                    try:
                                        col_entry = datetime.strptime(
                                            row[field], "%d/%m/%Y"
                                        )
                                    except:
                                        continue
                                    else:
                                        col_entry = col_entry.replace(
                                            tzinfo=timezone.utc
                                        )
                                if field == "level_admitted_to":
                                    try:
                                        col_entry = int(row[field])
                                    except:
                                        continue

                                if field == "mode_of_admission":
                                    try:
                                        col_entry = ModeOfAdmission.objects.get(
                                            mode_of_admission__icontains=row[
                                                field
                                            ]
                                        )
                                    except:
                                        try:
                                            col_entry = (
                                                ModeOfAdmission.objects.get(
                                                    description__icontains=row[
                                                        field
                                                    ]
                                                )
                                            )
                                        except:
                                            continue
                                if field == "mode_of_study":
                                    try:
                                        col_entry = ModeOfStudy.objects.get(
                                            mode_of_study__icontains=row[field]
                                        )
                                    except:
                                        continue
                                updated_fields[field] = col_entry
                                Student.objects.update_or_create(
                                    student_reg_no=row["student_reg_no"],
                                    defaults={field: col_entry},
                                )
                    else:
                        invalid_student_index_list.append(index + 1)

                if len(invalid_student_index_list) == 0:
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        "Update Complete",
                        extra_tags="text-success",
                    )
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Rows: {invalid_student_index_list} were not uploaded",
                        extra_tags="text-danger",
                    )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "No Bio entries found in uploaded file",
                    extra_tags="text-danger",
                )

            return render(request, template, {})


@login_required
def profile(request, reg_no):
    """
    This view will display a information about a student, 
    ranging from performance, bio-data, cgpa, results analytics 
    (grades and performance in entire class).
    """
    reg_no = reg_no.replace("_", "/")
    template = "students/profile.html"
    student = Student.objects.filter(student_reg_no=reg_no)

    if not student.exists():
        messages.error(
            "No student with that registration number was found", 
            extra_tags="text-danger"
        )
        return render(request, template, {})
    
    context = {}
    context["student_obj"] = student.first()
    context["student"] = StudentSerializer(student.first(), many=False).data
    context["results"] = ResultSerializer(Result.objects.filter(student_reg_no=reg_no), many=True).data
    return render(request, template, context)