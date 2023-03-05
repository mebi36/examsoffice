import pandas as pd
from pandas.api.types import is_string_dtype

from models import Result

def normal_excel_upload(excel_file):
    try:
        df = pd.read_excel(excel_file, header=None)
    except Exception:
        print("Problem reading excel file")

    results_row_df = pd.DataFrame()
    reg_no_col = None

    # find reg number column
    for col in df.columns:
        df_gen = df[df[col].str.contains(pat="^[0-9]{4}\/[0-9]{6}", regex=True, na=False)]

        if not df_gen.empty:
            reg_no_col = col
            results_row_df = df_gen
            break
    
    valid_grade_vals = Result.VALID_GRADES + ["FF"]
    expceted_grade_col = None

    for col in range(reg_no_col+1, generated_df.columns+1):
        if not is_string_dtype(generated_df[col]):
            continue
        generated_df[col] = generated_df.apply(lambda x: x.strip().upper())
        generated_df["grade_checker"] = generated_df[col].apply(lambda x: x in valid_grade_vals)
        if generated_df["grade_checker"].sum() >= len(generated_df) * .75:
            expceted_grade_col = col
            generated_df.rename(
                columns={expceted_grade_col: "letter_grade", reg_no_col: "reg_no"},
                inplace=True
            )
            generated_df["letter_grade"] = generated_df["letter_grade"].replace("FF", "F")
            generated_df = generated_df[generated_df["grade_checker"]]
            generated_df = generated_df[["reg_no", "letter_grade"]]
    if "letter_grade" not in generated_df:
        raise ValueError("Grades not detected in uploaded file")
    
    