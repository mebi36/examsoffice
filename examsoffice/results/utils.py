import os
from results.models import Lecturer

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import (Alignment, PatternFill, Font, Border, Side)
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.pagebreak import Break
from django.templatetags.static import static


normal_border = Border(left=Side(style='thin'),
                                right=Side(style='thin'),
                                top=Side(style='thin'),
                                bottom=Side(style='thin'),)

def _merge_row_wise(worksheet, row, col_start, col_end):
    cell_start = get_column_letter(col_start)+str(row)
    cell_stop = get_column_letter(col_end)+str(row)
    _range = f"{cell_start}:{cell_stop}"
    worksheet.merge_cells(_range)

def _merge_col_wise(worksheet, col, row_start, row_end):
        cell_start = get_column_letter(col)+str(row_start)
        cell_stop = get_column_letter(col)+str(row_end)
        _range = f"{cell_start}:{cell_stop}"
        worksheet.merge_cells(_range)

def failed_courses_breakdown(df):
    # collating and writing outstanding/failed courses
    failed_courses = df.loc[df['grade'] == 'F']
    failed_courses = failed_courses['course_code'].tolist()
    failed_courses = list(set(failed_courses))
    failed_courses_copy = failed_courses.copy()
    outstanding_credit_load = 0
    outstanding_cred_1st = 0
    outstanding_cred_2nd = 0
    failed_courses_first = []
    failed_courses_second = []
    
    for course in failed_courses_copy:
        if df.loc[(df['grade'] != 'F') & (df['course_code'] == course)].empty:
            if 'First' in df.query(
                            'course_code == @course')['semester'].iloc[0]:
                outstanding_cred_1st = outstanding_cred_1st + df.query(
                            'course_code == @course')['credit_load'].iloc[0]
                failed_courses_first.append(course)
            else:
                outstanding_cred_2nd = outstanding_cred_2nd + df.query(
                            'course_code == @course')['credit_load'].iloc[0]
                failed_courses_second.append(course)
            outstanding_credit_load = outstanding_credit_load + df.query(
                            'course_code == @course')['credit_load'].iloc[0]
        else:
            failed_courses.remove(course)
    
    return {'failed_courses_first': failed_courses_first, 
            'failed_courses_second': failed_courses_second, 
            'outstanding_cred_1st': outstanding_cred_1st,
            'outstanding_cred_2nd': outstanding_cred_2nd, 
            'outstanding_credit_load': outstanding_credit_load, 
            'failed_courses': failed_courses}
    
def student_transcript(transcript_data):
    file_path = ["static","excel_templates","transcript_template.xlsx"]
    wb = load_workbook(os.path.join(*file_path))
    ws = wb.active

    #writing the biodata block
    bio_info = ["ACADEMIC TRANSCRIPT OF", 
                "REGISTRATION NUMBER: ", 
                "LEVEL OF STUDY: "]
    row = 9
    col = 5
    # writing result block
    student_bio = transcript_data['student_bio']
    result_columns = [1,5,14,37,47,55,62]
    for idx, el in enumerate(bio_info):
        _ = ws.cell(row=row+idx, column=col, value=el)
        _.font = Font(bold=True)
        _merge_row_wise(ws, row=(row+idx), col_start=col, col_end=(col+18))

        _ = ws.cell(row=(row+idx), column=(col+19), value=student_bio[idx])
        _.font = Font(bold=True)
        _.border = Border(bottom=Side(style='thin'))
        _.alignment = Alignment(horizontal='center')
        _merge_row_wise(ws, row=row+idx, col_start=(col+19), col_end=(col+50))

    row = 13
    col = 1
    result_dict = transcript_data['transcript_body']

    credit_sum = 0
    weight_sum = 0
    for session, results in  result_dict.items():
        semesters = [x for x in results.keys()]
        
        credit_sem_sum = 0
        weight_sem_sum = 0
        for semester in semesters:
            df = results[semester]
            if len(df.index) == 0:
                continue
            res_headings = ['SN', 'Course Code', 'Course Title', 'Unit Load',
                            'Grade', 'Grade Point']
            
            res_df = df[['course_id__course_code',
                            'course_id__course_title','course_id__credit_load',
                            'letter_grade', 'weight']]
            semester_title = (f"{df['semester_id__desc'].iloc[0]} ({df['course_id__course_level'].max()}/5)")
            credit_sem_sum = df['course_id__credit_load'].sum()
            weight_sem_sum = df['weight'].sum()
            sem_gpa = round(weight_sem_sum/credit_sem_sum, 2)

            credit_sum += credit_sem_sum
            weight_sum += weight_sem_sum

            # preparing result for writing to excel
            df_rows = dataframe_to_rows(res_df, index=False, header=False)
            
            # printing semester title
            _ = ws.cell(row=row,column=1,value=semester_title)
            _.font = Font(bold=True)
            _.alignment = Alignment(horizontal='center')
            _merge_row_wise(ws, row=row,col_start=1,col_end=result_columns[-1])
            row += 1

            for c_idx, header in enumerate(res_headings):
                _ = ws.cell(row=row, column=result_columns[c_idx], value=header)
                _.font = Font(bold=True)
                _.border = normal_border
                _.alignment = Alignment(horizontal='center')
                _merge_row_wise(ws, row=row, col_start=result_columns[c_idx],
                                    col_end=(result_columns[c_idx + 1] - 1))
            row += 1

            count = 1
            for r_idx, df_row in enumerate(df_rows, row):
                _ = ws.cell(row=r_idx, column=result_columns[0], value=count)
                _.border = normal_border
                _merge_row_wise(ws, r_idx, col_start=result_columns[0],
                                                col_end=(result_columns[1]-1))
                count += 1
                for c_idx, df_value in enumerate(df_row, 1):
                    _ = ws.cell(row=r_idx, column=result_columns[c_idx], 
                                                            value=df_value)
                    _.alignment = Alignment(horizontal='center', wrap_text=True)
                    _.border = normal_border
                    _merge_row_wise(ws, r_idx, col_start=result_columns[c_idx],
                                    col_end=(result_columns[(c_idx+1)]-1))
            
            for index, i in enumerate(result_columns):
                _ = ws.cell(row=(r_idx+1), column=i)
                _.border = normal_border
                if index == 6:
                    _merge_row_wise(ws, row=(r_idx+1), col_start=i, col_end=(i + 4))
                else:
                    _merge_row_wise(ws, row=(r_idx+1), col_start=i,
                                        col_end=(result_columns[index+1]-1))
            _ = ws.cell(row=(r_idx+1), column=result_columns[3], value=credit_sem_sum)
            _.font = Font(bold=True)
            _.alignment = Alignment(horizontal='center')

            _ = ws.cell(row=(r_idx+1),column=result_columns[5], value=weight_sem_sum)
            _.font = Font(bold=True)
            _.alignment = Alignment(horizontal='center')

            _ = ws.cell(row=(r_idx+1),column=result_columns[6], value=sem_gpa)
            _.alignment = Alignment(horizontal='center')
            _.font = Font(bold=True)


            row = r_idx + 4
        _ = ws.cell(row=(r_idx+2), column=result_columns[5], value='CGPA')
        _.font = Font(bold=True)
        _.alignment = Alignment(horizontal='center')

        _ = ws.cell(row=(r_idx+2), column=result_columns[6], value=round(weight_sum/credit_sum, 2))
        _.font = Font(bold=True)
        _.border = Border(bottom=Side(style='thick'))
        _merge_row_wise(ws, row=(r_idx+2), col_start=result_columns[6], col_end=(result_columns[6]+4))    
        ws.row_breaks.append(Break(id=r_idx+2))

    hod_name = Lecturer.objects.get(head_of_dept=True).get_full_name()
    ws.HeaderFooter.differentFirst = False
    ws.oddFooter.left.text = '&BHead of Dept.: '+'&U'+hod_name + '  &U&B\n'
    ws.oddFooter.center.text = '&BSign:__________________&B\n'
    ws.oddFooter.right.text = '&BDate:__________________&B\nPage &[Page] of &[Pages]'
    return wb

    