from . import models as ex

def get_student_records(reg_no):
    queryset = ex.Tbl1StudentResults.objects.all().select_related(
                                'course_id', 'semester_number').filter(
                                student_reg_no=reg_no).order_by(
                                    'semster_number')
    student_records = queryset.values_list('course_id_id__course_title', 
                    'course_id_id__course_code', 'course_id_id__credit_load', 
                    'course_id_id__course_level','semester_number_id__semster', 
                    'student_reg_no', 'letter_grade', )
    # student_bio_data = ex.Tbl1StudentBios
# def format_student_records(records, new_row=1, serial_number=1):

#     if records.empty:
#         new_row=new_row - 1
#         return

#     semesters = records['semester'].unique()