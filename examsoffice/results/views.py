import csv
from datetime import date
from typing import Any, Callable, ClassVar, Dict, List, Optional, Union

from django.http import HttpResponse, HttpRequest
from django.db.models.query import QuerySet
from django.forms import Form
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.db.models import OuterRef, Subquery, Value, Count
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np

from results import models as ex
from results.forms import (
    CourseResultDeletionForm,
    GraduationSetResultSpreadsheetForm,
    GraduationSetSearchForm,
    ResultCollationBySessionAndLevelOfStudyForm,
    ResultFileUploadForm,
    ResultFileUploadFormatOptionForm,
    ResultForm,
)
from results.models import Result
from results.utils import (
    possible_graduands_wb,
    student_transcript,
    class_result_spreadsheet,
    collated_results_spreadsheet,
    class_failure_spreadsheet,
)


@method_decorator(login_required, name="dispatch")
class ResultObjectUpdateView(generic.UpdateView):
    """View to edit a result object."""

    model = Result
    template_name = "results/edit_result.html"
    form_class = ResultForm


@method_decorator(login_required, name="dispatch")
class ResultObjectDetailView(generic.DetailView):
    """View to display details of a result object."""

    model = Result
    template_name: str = "results/result_detail.html"


@method_decorator(login_required, name="dispatch")
class ResultCreateView(generic.CreateView):
    "A view for creating a new result object"
    form_class = ResultForm
    template_name: str = "results/add_result.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if "reg_no" in self.kwargs:
            student_reg_no: str = self.kwargs["reg_no"].replace("_", "/")
            context["form"] = ResultForm(initial={"student_reg_no": student_reg_no})
        return context

    def get_success_url(self) -> str:
        if "reg_no" in self.kwargs:
            return reverse(
                "results:student-records",
                kwargs={"reg_no": self.kwargs["reg_no"]},
            )
        return super().get_success_url()


@method_decorator(login_required, name="dispatch")
class ResultDeleteView(generic.DeleteView):
    """Delete a result object."""

    template_name = "results/delete.html"
    model = Result

    def get_success_url(self) -> str:
        if next_url := self.request.GET.get("next"):
            return next_url

        result = Result.objects.get(pk=self.kwargs["pk"])
        student = ex.Student.objects.filter(student_reg_no=result.student_reg_no)

        if student.exists():
            return student.first().get_records_url()
        else:
            return reverse("results:list_results")


@method_decorator(login_required, name="dispatch")
class StudentAcademicRecordsListView(generic.ListView):
    """Display results for student with a given registration number."""

    template_name: str = "results/student_records.html"

    def get_queryset(self) -> QuerySet:
        student_reg_no = self.kwargs["reg_no"].replace("_", "/")
        return Result.objects.filter(student_reg_no=student_reg_no).select_related(
            "course", "semester"
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["student"] = get_object_or_404(
            ex.Student, student_reg_no=self.kwargs["reg_no"].replace("_", "/")
        )
        return context


@method_decorator(login_required, name="dispatch")
class ResultListView(generic.ListView):
    """View for listing result objects.

    Will list a subset of recent results by default. Will
    accept query params to list a more specific set of results.
    """

    template_name: str = "results/result_obj_list.html"

    def get_queryset(self) -> QuerySet:
        qs = Result.objects.all().select_related("semester", "course").order_by("-id")

        if (course := self.request.GET.get("course")) and (
            session := self.request.GET.get("semester")
        ):
            qs = qs.filter(course__course_code=course, semester__desc=session)
            return qs

        return qs[:100]


@login_required
def recent_results_bulk(request: HttpRequest) -> HttpResponse:
    """This view will find results for the  last N unique courses
    uploaded to the db."""
    qs: QuerySet = (
        ex.Result.objects.all().order_by("-id").select_related("course", "semester")
    )
    course_count: int = 0
    for idx, entry in enumerate(qs):
        if idx != 0 and qs[idx].course != qs[idx - 1].course:
            course_count += 1
        if course_count == 26:
            break
    min_id: Any = qs[idx].id
    final_qs: QuerySet = (
        ex.Result.objects.all()
        .filter(id__gt=min_id)
        .order_by("-id")
        .values("course__course_title", "course__course_code", "semester__desc")
    )
    df: DataFrame = pd.DataFrame(final_qs)
    grouped = df.groupby(["course__course_code", "semester__desc"], sort=False)
    new_df: DataFrame = grouped.agg(np.size)
    grouped_dict = new_df.to_dict("dict")["course__course_title"]
    template: str = "results/recent_results_bulk.html"
    return render(request, template, {"qs": grouped_dict})


@method_decorator(login_required, name="dispatch")
class AggregatedResultsListView(generic.ListView):
    """Display available results aggregated by course and semester."""

    template_name: str = "results/aggregated_result_list.html"
    paginate_by: int = 20

    def get_queryset(self) -> List[List[str]]:
        session = self.request.GET.get("session")
        level = self.request.GET.get("level")

        qs = Result.objects.all()

        if session:
            qs = qs.filter(semester__session=session)
        if level:
            qs = qs.filter(course__course_level=level)

        qs = qs.values("course__course_title", "course__course_code", "semester__desc")

        df = pd.DataFrame(qs)
        grouped_df = df.groupby(["course__course_code", "semester__desc"])
        df_with_count = grouped_df.agg(np.size)
        grouped_dict = df_with_count.to_dict("dict")["course__course_title"]
        grouped_list = [[k, v] for (k, v) in grouped_dict.items()]
        return grouped_list

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["levels"] = ex.LevelOfStudy.objects.all().filter(level__lte=5)
        context["sessions"] = ex.Session.objects.all().order_by("-session")
        return context


# Views for bulk result operations like:
# class result uploads
# deletion of entire results for a particular session
# =====================================================================
@method_decorator(login_required, name="dispatch")
class ResultFileFormatFormView(generic.FormView):
    """Present user with choices of valid result file formats system accepts."""

    RESULT_FILE_COL_WITH_SCORES: ClassVar[List[str]] = [
        "Student Registration Number",
        "CA Score",
        "Exam Score",
        "Grade",
    ]
    RESULT_FILE_COL_NO_SCORES: ClassVar[List[str]] = [
        "Student Registration Number",
        "Grade",
    ]
    template_name: str = "results/result_upload_format.html"
    form_class = ResultFileUploadFormatOptionForm

    def form_valid(self, form: Form) -> HttpResponse:
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="resultformat.csv"'},
        )
        writer = csv.writer(response)
        if form.cleaned_data["upload_option"] == "Upload results without scores":
            writer.writerow(self.RESULT_FILE_COL_NO_SCORES)
        elif form.cleaned_data["upload_option"] == "Upload results with scores":
            writer.writerow(self.RESULT_FILE_COL_WITH_SCORES)
        return response


@method_decorator(login_required, name="dispatch")
class ResultUploadFormView(generic.FormView):
    """Accepts result csv files."""

    template_name = "results/upload_result_file.html"
    form_class = ResultFileUploadForm

    def form_valid(self, form: Form) -> HttpResponse:
        try:
            df = pd.read_csv(self.request.FILES["result_file"], skipinitialspace=True)
        except:
            messages.error(self.request, "File must be a non-empty CSV file.")
            return super().form_invalid(form)

        # strip whitespaces from dataframe
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        # make a copy of dataframe
        original_df = df.copy()

        # remove rows with empty entry for any required column
        df.dropna(axis=0, inplace=True)
        if len(df) == 0:
            messages.error(
                self.request,
                "File may be missing either column headers or result entries",
                extra_tags="text-danger",
            )
            return super().form_invalid(form)

        invalid_results_df = pd.DataFrame()
        df_columns = list(df.columns)
        if df_columns == ResultFileFormatFormView.RESULT_FILE_COL_NO_SCORES:
            df.rename(
                columns={
                    "Student Registration Number": "reg_no",
                    "Grade": "grade",
                },
                inplace=True,
            )

            course = form.cleaned_data["course"]
            semester = form.cleaned_data["semester"]

            for index, row in df.iterrows():
                if not row[
                    "grade"
                ].upper() in Result.VALID_GRADES or not ex.Student.is_valid_reg_no(
                    row["reg_no"]
                ):
                    offending_row = row.append(
                        pd.Series({"error": "INVALID REG. NO. OR GRADE"})
                    )
                    invalid_results_df = invalid_results_df.append(
                        offending_row, ignore_index=True
                    )
                    continue

                if form.cleaned_data["skip_existing_rows"]:
                    try:
                        ex.Result.objects.create(
                            student_reg_no=row["reg_no"],
                            course=course,
                            semester=semester,
                            letter_grade=row["grade"].upper(),
                        )
                    except ValidationError:
                        messages.add_message(
                            self.request,
                            messages.ERROR,
                            "%s already has a result for this course and sesison"
                            % row["reg_no"],
                        )
                        offending_row = row.append(
                            pd.Series(
                                {
                                    "error": "STUDENT ALREADY HAS A RESULT FOR SELECTED COURSE AND SESSION."
                                }
                            )
                        )
                        invalid_results_df = invalid_results_df.append(
                            offending_row, ignore_index=True
                        )
                else:
                    ex.Result.objects.update_or_create(
                        student_reg_no=row["reg_no"],
                        course=course,
                        semester=semester,
                        defaults={"letter_grade": row["grade"].upper()},
                    )

        elif df_columns == ResultFileFormatFormView.RESULT_FILE_COL_WITH_SCORES:
            df.rename(
                columns={
                    "Student Registration Number": "reg_no",
                    "CA Score": "ca_score",
                    "Exam Score": "exam_score",
                    "Grade": "grade",
                },
                inplace=True,
            )
            for index, row in df.iterrows():
                if (
                    not isinstance(row["ca_score"], (int, float))
                    or not isinstance(row["exam_score"], (int, float))
                    or row["grade"].upper() not in Result.VALID_GRADES
                    or not ex.Student.is_valid_reg_no(row["reg_no"])
                ):
                    offending_row = row.append(
                        pd.Series({"error": "INVALID REG. NO, GRADE, OR SCORE"})
                    )
                    invalid_results_df = invalid_results_df.append(row)
                    continue

                if form.cleaned_data["skip_existing_rows"]:
                    try:
                        ex.Result.objects.create(
                            student_reg_no=row["reg_no"],
                            course=course,
                            semester=semester,
                            ca_score=row["ca_score"],
                            exam_score=row["exam_score"],
                            letter_grade=row["letter_grade"],
                        )
                    except ValidationError:
                        offending_row = row.append(
                            pd.Series(
                                {
                                    "error": "STUDENT ALREADY HAS A RESULT FOR SELECTED COURSE AND SESSION."
                                }
                            )
                        )
                        invalid_results_df = invalid_results_df.append(
                            offending_row, ignore_index=True
                        )
                else:
                    ex.Result.objects.update_or_create(
                        student_reg_no=row["reg_no"],
                        course=course,
                        semester=semester,
                        defaults={
                            "letter_grade": row["grade"].upper(),
                            "ca_score": row["ca_score"],
                            "exam_score": row["exam_score"],
                        },
                    )
        else:
            messages.error(
                self.request,
                "File does not comply with any of the provided result file samples.",
                extra_tags="text-danger",
            )
            return super().form_invalid(form)

        if len(invalid_results_df) > 0:
            messages.add_message(
                self.request, messages.INFO, "Upload compete with some errors"
            )
            response = HttpResponse(
                self.request,
                content_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="invalid_result_file_rows.csv"'
                },
            )
            invalid_results_df.to_csv(response)
            return response
        else:
            return HttpResponseRedirect(reverse("results:upload_result_file"))


@method_decorator(login_required, name="dispatch")
class CourseResultDeleteFormView(generic.FormView):
    """View to delete course results for a given session/semester."""

    template_name: str = "results/delete_by_session.html"
    form_class = CourseResultDeletionForm

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        course = form.cleaned_data["course"]
        semester = form.cleaned_data["semester"]
        queryset = ex.Result.objects.all().filter(course=course, semester=semester)
        obj_count = len(queryset)

        if obj_count > 0:
            queryset.delete()
            messages.success(
                self.request,
                "%d result(s) were deleted" % obj_count,
                extra_tags="text-success",
            )
        elif obj_count == 0:
            messages.error(
                self.request,
                "No results were found for course in selected session.",
                extra_tags="text-danger",
            )
        return HttpResponseRedirect(reverse("results:delete_by_session"))


@method_decorator(login_required, name="dispatch")
class StudentTranscriptGeneratorView(generic.View):
    """Generate an xls file of a student's academic records."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        reg_no = self.kwargs["reg_no"].replace("_", "/")

        required_sessions: Optional[List[str]] = None
        if request.GET.get("required_sessions"):
            required_sessions = request.GET.get("required_sessions").split(",")

        # dict for holding data for student transcript
        transcript_data: Dict[str, Any] = {}

        if not ex.Student.is_valid_reg_no(reg_no):
            return HttpResponseBadRequest("Invalid Student registration number")

        required_fields = [
            "course_id__course_code",
            "course_id__course_title",
            "course_id__course_level",
            "letter_grade",
            "semester_id__desc",
            "semester_id__session",
            "course_id__credit_load",
        ]

        student: Union[ex.Student, HttpResponse] = get_object_or_404(
            ex.Student, student_reg_no=reg_no
        )
        student_results: QuerySet = (
            ex.Result.objects.filter(student_reg_no=reg_no)
            .prefetch_related("course", "semester")
            .values_list(*required_fields)
        )

        student_bio = [student.full_name, reg_no, student.get_level_of_study()]
        transcript_data["student_bio"] = student_bio

        if not student_results.exists():
            messages.error(request, "Student has no results.", extra_tags="text-danger")
            return HttpResponseRedirect(student.get_absolute_url())

        result_sessions = list(
            student_results.values_list("semester__session", flat=True).distinct()
        )

        if required_sessions:
            selected_sessions = [x for x in required_sessions if x in result_sessions]

        # if user provided invalid academic sessions/sessions where
        # student has no result, return a transcript of all student
        # results anyway.
        if required_sessions is None or selected_sessions is None:
            selected_sessions = result_sessions

        transcript_body: Dict[str, Dict[str, DataFrame]] = {}

        for session in selected_sessions:
            results_for_session = {}
            session_res = student_results.filter(semester__session=session)
            first_sem_res = session_res.filter(semester__semester=1).order_by(
                "course__course_level"
            )
            second_sem_res = session_res.filter(semester__semester=2).order_by(
                "course__course_level"
            )

            if len(first_sem_res) > 0:
                first_sem_df = DataFrame(list(first_sem_res))
                first_sem_df.rename(
                    columns={k: v for (k, v) in enumerate(required_fields)},
                    inplace=True,
                )

                first_sem_df["weight"] = first_sem_df["course_id__credit_load"] * [
                    ex.Result.GRADE_WEIGHTS[x] for x in first_sem_df["letter_grade"]
                ]
                results_for_session["first"] = first_sem_df
            if len(second_sem_res) > 0:
                second_sem_df = DataFrame(list(second_sem_res))
                second_sem_df.rename(
                    columns={k: v for (k, v) in enumerate(required_fields)},
                    inplace=True,
                )
                second_sem_df["weight"] = second_sem_df["course_id__credit_load"] * [
                    ex.Result.GRADE_WEIGHTS[x] for x in second_sem_df["letter_grade"]
                ]
                results_for_session["second"] = second_sem_df
            transcript_body[session] = results_for_session
        transcript_data["transcript_body"] = transcript_body
        print("This is the transcript body: ", transcript_data["transcript_body"])
        wb = student_transcript(transcript_data)

        file_name = f'Academic Transcript of {student.full_name.replace(",","")}.xlsx'
        response = HttpResponse(
            content=save_virtual_workbook(wb),
            content_type="application/ms-excel",
        )
        response["Content-Disposition"] = f"attachment; filename={file_name}"

        return response


@login_required
def generic_class_info_handler(
    request: HttpRequest,
    expected_yr_of_grad: str,
    file_name: str,
    spread_sheet_method: Callable[..., Worksheet] = class_failure_spreadsheet,
) -> HttpResponse:

    class_query: QuerySet = (
        ex.Student.objects.all()
        .select_related("mode_of_admission")
        .filter(expected_yr_of_grad=expected_yr_of_grad)
        .values_list("student_reg_no", "mode_of_admission_id__mode_of_admission")
    )
    if not class_query.exists():
        messages.add_message(
            request,
            messages.ERROR,
            f"No students are currently registered with "
            f"{expected_yr_of_grad} as their year of graduation",
            extra_tags="text-danger",
        )
        return HttpResponseRedirect(reverse("index"))

    class_reg_no: List[str] = list(class_query.values_list("student_reg_no", flat=True))
    class_list: List[List[str]] = []
    for el in class_query:
        name = ex.Student.objects.get(student_reg_no=el[0]).full_name
        class_list.append([el[0], name, el[1]])

    result_qs: QuerySet = (
        ex.Result.objects.all()
        .select_related("semester", "course")
        .filter(student_reg_no__in=class_reg_no)
        .values_list(
            "course_id__course_title",
            "course_id__course_code",
            "course_id__credit_load",
            "course_id__course_level",
            "semester_id__desc",
            "letter_grade",
        )
    )

    if len(class_list) > 0:
        wb = spread_sheet_method(
            result_qs=result_qs,
            class_list=class_list,
            expected_yr_of_grad=expected_yr_of_grad,
        )
        response = HttpResponse(
            content=save_virtual_workbook(wb),
            content_type="application/ms-excel",
        )
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "No results have been uploaded for students of this level",
            extra_tags="text-danger",
        )

    return render(request, "results/class_spreadsheet.html", {})


@login_required
def class_outstanding_courses(
    request: HttpRequest, expected_yr_of_grad: str
) -> HttpResponse:
    file_name: str = f"Class of {expected_yr_of_grad} Extra Load Summary.xlsx"
    return generic_class_info_handler(request, expected_yr_of_grad, file_name)


@login_required
def class_speadsheet_generator(
    request: HttpRequest, expected_yr_of_grad: str
) -> HttpResponse:
    file_name: str = f"Class of {expected_yr_of_grad} Results.xlsx"
    return generic_class_info_handler(
        request,
        expected_yr_of_grad,
        file_name,
        spread_sheet_method=class_result_spreadsheet,
    )


def result_collation(request: HttpRequest, session: str, level: str) -> HttpResponse:
    """This view will take two args: level of study and session.
    Using these, it will produce a file response (excel worksheet) of all
    available results for the given session and level of study"""

    session = session.replace("_", "/")
    try:
        level_of_study = int(level)
    except ValueError:
        return HttpResponseBadRequest("Invalid Arg(s) provided")
    student_info = ex.Student.objects.filter(student_reg_no=OuterRef("student_reg_no"))
    qs: QuerySet = (
        ex.Result.objects.all()
        .select_related("course", "semester")
        .filter(semester__session=session, course__course_level=level_of_study)
        .annotate(
            name=Concat(
                Subquery(student_info.values("last_name")),
                Value(" "),
                Subquery(student_info.values("first_name")),
                Value(" "),
                Subquery(student_info.values("other_names")),
            )
        )
        .order_by("course__course_semester")
    )
    result_dict: Dict[int, Dict[str, Any]] = {}
    if qs.exists():
        for idx, el in enumerate(qs):
            result_dict[(idx)] = {
                "reg_no": el.student_reg_no,
                "name": el.name,
                "course_title": el.course.course_title,
                "course_code": el.course.course_code,
                "semester": el.course.course_semester.semester,
                "grade": el.letter_grade,
            }
        result_df = DataFrame(result_dict)
        result_df = result_df.transpose()
        wb = collated_results_spreadsheet(result_df)
        file_name = f"{session} Collated Results - {int(level) * 100}L.xlsx"
        response = HttpResponse(
            content=save_virtual_workbook(wb),
            content_type="application/ms-excel",
        )
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "No results found for the selected session/level of study",
        )
        return HttpResponseRedirect(reverse("results:collation"))


@method_decorator(login_required, name="dispatch")
class ResultCollationByLevelOfStudyAnsSessionFormView(generic.FormView):
    """Collated results for a specified session and level of study"""

    template_name: str = "results/result_collation_form.html"
    form_class: Form = ResultCollationBySessionAndLevelOfStudyForm

    def form_valid(self, form: Form) -> HttpResponse:
        session: str = form.cleaned_data["session"].session.replace("/", "_")
        level_of_study: str = form.cleaned_data["level_of_study"]
        next_url: str = reverse(
            "results:result_collation",
            kwargs={"session": session, "level": level_of_study},
        )
        return HttpResponseRedirect(
            reverse("index:download_info") + "?next=%s" % next_url
        )


@method_decorator(login_required, name="dispatch")
class GraduationSetResultSpreadsheetFormView(generic.FormView):
    """Generate spreadsheet of results for selected graduation set."""

    template_name: str = "results/graduationset_spreadsheet_form.html"
    form_class: Form = GraduationSetResultSpreadsheetForm

    def form_valid(self, form: Form) -> HttpResponse:
        next_url: str = reverse(
            "results:generate_class_spreadsheet",
            kwargs={"expected_yr_of_grad": form.cleaned_data["expected_yr_of_grad"]},
        )
        # TODO: could be better to processs handling of longer
        # pre-download file processing with vue to prevent impatient
        # user from continuously hitting server.
        return HttpResponseRedirect(
            reverse("index:download_info") + "?next=%s" % next_url
        )


@method_decorator(login_required, name="dispatch")
class GraduationSetOutstandingCoursesFormView(generic.FormView):
    """Generate spreadsheet of outstanding courses for selected grad set."""

    template_name: str = (
        "results/graduationset_spreadsheet_outstanding_courses_form.html"
    )
    form_class: Form = GraduationSetResultSpreadsheetForm

    def form_valid(self, form: Form) -> HttpResponse:
        next_url: str = reverse(
            "results:class_outstanding_courses",
            kwargs={"expected_yr_of_grad": form.cleaned_data["expected_yr_of_grad"]},
        )
        return HttpResponseRedirect(
            reverse("index:download_info") + "?next=%s" % next_url
        )


@login_required
def class_outstanding_courses_form(request: HttpRequest) -> HttpResponse:
    template: str = "results/spreadsheet_form.html"
    context: Dict[str, Any] = {}

    if request.method == "GET":
        expected_yrs_of_grad = sorted(
            [x for x in range(2017, (date.today().year + 5))], reverse=True
        )
        context = {"expected_yrs_of_grad": expected_yrs_of_grad}

    elif request.method == "POST":
        if request.POST["expected_yr_of_grad"]:
            try:
                expected_yr_of_grad = int(request.POST["expected_yr_of_grad"])
            except ValueError:
                return HttpResponseBadRequest("Invalid Session. Select a valid year.")
            else:
                next_url = reverse(
                    "results:class_outstanding_courses",
                    kwargs={"expected_yr_of_grad": expected_yr_of_grad},
                )
                return HttpResponseRedirect(
                    reverse("index:download_info") + "?next=%s" % next_url
                )
    return render(request, template, context)


@login_required
def transcript_download_info(request: HttpRequest, reg_no: str) -> HttpResponse:
    template: str = "results/transcript_download_info.html"
    context: Dict[str, Any] = {}
    if request.method == "GET":
        try:
            context.update(next=request.GET["next"])
        except:
            pass
    reg_no = reg_no.replace("_", "/")
    if ex.Student.is_valid_reg_no(reg_no):
        student = get_object_or_404(ex.Student, student_reg_no=reg_no)
        hod_info = get_object_or_404(ex.Lecturer, head_of_dept=True)
        context.update(student=student, hod=hod_info)
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Invalid Student Registration Number",
            extra_tags="text-danger",
        )
        HttpResponseRedirect(reverse("students:search"))
    return render(request, template, context)


@login_required
def possible_graduands(request: HttpRequest, expected_yr_of_grad: str) -> HttpResponse:

    try:
        wb = possible_graduands_wb(expected_yr_of_grad)
    except ValueError as e:
        messages.error(request, e, extra_tags="text-danger")
        return HttpResponseRedirect(reverse("results:possible_graduands_form"))

    file_name = f"{expected_yr_of_grad} List of Possible graduands.xlsx"
    response = HttpResponse(
        content=save_virtual_workbook(wb), content_type="application/ms-excel"
    )
    response["Content-Disposition"] = f"attachment; filename={file_name}"
    return response


@method_decorator(login_required, name="dispatch")
class PossibleGraduandsFormView(generic.FormView):
    """Generate a report of possible graduands for a given session."""

    form_class: Form = GraduationSetSearchForm
    template_name: str = "results/possible_graduands_form.html"

    def form_valid(self, form: Form) -> HttpResponse:
        expected_yr_of_grad = form.cleaned_data["expected_yr_of_grad"]
        return HttpResponseRedirect(
            reverse(
                "results:possible_graduands",
                kwargs={"expected_yr_of_grad": expected_yr_of_grad},
            )
        )
