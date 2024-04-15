from RPA.Browser.Selenium import Selenium
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import logging
import re
import os
import requests
import math


def setup_browser():
    browser = Selenium()
    browser.open_available_browser()
    return browser

def assert_element(browser, element, message="Element not found.", element_type="element"):
    if element_type == "title":
        assert element in browser.get_title(), message
    else:
        assert element.is_element_visible(), message

def assert_results_count(browser, locator):
    if not browser.is_element_visible('css=.SearchResultsModule-noResults'):
        element = browser.find_element(locator).text
        if element:
            text = element
            # Extracting digits and converting them to an integer
            results_count = int(re.sub(r"[^\d]", "", text))
            assert results_count > 0, "Results count is not greater than 0."
            page_count = results_count / 30
            page_count = math.ceil(page_count)
            logging.info(f"Results count is {results_count}, which is greater than 0.")
            return page_count
        else:
            raise AssertionError("Results count element not found.")     
    else:
        raise AssertionError('There is no result for the search')       
    
def download_image(url, title):
    response = requests.get(url)
    if response.status_code == 200:
        # Save the image locally
        words = title.split()
        words = words[:2]
        filename = ' '.join(words)
        filename = re.sub(r'[^a-zA-Z0-9\s]', '', filename)
        filename = filename + '.png'
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filepath = os.path.join(filepath, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        logging.error("Failed to download image from %s", url)
        return None
    
def apply_filters(self):
    if self.category:
        target_category = self.category
        logging.info(f"Applying filter for category: {self.category}")

        try:
            self.browser.click_element('css=.SearchFilter-heading > .chevron')
            if self.browser.is_element_visible('css=.seeAllText'):
                self.browser.click_element('css=.seeAllText')
            filters = self.browser.find_elements('xpath=//bsp-toggler/div/ul/li/div')
            idx = 1
            for filter_item in filters:
                label = self.browser.get_text(filter_item)
                label_text = label.lower()  # Normalize text to lowercase
                
                if target_category in label_text:
                    checkbox = self.browser.find_element(f'xpath=//li[{idx}]/div/div/label/input')
                    if not self.browser.get_element_attribute(checkbox, 'checked'):
                        self.browser.click_element(checkbox)
                        logging.info(f"Applied filter: {label}")
                        break

                idx = idx + 1     
        except Exception as e:
            logging.error(f"Error during filter application: {str(e)}")


def apply_sorting(self):
    sort_options = {'newest': '3', 'oldest': '2', 'relevance': '0'}

    if self.category and self.category.lower() in ['newest', 'oldest', 'relevant', 'relevance']:
        if self.category.lower() == 'newest':
            sort_value = sort_options.get('newest', '3')
        elif self.category.lower() == 'oldest':
            sort_value = sort_options.get('oldest', '2')
        elif self.category.lower() == 'relevant' or self.category.lower() == 'relevance':
            sort_value = sort_options.get('relevance', '0')
    else:
        sort_value = sort_options.get('newest', '3')            
    return sort_value    

def replace_page_number(url, new_page_number):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['p'] = [str(new_page_number)]
    new_query = urlencode(query_params, doseq=True)
    new_url = parsed_url._replace(query=new_query)
    return urlunparse(new_url)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
