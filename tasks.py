from scraper import NewsScraper, logging
from RPA.Robocorp.WorkItems import WorkItems
from robocorp.tasks import task
import json


#================= Info =====================
# Project Structure:
#
# news_scraper/
# │
# ├── main.py             # Main script to run the scraper
# ├── scraper.py          # Module for scraping functionality
# ├── data_handler.py     # Module for handling data storage
# └── utils.py            # Module for utility functions like logging and assertions

@task
def my_task():

    wi = WorkItems()
    wi.get_input_work_item()
    logging.info("Getting Work Item")
    search_phrase = wi.get_work_item_variable('search phrase')
    category = wi.get_work_item_variable('category')
    months = int(wi.get_work_item_variable('months'))
    
    scraper = NewsScraper(search_phrase, category, months, wi)
    scraper.run()
    logging.info("Finishing")

my_task()
