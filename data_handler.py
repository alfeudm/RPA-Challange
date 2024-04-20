from RPA.Excel.Files import Files
from datetime import datetime
from RPA.Excel.Files import Files
from RPA.FileSystem import FileSystem
from RPA.Robocorp.WorkItems import WorkItems
import logging
import os

def save_to_excel(data):
    # Initialize Excel and File System handlers
    excel = Files()
    fs = FileSystem()
    
    # Create a new Excel workbook and worksheet
    excel.create_workbook()
    excel.rename_worksheet('Sheet', 'Data')
    
    # Prepare timestamp for file naming
    current_datetime = datetime.now()
    str_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    # Define output folder and ensure its existence
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    fs.create_directory(output_dir, parents=True, exist_ok=True)
    
    # Define workbook headers and data append
    if data:
        headers = list(data[0].keys())
        excel.append_rows_to_worksheet([headers], 'Data')
    
        # Append rows of values
        for item in data:
            row = [item[key] for key in headers]
            excel.append_rows_to_worksheet([row], 'Data')

    # Define the file path for the workbook
    name_xl = f"APNewsData_{str_datetime}.xlsx"
    excel_path = os.path.join(output_dir, name_xl)
    
    # Save and close the workbook
    excel.save_workbook(excel_path)
    excel.close_workbook()

    return excel_path


def attach_excel_file_to_work_item(excel_path):
    """
    Attach the Excel file specified by excel_path to the current work item in Robocorp.
    
    Args:
    excel_path (str): The file path to the Excel document to attach.

    Returns:
    bool: True if file was successfully attached, otherwise False.
    """
    try:
        wi = WorkItems()
        wi.get_input_work_item()
        logging.info("Creating output work item and adding files.")
        wi.create_output_work_item(files=excel_path, save=True)
        wi.add_work_item_file(excel_path)
        wi.save_work_item()
        wi.release_input_work_item("DONE")
        wi.save_work_item()
        logging.info("Excel file successfully attached to the work item.")
        return True
    except Exception as e:
        logging.error(f"Failed to attach Excel file: {str(e)}")
        return False