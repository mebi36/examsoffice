from datetime import time
import os
from results.models import Lecturer, Student
from itertools import chain

import pandas as pd
from pandas.core.frame import DataFrame
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import (Alignment, PatternFill, Font, Border, Side)
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.pagebreak import Break
from openpyxl.worksheet.worksheet import Worksheet
from django.templatetags.static import static


normal_border = Border(left=Side(style='thin'),
                                right=Side(style='thin'),
                                top=Side(style='thin'),
                                bottom=Side(style='thin'),)
times_new_rom_style = Font('Times New Roman', 11)
center_align = Alignment(horizontal='center')
vertical_align_top = Alignment(vertical='top')
top_bot_text_direction = Alignment(text_rotation=255, vertical='top')

def _list_to_cell(list_var):
    final_str = ''
    if len(list_var)>0:
        for index, content in enumerate(list_var, 1):
            final_str += content
            if index != len(list_var):
                final_str += ', '
    else:
        final_str = 'No outstanding course for semester'    
    return final_str

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
    # result_columns = [1,5,14,37,47,55,62]
    result_columns = [1,4,11,44,51,55,62]
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
                                                            value=str(df_value).upper())
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

def class_result_spreadsheet(result_qs, class_list, expected_yr_of_grad):
    wb = Workbook()
    ws = wb.active

    def _format_summary_block(row, col):
            for i in range(row,(row+4)):
                _ = ws.cell(row=i, column=(col+20))
                _.fill = PatternFill(
                                fgColor="50E2F2", fill_type="solid")
                _.border = Border(left=Side(style='thick'),
                                    right=Side(style='thick'),
                                    top=Side(style='thick'),
                                    bottom=Side(style='thick'))

    def _failed_crses_block(course_list, total_cred, first_sem=False):
        
        head_fill = "First" if first_sem else "Second"
        f1_head = f'''Courses with no passing grade ({head_fill})'''
        f1_head_cell = ws.cell(row=row-1, column=(col), value=f1_head)
        _merge_row_wise(ws, row=(row-1), col_start=col, col_end=(col+19))
        f1_head_cell.font = Font(bold=True)
        f1_head_cell.alignment = center_align
        f1_head_cell.fill = PatternFill(
                                fgColor="F7C5C1", fill_type="solid")


        i=0
        j=0
        for el in course_list:
            _ = ws.cell(row=(row+i), column=(col+j), value=el)
            _.alignment = Alignment(vertical='top', textRotation=180)
            if i == 0:
                i = 1
            elif i == 1:
                _merge_col_wise(ws, col=(col+j), row_start=(row+i), 
                                        row_end=(row+3))
                
                i = 0
                j = j + 1
        for row_el in range(row, (row+4)):
            for col_el in range(col, (col+20)):
                ws.cell(row=row_el,column=col_el).border = normal_border
                ws.column_dimensions[get_column_letter(col_el)].width = 3
        
        block_title=("Cred Load of CO's (1st Sem)" if first_sem else 
                                            "Total Credit Load of CO's")
        _ = ws.cell(row=row, column=(col+20), value=block_title)
        _.alignment = Alignment(wrap_text=True)
        ws.cell(row=(row+1), column=(col+20), value=total_cred)
        _format_summary_block(row,col)

            
    ws.title = f'Class of {expected_yr_of_grad} Results'
    headers = ['SN', 'Name', 'RN','E.M']
    ws.append(headers)
    ws.freeze_panes = 'E1'
    serial_number = 1
    row = 2


    for student in class_list:
        student_qs = result_qs.filter(student_reg_no=student[0]).order_by(
                                                                'semester')
        # confirm that the student's results are available
        if len(student_qs) == 0:
            continue
        
        else:
            df = pd.DataFrame.from_records(student_qs)
            df = df.rename(columns = {0: 'course_title', 1: 'course_code', 
                                    2: 'credit_load', 3: 'course_level', 
                                    4: 'semester', 5: 'grade'})
            # df['weight'] = df['credit_load'] * [5 if x == 'A' else 4 
            #                                     if x == 'B' else 3 if 
            #                                     x == 'C' else 2 if x == 'D'
            #                                     else 1 if x == 'E' else 0 
            #                                     for x in df['grade']]
            df = Student.get_weight_col(df)
            reg_no = student[0]
            name = student[1]
            mode_of_admission = student[2] or 'N/A'
            semesters = df['semester'].unique().tolist()
            
            # writing and formatting student biodata to the excel sheet
            sn_cell = ws.cell(column=1, row=row, value=serial_number)
            sn_cell.alignment = top_bot_text_direction
            sn_cell.border = normal_border
            _merge_col_wise(ws, col=1, row_start=row, row_end=row+3)

            name_cell = ws.cell(column=2, row=row, value=name.upper())
            name_cell.alignment = Alignment(wrapText=True, vertical='top')
            name_cell.border = normal_border
            _merge_col_wise(ws, col=2, row_start=row, row_end=row+3)
            ws.column_dimensions['B'].width = 20

            reg_no_cell = ws.cell(column=3, row=row, value=reg_no)
            reg_no_cell.alignment = Alignment(
                                        textRotation=180, vertical='top')
            reg_no_cell.border = normal_border
            _merge_col_wise(ws, col=3, row_start=row, row_end=row+3)
            
            adm_mode_cell = ws.cell(column=4, row=row, 
                                        value=mode_of_admission.upper())
            adm_mode_cell.alignment = Alignment(
                                        textRotation=180, vertical='top')
            adm_mode_cell.border = normal_border
            _merge_col_wise(ws, col=4, row_start=row, row_end=row+3)

            for el in ['A', 'C', 'D']:
                ws.column_dimensions[el].width = 3
            
            # writing results to worksheet
            cred_sum = 0
            weight_sum = 0
            col = 5

            for semester in semesters:
                semester_records = df.query('semester == @semester')
                semester_records = semester_records.sort_values(
                                        'course_level', ascending=False)
                semester_records = semester_records[['course_code', 
                                    'credit_load','grade','weight']].copy()
                semester_records = semester_records.transpose()
                
                #calculating the semester CGPA&writing to the last column
                credit_sem_sum = semester_records.sum(axis=1)[1]
                weight_sem_sum = semester_records.sum(axis=1)[3]
                weight_sum = weight_sum + weight_sem_sum
                cred_sum = cred_sum + credit_sem_sum

                ws.cell(row=row, column=(col+20), value=round(
                                                    weight_sum/cred_sum,3))
                ws.cell(row=(row+1), column=(col+20), value=credit_sem_sum)
                ws.cell(row=(row+2), column=(col+20), value=round(
                                        weight_sem_sum/credit_sem_sum, 3))
                ws.cell(row=(row+3), column=(col+20), value=weight_sem_sum)
                _format_summary_block(row,col)

                #prepare result dataframe for writing to excel 
                df_rows = dataframe_to_rows(semester_records, 
                                            index=False, header=False)
                
                # working on the semester header
                ws.cell(column=col, row=(row-1), value=semester.upper())
                header_start = get_column_letter(col)+str(row-1)
                _merge_row_wise(ws, row=(row-1), col_start=col, col_end=(col+19))
                ws[header_start].alignment = center_align
                ws[header_start].fill = PatternFill(
                                    fgColor="50E2F2", fill_type="solid")
                ws[header_start].font = Font(bold=True)

                for r_idx, df_row in enumerate(df_rows, row):
                    for all_col in range(col,(col+20)):
                        _ = ws.cell(column=all_col,row=r_idx)
                        _.border = Border(left=Side(style='thin'),
                                    right=Side(style='thin'),
                                    top=Side(style='thin'),
                                    bottom=Side(style='thin'))
                        ws.column_dimensions[get_column_letter(
                                                all_col)].width = 3
                    for c_idx, df_value in enumerate(df_row, col):
                        _ = ws.cell(column=c_idx, row=r_idx, 
                                                value=df_value)
                        _.alignment = Alignment(horizontal='center')
                        if r_idx == row:
                            _.alignment = Alignment(
                                        text_rotation=180, vertical='top')                    

                col += 21

            # collating and writing outstanding/failed courses
            course_brk_dwn = failed_courses_breakdown(df)
            failed_courses_first = course_brk_dwn['failed_courses_first']
            outstanding_cred_1st = course_brk_dwn['outstanding_cred_1st']
            outstanding_cred = course_brk_dwn['outstanding_credit_load']
            failed_courses_second = course_brk_dwn['failed_courses_second']

            _failed_crses_block(failed_courses_first,outstanding_cred_1st,
                                    first_sem=True)
            col += 21

            _failed_crses_block(failed_courses_second, 
                                                outstanding_cred)

            row += 5
            serial_number += 1        
    
    return wb

def class_failure_spreadsheet(result_qs, class_list, expected_yr_of_grad):
    wb = Workbook()
    ws = wb.active

    ws.title = f'Class of {expected_yr_of_grad} CO Summary List'
    headers = ['SN', 'Reg Number', 'Name', 'Outstanding Courses (1st)', 
                'Credit Load(1st)','Outstanding Courses (2nd)',
                'Total Credit Load', 'CGPA']
    ws.append(headers)
    ws.freeze_panes = 'A2'
    serial_number = 1
    column_dimensions = {1:4,2:12,3:20,4:28,5:10,6:28,7:11,8:9}
    
    for key, value in column_dimensions.items():
        ws.column_dimensions[get_column_letter(key)].width = value
        cell = ws.cell(row=1, column=key)
        cell.border = normal_border
        cell.alignment = Alignment(horizontal='center',vertical='top',
                                                        wrap_text=True)
        cell.font = Font(bold=True)


    row = 2
    for student in class_list:
        student_qs = result_qs.filter(student_reg_no=student[0]).order_by(
                                                                'semester')
        # confirm that the student's results are available
        if len(student_qs) == 0:
            continue
        
        else:
            #convert student's result qs to dataframe
            df = pd.DataFrame.from_records(student_qs)
            df = df.rename(columns = {0: 'course_title', 1: 'course_code', 
                                    2: 'credit_load', 3: 'course_level', 
                                    4: 'semester', 5: 'grade'})
            df = Student.get_weight_col(df)
            reg_no = student[0]
            name = student[1]
            
            #calculate the cgpa of the student
            weight_sum = df['weight'].sum()
            credit_sum = df['credit_load'].sum()
            cgpa = round(weight_sum/credit_sum,3)

            #get dictionary containing breakdown of failed courses
            course_brk_dwn = failed_courses_breakdown(df)
            failed_courses_first = course_brk_dwn['failed_courses_first']
            outstanding_cred_1st = course_brk_dwn['outstanding_cred_1st'] 
            outstanding_cred = course_brk_dwn['outstanding_credit_load'] 
            failed_courses_second = course_brk_dwn['failed_courses_second']

            entry_alignment = Alignment(vertical='top',horizontal='center',
                                                            wrap_text=True)
            
            ws.row_dimensions[row].height = 90
            ws.cell(row=row, column=1, value=serial_number)
            ws.cell(row=row, column=2, value=reg_no)
            ws.cell(row=row, column=3, value=name)
            ws.cell(row=row, column=4, value=_list_to_cell(failed_courses_first))
            ws.cell(row=row, column=5, value=outstanding_cred_1st)
            ws.cell(row=row, column=6, value=_list_to_cell(failed_courses_second))
            ws.cell(row=row, column=7, value=outstanding_cred)
            ws.cell(row=row, column=8, value=cgpa)

            for col_idx in range(1,9):
                cell = ws.cell(row=row, column=col_idx)
                cell.alignment = entry_alignment
                cell.border = normal_border


            row += 1
            serial_number += 1
    ws.oddHeader.center.text = '''&BDEPARTMENT OF ELECTRONIC ENGINEERING\nSTUDENT ACADEMIC PERFORMANCE SUMMARY&B'''
    Worksheet.set_printer_settings(ws, paper_size=9,orientation='landscape')
    return wb

def collated_results_spreadsheet(res_df):
    '''This function will process the result df into a spreadsheet which
        will be returned to the caller'''
    
    courses = res_df['course_code'].unique().tolist()
    students  = res_df.groupby(['name', 'reg_no']).size().reset_index()
    students = students[['name', 'reg_no']].values.tolist()
    collated_result = pd.DataFrame(students, columns=['Name', 'RegNo'])
    print("This is before",collated_result)
    for course in courses:
        x = ['X'] * len(students)
        j = course
        for student in range(0,len(students)):
            grade = res_df.query('(reg_no == @students[@student][1]) and (course_code == @course)')
            if len(grade) == 1:
                x[student] = grade['grade'].tolist()[0]
        collated_result[j] = x
    # print(collated_result)

    # printing to a worksheet
    wb = Workbook()
    ws = wb.active

    row = 1
    col = 1
    ws.freeze_panes = 'D2'
    headings = ['SN', 'Name','REG NO'] + courses

    for c_idx in chain(range(1,2),range(4,(len(headings)+1))):
        ws.column_dimensions[get_column_letter(c_idx)].width = 4
    ws.column_dimensions[get_column_letter(2)].width = 38
    ws.column_dimensions[get_column_letter(3)].width = 12
    for idx, heading in enumerate(headings, 1):
        _ = ws.cell(row=1,column=idx, value=heading)
        _.font = Font('Times new Roman', 13, bold=True)
        _.border = normal_border
        _.alignment = Alignment(vertical='top', horizontal='center')
        if idx > 3:
            _.alignment = Alignment(vertical='top', text_rotation=180, 
                                    horizontal='center')
    row += 1

    result_rows = dataframe_to_rows(collated_result, index=False, header=False)
    count = 1
    for row_idx, df_row in enumerate(result_rows, row):
        _ = ws.cell(row=row_idx, column=1, value = count)
        _.border = normal_border
        _.font = times_new_rom_style
        _.alignment = Alignment(horizontal='center', vertical='top')
        count += 1
        for col_idx, df_value in enumerate(df_row, col+1):
            _ = ws.cell(row=row_idx, column=col_idx, value=df_value.upper())
            _.border = normal_border
            _.alignment = Alignment(horizontal='center', vertical='top',
                                    wrap_text=True)
            _.font = times_new_rom_style    
    
    hod_name = Lecturer.objects.get(head_of_dept=True).get_full_name()
    
    ws.print_title_rows = '1:1'
    ws.HeaderFooter.differentFirst = False
    ws.oddFooter.left.text = '&BHead of Dept.: '+'&U'+hod_name + '  &U&B\nSign:__________________'
    ws.oddFooter.right.text = '&BExams Officer:__________________&B\nSign:__________________'
    Worksheet.set_printer_settings(ws, paper_size=9,orientation='landscape')
    return wb


