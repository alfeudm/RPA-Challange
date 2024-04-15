from scraper import NewsScraper
from RPA.Robocorp.WorkItems import WorkItems
from robocorp.tasks import task

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
    #item = wi.get_input_work_item()
    #wi.load_work_item_from_environment()
    search_phrase = wi.get_work_item_variable('search phrase', '')
    category = wi.get_work_item_variable('category', '')
    months = int(wi.get_work_item_variable('months', 0))

    scraper = NewsScraper(search_phrase, category, months)
    scraper.run()

my_task()
