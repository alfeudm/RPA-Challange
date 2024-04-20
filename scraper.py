from utils import (
    setup_browser,
    assert_element,
    assert_results_count,
    download_image,
    apply_filters,
    apply_sorting,
    replace_page_number,
    logging,
    re
)
from data_handler import save_to_excel, attach_excel_file_to_work_item
from datetime import datetime
import os

class NewsScraper:
    
    def __init__(self, search_phrase, category, months, wi):
        self.browser = setup_browser()
        self.search_phrase = search_phrase
        self.category = category.lower() if category else None
        self.months = months
        self.url = "https://apnews.com/"
        self.main_window = None
        self.wi = wi
        self.results = []
        
    def open_site(self):
        self.main_window = self.browser.get_window_handles()[0]
        logging.info("Loading Browser")
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

        logging.info("Getting Page Count")
        for page in range(self.page_number):
            page += 1

            for item in range(30):
                logging.info("Getting Page Item")
                item += 1

                try:
                    logging.info("Trying to get News Date")
                    date_text = self.browser.find_element(
                        f'css=.PageList-items-item:nth-child({str(item)}) .PagePromo-byline span'
                    ).text
                    date_text = date_text.split(',')
                    date = date_text[1] + ',' + date_text[2]
                    date = date.strip()
                    news_date = datetime.strptime(date, '%B %d, %Y')
                except:
                    try:
                        logging.info("Date found in a different format")
                        date_text = self.browser.find_element(
                            f'css=.PageList-items-item:nth-child({str(item)}) .Timestamp-minago'
                        ).text
                        news_date = datetime.today()
                    except:
                        logging.info("No Date found")
                        logging.info("Going to next News")
                        continue
                logging.info("Getting News' Date")

                if (datetime.now() - news_date).days <= self.months * 30:
                    stop_scraping = self.extract_title_description_image(item, news_date)
                    if len(self.results) >= 48: break
                else:
                    logging.info("News outdated")
                    continue

            stop_scraping = self.go_to_next_page(page)
            if stop_scraping:
                break


    def extract_title_description_image(self, item, news_date):
        logging.info("Getting Title locator")
        try:
            title_selector = (
                f'css=.PageList-items-item:nth-child({item}) > .PagePromo .PagePromo-title'
            )
            title = self.browser.find_element(title_selector).text
            logging.info("Getting News' title")
        except Exception as e:
            logging.info("News does not have title. Error: " + str(e))
            return  # Skip this item if the title cannot be found

        try:
            description_selector = (
                f'css=.PageList-items-item:nth-child({item}) .PagePromo-description'
            )
            description = self.browser.find_element(description_selector).text
            logging.info("Getting News' Description")
        except Exception as e:
            logging.info("News does not have description. Error: " + str(e))
            description = ''  # Assume no description if an error occurs

        image_url, image_path, image_filename = '', '', 'no_image_available'
        try:
            image_selector = (
                f'css=.PageList-items-item:nth-child({item}) .Image'
            )
            image_url = self.browser.find_element(image_selector).get_attribute('src')
            image_filename = download_image(image_url, title)
            logging.info("Downloading and saving News' Image")
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', image_filename)
            self.wi.add_work_item_file(image_path, image_filename)
            self.wi.save_work_item()
        except Exception as e:
            logging.info("News does not have image or download failed. Error: " + str(e))

        # Check for monetary values in the title or description
        contains_money = bool(re.search(r'\$\d+\.?\d*|\d+\s(dollars|USD)', title))
        logging.info("Checking for monetary values")

        # Append result to the results list
        self.results.append({
            'title': title,
            'date': news_date,
            'description': description,
            'picture_filename': image_filename,
            'contains_money': contains_money,
            'image_path': image_path
        })
        logging.info("Appending results")

    def go_to_next_page(self, current_page):
        url = self.browser.get_location()
        stop_scraping = False
    
        if current_page == 1:
            new_url = url + '&p=2'
        else:
            new_url = replace_page_number(url, current_page + 1)

        self.browser.go_to(new_url)
        self.browser.switch_window(self.main_window)
        if current_page == 2:
            stop_scraping = True
        
        return stop_scraping

    def run(self):
        """
        Orchestrates the process of opening the site, performing searches,
        extracting data, saving it to Excel, and attaching the file to a work item.
        Ensures the browser is closed after operations complete.
        """
        try:
            self.open_site()
            self.perform_search()
            self.extract_data()
            name_xl = save_to_excel(self.results)
            if name_xl:  # Ensure the Excel file was created successfully.
                success = attach_excel_file_to_work_item(name_xl)
                if not success:
                    logging.error("Failed to attach the Excel file to the work item.")
        except Exception as e:
            logging.error(f"An error occurred during the run process: {str(e)}")
        finally:
            self.browser.close_browser()



