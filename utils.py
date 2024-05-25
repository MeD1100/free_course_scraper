import os
import pandas as pd
from datetime import datetime

def save_to_excel(courses, save_location):
    today_date = datetime.now().strftime("%d%m%Y")
    file_name = f"free_courses_{today_date}.xlsx"
    file_path = os.path.join(save_location, file_name)

    data = [{
        "Course Title": course[0],
        "Category": course[1],
        "Link": course[2],
        "Release Time": course[3]
    } for course in courses]

    df = pd.DataFrame(data)
    df.sort_values(by='Release Time', inplace=True, ascending=False)  # Sort by release time in descending order

    # Adjust the width of the columns for better readability
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Courses')

    worksheet = writer.sheets['Courses']
    worksheet.set_column('A:A', 40)  # Set column width for Course Title
    worksheet.set_column('B:B', 30)  # Set column width for Category
    worksheet.set_column('C:C', 80)  # Set column width for Link
    worksheet.set_column('D:D', 20)  # Set column width for Release Time

    writer.close()

    print(f"Saved scraped data to {file_path}")