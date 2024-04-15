
import openpyxl
from datetime import datetime
from RPA.Robocorp.WorkItems import WorkItems

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

    name_xl = f"APNewsData_{str_datetime}.xlsx"
    
    workbook.save(name_xl)

    return name_xl


def attach_excel_file_to_work_item(self, name_xl):
    # Attach the Excel file to the current work item
    try:
        wi = WorkItems()
        wi.get_input_work_item()
        wi.add_work_item_file(name_xl, name="Processed Data") 
    except:
        return None       