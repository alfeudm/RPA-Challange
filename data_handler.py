from RPA.Excel.Files import Files
from datetime import datetime
from RPA.Robocorp.WorkItems import WorkItems
import logging

def save_to_excel(data):
    excel = Files()
    workbook = excel.create_workbook()
    sheet = workbook.active
    current_datetime = datetime.now()
    str_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    if data:
        headers = list(data[0].keys())
        sheet.append_rows_to_worksheet(headers)
    
    # Append rows of values
    for item in data:
        row = [item[key] for key in headers] 
        sheet.append_rows_to_worksheet(row)

    name_xl = f"APNewsData_{str_datetime}.xlsx"
    
    workbook.save(name_xl)

    return name_xl


def attach_excel_file_to_work_item(name_xl):
    # Attach the Excel file to the current work item
    try:
        wi = WorkItems()
        item = wi.get_input_work_item()
        logging.info("creating output workitem") 
        wi.create_output_work_item(files=name_xl, save=True)
        logging.info("Adding file to artifact")
        wi.add_work_item_file(name_xl) 
        wi.save_work_item()
        wi.add_work_item_file(name_xl) 
    except:
        return None       