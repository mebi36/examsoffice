import re
import json
from typing import Any, Callable, ClassVar, Dict, List, Optional, Union

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.db.models.query import QuerySet
from django.forms import Form
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import generic
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.core.frame import DataFrame
import numpy as np

from results import models as ex
from results.forms import (
    CourseResultDeletionForm,
    ResultCollationBySessionAndLevelOfStudyForm,
    ResultFileUploadForm,
    ResultFileUploadFormatOptionForm,
    ResultForm,
    UnmoderatedResultDirectorySelectionForm,
)
from results.models import Result, Student
from results.utils import (
    possible_graduands_wb,
    student_transcript,
    class_result_spreadsheet,
    collated_results_spreadsheet,
    class_failure_spreadsheet,
    class_of_degree_spreadsheet,
)


@method_decorator(login_required, name="dispatch")
class ResultObjectUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """View to edit a result object."""

    permission_required = "results.change_result"
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
            context["form"] = ResultForm(
                initial={"student_reg_no": student_reg_no}
            )
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
        student = ex.Student.objects.filter(
            student_reg_no=result.student_reg_no
        )

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
        res = Result.objects.filter(
            student_reg_no=student_reg_no
        ).select_related("course", "semester")
        return res

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["student"] = get_object_or_404(
            ex.Student, student_reg_no=self.kwargs["reg_no"].replace("_", "/")
        )
        context["courses"] = ex.Course.objects.all().order_by("course_code")
        context["semesters"] = ex.SemesterSession.objects.all().order_by("-desc")
        return context


@method_decorator(login_required, name="dispatch")
class ResultListView(generic.ListView):
    """View for listing result objects.

    Will list a subset of recent results by default. Will
    accept query params to list a more specific set of results.
    """

    template_name: str = "results/result_obj_list.html"

    def get_queryset(self) -> QuerySet:
        qs = (
            Result.objects.all()
            .select_related("semester", "course")
            .order_by("-id")
        )

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
        ex.Result.objects.all()
        .order_by("-id")
        .select_related("course", "semester")
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
        course = self.request.GET.get("course")

        qs = Result.objects.all()

        if session:
            qs = qs.filter(semester__session=session)
        if level:
            qs = qs.filter(course__course_level=level)
        if course:
            qs = qs.filter(course__id=course)
        qs = qs.values(
            "course__course_title", "course__course_code", "semester__desc"
        )
        if not qs.exists():
            return []

        df = pd.DataFrame(qs)
        grouped_df = df.groupby(["course__course_code", "semester__desc"])
        df_with_count = grouped_df.agg(np.size)
        grouped_dict = df_with_count.to_dict("dict")["course__course_title"]
        grouped_list = [[k, v] for (k, v) in grouped_dict.items()]
        return grouped_list

    def render_to_response(self, context, **response_kwargs):
        """
        If the client requests JSON return a JsonResponse instead of
        rendering HTML.
        """
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest" or self.request.headers.get("accept") == "application/json":
            data = self.get_queryset()
            return JsonResponse({"results": data}, safe=False)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["levels"] = ex.LevelOfStudy.objects.all().filter(level__lte=5)
        context["sessions"] = ex.Session.objects.all().order_by("-session")
        return context


# Views for bulk result operations like:
# class result uploads
# deletion of entire results for a particular session
# =====================================================================
@csrf_exempt
@require_http_methods(["POST"])
def preview_result_file(request):
    file = request.FILES["result_file"]
    if not file:
        return JsonResponse({"success": False, "error": "No file uploaded"}, status=400)

    try:
        df = pd.read_excel(file)
    except Exception as exc:
        return JsonResponse({"success": False, "error": f"Problem reading excel file {exc}"}, status=400)
    if "Student Registration Number" not in df.columns or "Grade" not in df.columns:
        try:
            df = pd.read_excel(file, header=None)
        except Exception as exc:
            return JsonResponse({"success": False, "error": f"Problem reading excel file {exc}"}, status=400)
        results_row_df = pd.DataFrame()
        reg_no_col = None

        # find reg number column
        for col in df.columns:
            try:
                df_gen = (
                    df[df[col].str.contains(
                        pat="^[0-9]{4}\/[0-9]{6}",
                        regex=True,
                        na=False
                    )]
                )
            except Exception as exc:
                continue
                

            if not df_gen.empty:
                reg_no_col = col
                results_row_df = df_gen
                break
        
        valid_grade_vals = Result.VALID_GRADES + ["FF"]
        expected_grade_col = None

        for col in range(reg_no_col+1, max(list(results_row_df.columns))+1):
            try:
                if not is_string_dtype(results_row_df[col]):
                    continue
            except Exception as exc:
                return JsonResponse(
                    {"success": False, "error": f"Problem processing file. {exc}"},
                    status=400
                )

            results_row_df[col] = results_row_df[col].apply(lambda x: str(x).strip().upper())
            results_row_df["grade_checker"] = results_row_df[col].apply(lambda x: x in valid_grade_vals)
            if results_row_df["grade_checker"].sum() >= len(results_row_df) * 0.75:
                expected_grade_col = col
                results_row_df.rename(
                    columns={expected_grade_col: "letter_grade", reg_no_col: "reg_no"},
                    inplace=True
                )
                results_row_df["letter_grade"] = results_row_df["letter_grade"].replace("FF", "F")
                results_row_df = results_row_df[results_row_df["grade_checker"]]
                results_row_df = results_row_df[["reg_no", "letter_grade"]]
                break
        
        if "letter_grade" not in results_row_df:
            return JsonResponse({"success": False, "error": "Grades not detected in uploaded file"}, status=400)
    else:
        results_row_df = df
        results_row_df.rename(
            columns={
                "Student Registration Number": "reg_no",
                "Grade": "letter_grade"
            },
            inplace=True
        )
        if "Exam Score" in df.columns and "CA Score" in df.columns:
            results_row_df.rename(
                columns={"Exam Score": "exam_score", "CA Score": "ca_score"},
                inplace=True
            )
    
    rows = []
    valid_grade_vals = Result.VALID_GRADES + ["FF"]
    common_reg_no_len = results_row_df["reg_no"].str.len().mode()[0]
    for row in results_row_df.itertuples():
        row_dict = {"reg_no": row.reg_no.strip(), "letter_grade": row.letter_grade.strip(), "error": None}
        if row_dict["reg_no"] is None:
            row_dict["error"] = "MISSING REGISTRATION NUMBER"
        if " " in row_dict["reg_no"]:
            row_dict["error"] = "REGISTRATION NUMBER CONTAINS SPACES"
        if len(row_dict["reg_no"]) != common_reg_no_len:
            row_dict["error"] = "INVALID REGISTRATION NUMBER"
        if re.search(r"^[0-9]{4}/[0-9]{6}$", row_dict["reg_no"]) is None:
            row_dict["error"] = "INVALID REGISTRATION NUMBER"
        if row_dict["letter_grade"] is None:
            row_dict["error"] = "MISSING GRADE"
        if row_dict["letter_grade"] not in valid_grade_vals:
            row_dict["error"] = "GRADE NOT RECOGNIZED. WILL NOT APPEAR ON TRANSCRIPTS"
        if any([existing_row["reg_no"] == row_dict["reg_no"] for existing_row in rows]):
            row_dict["error"] = "DUPLICATE REGISTRATION NUMBER"
        rows.append(row_dict)
    return JsonResponse({
        "columns": ["reg_no", "letter_grade", "error"],
        "rows": rows
    })


def result_upload_file_format(request, upload_type: int):
    if upload_type == 1:
        columns = [
        "Student Registration Number",
        "Grade",
    ]
    elif upload_type == 2:
        columns = [
            "Student Registration Number",
            "CA Score",
            "Exam Score",
            "Grade",
        ]
    else:
        return HttpResponseBadRequest("Invalid upload_type specified.")
    response = HttpResponse(
        content_type="application/ms-excel",
        headers={
            "Content-Disposition": 'attachment; filename="resultformat.xlsx"'
        },
    )
    wb = Workbook()
    ws = wb.worksheets[0]
    ws.title = "Format"
    row_num = 0
    for col_num in range(len(columns)):
        c = ws.cell(row=row_num+1, column=col_num+1)
        c.value = columns[col_num]
    wb.save(response)
    return response


@method_decorator(login_required, name="dispatch")
class ResultUploadFormView(generic.FormView):
    """Accepts result excel files."""

    template_name = "results/upload_result_file.html"
    form_class = ResultFileUploadForm

    def form_valid(self, form: Form):
        excel_file = self.request.FILES["result_file"]
        try:
            df = pd.read_excel(excel_file, header=None)
        except Exception as exc:
            return JsonResponse({"error": f"Problem reading excel file {exc}"}, status=400)

        results_row_df = pd.DataFrame()
        reg_no_col = None

        # find reg number column
        for col in df.columns:
            try:
                df_gen = (
                    df[df[col].str.contains(
                        pat="^[0-9]{4}\/[0-9]{6}",
                        regex=True,
                        na=False
                    )]
                )
            except Exception as exc:
                continue
                

            if not df_gen.empty:
                reg_no_col = col
                results_row_df = df_gen
                break
        
        valid_grade_vals = Result.VALID_GRADES + ["FF"]
        expected_grade_col = None

        for col in range(reg_no_col+1, max(list(results_row_df.columns))+1):
            try:
                if not is_string_dtype(results_row_df[col]):
                    continue
            except Exception as exc:
                return JsonResponse({"error": f"Problem processing file. {exc}"}, status=400)

            results_row_df[col] = results_row_df[col].apply(lambda x: str(x).strip().upper())
            results_row_df["grade_checker"] = results_row_df[col].apply(lambda x: x in valid_grade_vals)
            if results_row_df["grade_checker"].sum() >= len(results_row_df) * .75:
                expected_grade_col = col
                results_row_df.rename(
                    columns={expected_grade_col: "letter_grade", reg_no_col: "reg_no"},
                    inplace=True
                )
                results_row_df["letter_grade"] = results_row_df["letter_grade"].replace("FF", "F")
                results_row_df = results_row_df[results_row_df["grade_checker"]]
                results_row_df = results_row_df[["reg_no", "letter_grade"]]
                break
        
        if "letter_grade" not in results_row_df:
            return JsonResponse({"error": "Grades not detected in uploaded file"}, status=400)
        course = form.cleaned_data["course"]
        semester = form.cleaned_data["semester"]
        invalid_results_df = pd.DataFrame()
        results_row_df["reg_no"] = results_row_df["reg_no"].str.strip()
        results_row_df["letter_grade"] = results_row_df["letter_grade"].str.strip().str.upper()
        results_row_df = results_row_df.drop_duplicates(subset=["reg_no"], keep="first")

        # ensure all reg nos are of the same length
        results_row_df["reg_no_len"] = results_row_df["reg_no"].str.len()
        results_row_df["reg_no_common_len"] = results_row_df["reg_no_len"].mode()[0]
        reg_no_common_len = results_row_df["reg_no_len"].mode()[0]
        invalid_results_df = results_row_df[results_row_df["reg_no_len"] != results_row_df["reg_no_common_len"]]
        results_row_df = results_row_df[results_row_df["reg_no_len"] == results_row_df["reg_no_common_len"]]
        invalid_results_df["error"] = "INVALID REGISTRATION NUMBER"

        for index, row in results_row_df.iterrows():
            if len(row["reg_no"]) != reg_no_common_len or " " in row["reg_no"] or not re.fullmatch(r"[0-9/]+", row["reg_no"]) or len(row["reg_no"].split("/")) != 2:
                offending_row = row.append(
                    pd.Series({"error": "INVALID REGISTRATION NUMBER"})
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
                        letter_grade=row["letter_grade"].upper()
                    )
                except ValidationError:
                    offending_row = row.append(
                        pd.Series({
                            "error": "STUDENT ALREADY HAS A RESULT FOR SELECTED COURSE AND SESSION."
                        })
                    )
                    invalid_results_df = invalid_results_df.append(
                        offending_row, ignore_index=True
                    )
            else:
                ex.Result.objects.update_or_create(
                    student_reg_no=row["reg_no"],
                    course=course,
                    semester=semester,
                    defaults={"letter_grade": row["letter_grade"].upper()},
                )
        if len(invalid_results_df) > 0:
            return JsonResponse(
                {
                    "message": "Upload complete with some invalid rows.",
                    "invalid_rows": invalid_results_df.to_dict("records"),
                },
                status=207
            )
        else:
            return JsonResponse(
                {
                    "message": "Upload complete.",
                    "redirect_url": f"{reverse('results:list')}?course={course.course_code}&semester={semester.desc}"
                }
            )


@method_decorator(login_required, name="dispatch")
class CourseResultDeleteFormView(generic.FormView):
    """View to delete course results for a given session/semester."""

    template_name: str = "results/delete_by_session.html"
    form_class = CourseResultDeletionForm

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        course = form.cleaned_data["course"]
        semester = form.cleaned_data["semester"]
        queryset = ex.Result.objects.all().filter(
            course=course, semester=semester
        )
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

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
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
            messages.error(
                request, "Student has no results.", extra_tags="text-danger"
            )
            return HttpResponseRedirect(student.get_absolute_url())

        result_sessions = list(
            student_results.values_list(
                "semester__session", flat=True
            ).distinct()
        )

        if required_sessions:
            selected_sessions = [
                x for x in required_sessions if x in result_sessions
            ]

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

                first_sem_df["weight"] = first_sem_df[
                    "course_id__credit_load"
                ] * [
                    ex.Result.GRADE_WEIGHTS[x]
                    for x in first_sem_df["letter_grade"]
                ]
                results_for_session["first"] = first_sem_df
            if len(second_sem_res) > 0:
                second_sem_df = DataFrame(list(second_sem_res))
                second_sem_df.rename(
                    columns={k: v for (k, v) in enumerate(required_fields)},
                    inplace=True,
                )
                second_sem_df["weight"] = second_sem_df[
                    "course_id__credit_load"
                ] * [
                    ex.Result.GRADE_WEIGHTS[x]
                    for x in second_sem_df["letter_grade"]
                ]
                results_for_session["second"] = second_sem_df
            transcript_body[session] = results_for_session
        transcript_data["transcript_body"] = transcript_body
        print(
            "This is the transcript body: ", transcript_data["transcript_body"]
        )
        wb = student_transcript(transcript_data)

        file_name = (
            f'Academic Transcript of {student.full_name.replace(",","")}.xlsx'
        )
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
        .values_list(
            "student_reg_no", "mode_of_admission_id__mode_of_admission"
        )
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

    class_reg_no: List[str] = list(
        class_query.values_list("student_reg_no", flat=True)
    )
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
def possible_grads_with_class_of_degree(
    request: HttpRequest, expected_yr_of_grad: str
) -> HttpResponse:
    file_name: str = f"Class of {expected_yr_of_grad} class of degree.xlsx"
    return generic_class_info_handler(
        request,
        expected_yr_of_grad,
        file_name,
        spread_sheet_method=class_of_degree_spreadsheet,
    )


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


def result_collation(
    request: HttpRequest, session: str, level: str
) -> HttpResponse:
    """This view will take two args: level of study and session.
    Using these, it will produce a file response (excel worksheet) of all
    available results for the given session and level of study"""

    session = session.replace("_", "/")
    try:
        level_of_study = int(level)
    except ValueError:
        return HttpResponseBadRequest("Invalid Arg(s) provided")
    student_info = ex.Student.objects.filter(
        student_reg_no=OuterRef("student_reg_no")
    )
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


class UnmoderatedResultAnalysis(generic.FormView):
    """Analyze results without persisting them in the production database."""
    template_name: str = "results/unmoderated_results_form.html"
    form_class: Form = UnmoderatedResultDirectorySelectionForm

    def form_valid(self, form: Form) -> HttpResponse:
        res_dir: str = form.cleaned_data["results_directory"]


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
def possible_graduands(
    request: HttpRequest, expected_yr_of_grad: str
) -> HttpResponse:

    try:
        wb = possible_graduands_wb(expected_yr_of_grad)
    except ValueError as e:
        messages.error(request, e, extra_tags="text-danger")
        return HttpResponseRedirect(
            reverse(
                "graduation_classes:info",
                kwargs={"expected_yr_of_grad": expected_yr_of_grad},
            )
        )

    file_name = f"{expected_yr_of_grad} List of Possible graduands.xlsx"
    response = HttpResponse(
        content=save_virtual_workbook(wb), content_type="application/ms-excel"
    )
    response["Content-Disposition"] = f"attachment; filename={file_name}"
    return response


# API Views for results
def results_list(request):
    try:
        qs = Result.objects.values("id", "student_reg_no", "letter_grade", "course__course_code", "course__course_title", "semester__desc").order_by("-id")
        if (course := request.GET.get("course")) and (
                session := request.GET.get("semester")
            ):
                qs = qs.filter(course__course_code=course, semester__desc=session)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
    return JsonResponse(list(qs), safe=False)


@require_http_methods({"POST"})
def update_result(request, pk):
    result = get_object_or_404(Result, pk=pk)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    try:
        grade = body.get("grade")
        result.letter_grade = grade
        result.save()
    except Exception as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=500)
    return JsonResponse({"success": True})


@require_http_methods({"POST"})
def create_result(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
    student_reg_no = body.get("student")
    grade = body.get("grade")
    course = body.get("course")
    semester = body.get("semester")

    if not all([student_reg_no, grade, course, semester]):
        return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)
    
    try:
        ex.Result.objects.create(
            student_reg_no=student_reg_no,
            letter_grade=grade,
            course_id=course,
            semester_id=semester
        )
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": True})


@require_http_methods(["DELETE"])
def delete_result(request, pk):
    result = get_object_or_404(Result, pk=pk)
    try:
        result.delete()
    except Exception as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=500)
    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def bulk_delete_results(request):

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    ids = body.get("ids", [])
    if not isinstance(ids, list):
        return JsonResponse({"success": False, "error": "Invalid data format"}, status=400)
    Result.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def delete_entire_semester_result(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    course_code = body.get("course_code", None)
    semester = body.get("semester", None)
    if course_code is not None and semester is not None:
        try:
            Result.objects.filter(course__course_code=course_code, semester__desc=semester).delete()
        except Exception as exc:
            return JsonResponse({"success": False, "error": str(exc)}, status=500)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Specify Course and Semester"}, status=400)


def aggregated_results_json(request):
    view = AggregatedResultsListView()
    view.request = request
    data = view.get_queryset()

    results = [
        {
            "course_code": course_code,
            "semester": semester,
            "count": count,
        }
        for (course_code, semester), count in data
    ]
    return JsonResponse({"results": results})


def download_by_session(request):
    course = request.GET.get("course")
    session = request.GET.get("semester")
    if not course or not session:
        return JsonResponse({"success": False, "error": "Course and semester must be provided"}, status=400)
    qs = Result.objects.filter(course__course_code=course, semester__desc=session).select_related("semester", "course").order_by("-id")
    if not qs.exists():
        return JsonResponse({"success": False, "error": "No results found for the specified course and semester"}, status=400)
    df = pd.DataFrame(list(qs.values("student_reg_no", "letter_grade")))
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="Results-{course}-{session}.csv"'
        },
    )
    df.to_csv(response, index=False)
    return response
