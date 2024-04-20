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
    #Download an image from a URL and save it locally 
    #with a sanitized title as the filename.
    response = requests.get(url)
    if response.status_code == 200:
        # Save the image locally
        words = title.split()[:2]  # Use only the first two words of the title
        filename = ' '.join(words)
        filename = re.sub(r'[^a-zA-Z0-9\s]', '', filename) + '.png'
        
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as file:
            file.write(response.content)
        
        return filename
    else:
        logging.error("Failed to download image from %s", url)
        return None
    
def apply_filters(self):
    #Apply filters based on the category to the browser's search functionality.
    if not self.category:
        return

    logging.info(f"Applying filter for category: {self.category}")
    try:
        self.browser.click_element('css=.SearchFilter-heading > .chevron')
        if self.browser.is_element_visible('css=.seeAllText'):
            self.browser.click_element('css=.seeAllText')

        filters = self.browser.find_elements('xpath=//bsp-toggler/div/ul/li/div')
        for index, filter_item in enumerate(filters, start=1):
            label_text = self.browser.get_text(filter_item).lower()  # Normalize text to lowercase

            if self.category in label_text:
                checkbox = self.browser.find_element(f'xpath=//li[{index}]/div/div/label/input')
                if not self.browser.get_element_attribute(checkbox, 'checked'):
                    self.browser.click_element(checkbox)
                    logging.info(f"Applied filter: {self.browser.get_text(filter_item)}")
                    break
    except Exception as e:
        logging.error(f"Error during filter application: {str(e)}")

def apply_sorting(self):
    #Determine the sort value based on the category set for the scraper.
    sort_options = {'newest': '3', 'oldest': '2', 'relevance': '0'}

    # Normalize the category to lower case
    category_lower = self.category.lower() if self.category else 'newest'

    # Simplified logic for choosing sort value
    return sort_options.get(category_lower, '3')   

def replace_page_number(url, new_page_number):
    #Replace the page number parameter in a URL query string with a new page number.
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['p'] = [str(new_page_number)]  # Set new page number
    new_query = urlencode(query_params, doseq=True)  # Re-encode the query parameters
    new_url = parsed_url._replace(query=new_query)  # Replace the query part of the URL

    return urlunparse(new_url)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
