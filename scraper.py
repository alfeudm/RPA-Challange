from utils import setup_browser, assert_element, assert_results_count, logging, download_image, re, apply_filters, apply_sorting, replace_page_number
from data_handler import save_to_excel, attach_excel_file_to_work_item, WorkItems
from datetime import datetime, timedelta
import os

class NewsScraper:
    
    def __init__(self, search_phrase, category, months):
        self.browser = setup_browser()
        self.search_phrase = search_phrase
        self.category = category.lower() if category else None
        self.months = months
        self.url = "https://apnews.com/"
        self.main_window = None
        self.results = []

    def open_site(self):
        self.main_window = self.browser.get_window_handles()[0]
        self.browser.go_to(self.url)
        try:
            assert_element(self.browser, "AP", element_type="title")
            logging.info("Home page loaded successfully.")
        except AssertionError:
            logging.error("Home page did not load correctly or title mismatch.")

    def perform_search(self):
        sort_value = apply_sorting(self)
        search_url = f"{self.url}search?q={self.search_phrase.replace(' ', '+')}&s={sort_value}"
        self.browser.go_to(search_url)
        logging.info(f"Performing search on: {search_url}")
        self.page_number = assert_results_count(self.browser, 'css=.SearchResultsModule-count-desktop')
        if self.category and self.category.lower() not in ['newest', 'oldest', 'relevant', 'relevance']:
            apply_filters(self)

    def extract_data(self):
        self.browser.wait_until_page_contains_element('xpath=//bsp-list-loadmore/div[2]/div', timeout=30)
        self.browser.switch_window(self.main_window)

        for page in range(self.page_number):
            page = page + 1

            for item in range(30):
                item = item + 1
 
                try:
                    date_text = self.browser.find_element(f'css=.PageList-items-item:nth-child({str(item)}) .PagePromo-byline span').text
                    date_text = date_text.split(',')
                    date = date_text[1] + ',' + date_text[2]
                    date = date.strip()
                    news_date = datetime.strptime(date, '%B %d, %Y')
                except:
                    try:
                        date_text = self.browser.find_element(f'css=.PageList-items-item:nth-child({str(item)}) .Timestamp-minago').text
                        news_date = datetime.today()
                    except:
                        logging.info("No Date found")
                        logging.info("Going to next News")
                        continue   
                logging.info("Getting News' Date")

                # Calculate how many months ago the news was published
                
                if (datetime.now() - news_date).days <= self.months * 30:

                    # Extract the title
                    try:
                        title = self.browser.find_element(f'css=.PageList-items-item:nth-child({str(item)}) > .PagePromo .PagePromo-title').text
                        logging.info("Getting News' title")
                    except:
                        logging.info("News does not have title.")
                        continue

                    try:
                        description = self.browser.find_element(f'css=.PageList-items-item:nth-child({str(item)}) .PagePromo-description').text
                        logging.info("Getting News' Description")
                    except:
                        logging.info("News does not have description.")
                        description = ''

                    try:
                        image_url = self.browser.find_element(f'css=.PageList-items-item:nth-child({str(item)}) .Image').get_attribute('src')
                        logging.info("Getting News' Image")
                        no_image = False
                    except:
                        no_image = True
                        logging.info("News does not have image.")

                    
                    image_path = ''
                    image_filename = 'no image avaliable'

                    if not no_image:
                        # Download image
                        image_filename = download_image(image_url, title)
                        logging.info("Saving image")
                        work_items = WorkItems()
                        work_items.get_input_work_item()
                        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', image_filename)
                        work_items.add_work_item_file(image_path, image_filename)

                    # Check for monetary values
                    contains_money = bool(re.search(r'\$\d+\.?\d*|\d+\s(dollars|USD)', title + ' ' + 
                    (description if description else '')))
                    logging.info("Checking for monetary values")

                    # Append result
                    self.results.append({
                        'title': title,
                        'date': news_date,
                        'description': description,
                        'picture_filename': image_filename,
                        'contains_money': contains_money,
                        'image_path': image_path
                    })
                    logging.info("Appending results")
                else:
                    logging.info("News outdated")
                    continue

            #Go to next page
            url = self.browser.get_location() 

            if page == 1:
                url = url + '&p=2'
            else:
                url = replace_page_number(url, page + 1)

            self.browser.go_to(url)
            self.browser.switch_window(self.main_window) 
            if page >= 3:
                
                break   

    def run(self):
        try:
            self.open_site()
            self.perform_search()
            self.extract_data()
            name_xl = save_to_excel(self.results)
            attach_excel_file_to_work_item(name_xl)
        finally:
            self.browser.close_browser()


