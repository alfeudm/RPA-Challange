from RPA.Excel.Files import Files
from datetime import datetime
from RPA.Robocorp.WorkItems import WorkItems
import logging
import os

def save_to_excel(data):
    excel = Files()
    
    excel.create_workbook()
    current_datetime = datetime.now()
    str_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    if data:
        headers = list(data[0].keys())
        excel.append_rows_to_worksheet(headers)
    
    # Append rows of values
    for item in data:
        row = [item[key] for key in headers] 
        excel.append_rows_to_worksheet(row)

    name_xl = f"APNewsData_{str_datetime}.xlsx"
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', name_xl)
    excel.save_workbook(excel_path)

    return excel_path


def attach_excel_file_to_work_item(excel_path):
    # Attach the Excel file to the current work item
    try:
        wi = WorkItems()
        item = wi.get_input_work_item()
        logging.info("creating output workitem") 
        wi.create_output_work_item(files=excel_path, save=True)
        logging.info("Adding files to artifact")
        wi.add_work_item_file(excel_path)
        wi.save_work_item()
        wi.release_input_work_item("DONE")
    except:
        return None       