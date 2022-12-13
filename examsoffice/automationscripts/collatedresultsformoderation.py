import csv
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

from results.models import Student


def get_results():
    with open(os.path.join(os.path.dirname(__file__), "ALL_RESULTS.csv")) as res_file:
        results = list(csv.DictReader(res_file))
    df = pd.DataFrame(results)
    df.reg_no = df.reg_no.apply(lambda x: x.strip())
    df.course = df.course.apply(lambda x: x.strip())
    return df


def collate_results(input_results_df):
    """Prepare CSV file of collated result.

    Each row is the details of a student's performance in all courses
    available in the input_results_df.
    """
    all_courses = input_results_df.course.unique().tolist()
    # sort the courses, knowing that first semester courses end
    # with odd numbers while second semester courses end with even
    # numbers
    all_courses.sort(key=lambda x: ((int(x[-1]) % 2 == 0), x))
    all_students = input_results_df.reg_no.unique().tolist()
    student_names = []

    for student in all_students:
        name = Student.objects.filter(student_reg_no=student)
        if name.exists():
            name = name.first()
            name_and_initials = (
                (name.last_name.upper() if (name.last_name is not None) else "")
                + " "
                + (name.first_name[0].upper() if (name.first_name is not None) else "")
                + ". "
                + (name.other_names[0].upper() if (name.other_names is not None) else "")
            )
            student_names.append(name_and_initials)
            continue
        student_names.append(None)

    result_df = pd.DataFrame()
    result_df["reg_no"] = all_students
    result_df["name"] = student_names
    for course in all_courses:
        result_df[course] = ["XX"] * len(result_df.reg_no)


    def get_score(row, course):
        """Get score for given result_df row and course.

        Written to be used as a transform function in a dataframe.
        """
        score = (
            input_results_df[(
                input_results_df['reg_no'] == row.reg_no)
                & (input_results_df['course'] == course)]['score']
        )
        return score.iloc[0] if (not score.empty) else "XX"

    for course in all_courses:
        result_df[course] = result_df.apply(
            lambda x: get_score(x, course), axis=1
        )
    result_df.sort_values("name", inplace=True)
    result_df.to_csv("output.csv", index=False)


def generate_results_analytics(result_df):
    """
    Generate a report that details and presents analytics of the
    performance of the entire class (number of scores above 69, etc.)
    for each course present in result_df
    -----------------------
    Inputs:
        result_df: Dataframe: a dataframe of results to be processed
    Returns:
        output.pdf: A pdf file of the generated analytics
    """
    courses = result_df.course.unique().tolist()
    courses.sort(key=lambda x: ((int(x[-1]) % 2 == 0), x))
    result_df.score = pd.to_numeric(result_df.score, errors="coerce")
    result_df.dropna()
    ranges = [0, 40, 45, 50, 60, 70, 100]
    score_labels = [
        '-'.join([str(ranges[i-1]), str(ranges[i] - 1)])
        for i in range(len(ranges)) if i != 0
    ]
    with PdfPages(('performance_analytics.pdf')) as pdf:
        for course in courses:
            course_res = result_df[result_df.course==course]
            performance = course_res.groupby(
                pd.cut(
                    course_res.score,
                    ranges,
                    right=False,
                    include_lowest=True
                )
            ).count()
            performance = performance.head(result_df.shape[0])
            counts = performance.score.tolist()
            plot_df = pd.DataFrame(
                {"Number of Students": counts},
                index=score_labels
            )
            plot_df.plot.bar(y="Number of Students", title=course)
            pdf.savefig()
            plt.close()

            plot_df.plot.pie(
                y="Number of Students", title='', autopct="%.1f%%"
            )
            pdf.savefig()
            plt.close()

            table = pd.DataFrame(plot_df['Number of Students'])
            table.sort_index(ascending=True, inplace=True)
            fig = plt.figure()
            ax = fig.add_subplot(111)
            cell_text = []
            for row in range(len(table)):
                cell_text.append(table.iloc[row])
            # cell_text.append(f'Total Number of students: {table.sum()}')
            ax.table(
                cellText=cell_text,
                colLabels=table.columns,
                rowLabels=table.index,
                loc='center'
            )
            ax.set_title(
                f'Total Number of students: {table["Number of Students"].sum()}'
            )
            ax.axis('off')

            pdf.savefig(fig)
            plt.close()


def run():
    result_df = get_results()
    collate_results(result_df)
    generate_results_analytics(result_df)


if __name__ == '__main__':
    run()
