
import openpyxl
from datetime import datetime

def save_to_excel(data):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    current_datetime = datetime.now()
    str_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    if data:
        headers = list(data[0].keys())
        sheet.append(headers)
    
    # Append rows of values
    for item in data:
        row = [item[key] for key in headers] 
        sheet.append(row)
    
    workbook.save(f"APNewsData_{str_datetime}.xlsx")