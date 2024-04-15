
from news_article import NewsArticle
import re
from datetime import datetime, timedelta
from utils import logging
import RPA.Browser.Selenium as Browser
from RPA.Browser.Selenium import SeleniumLibrary as Browser

class NewsExtractor:
    def __init__(self, search_phrase, category, months):
        self.search_phrase = search_phrase
        self.category = category
        self.months = months
        self.articles = []
        self.browser = Browser()

    def open_website(self, url):
        # Open the website and enter the search phrase.
        logging.info("Opening website: %s", url)
        self.browser.open_browser(url)
        # Assert that the search input field is present
        assert self.browser.wait_until_page_contains_element("//input[@name='query']"), "Search input field not found"
        self.browser.input_text("//input[@name='query']", self.search_phrase)
        self.browser.press_keys("//input[@name='query']", "ENTER")
        logging.info("Entered search phrase: %s", self.search_phrase)

    def extract_news(self):
        # Retrieve the news articles and extract the required information.
        if self.category:
            logging.info("Selecting news category: %s", self.category)
            assert self.browser.wait_until_page_contains_element(f"//a[contains(text(), '{self.category}')]"), f"News category '{self.category}' not found"
            self.browser.click(f"//a[contains(text(), '{self.category}')]")

        article_elements = self.browser.find_elements("//article")
        assert len(article_elements) > 0, "No articles found on the page"
        logging.info("Found %d articles", len(article_elements))

        for article_element in article_elements:
            try:
                title = article_element.find_element("./h2").text
                date_text = article_element.find_element("./div/time").text
                description = article_element.find_element("./p").text
                image_url = article_element.find_element("//img").get_attribute("src")

                date = datetime.strptime(date_text, "%B %d, %Y")
                if self.months > 0:
                    if date < datetime.now() - timedelta(days=self.months * 30):
                        continue

                search_phrase_count = sum(1 for _ in re.finditer(self.search_phrase, title + description))
                has_money = bool(re.search(r'\$\d+(?:[,\.\d]+)?|\d+\s*(?:dollars|USD)', title + description))

                article = NewsArticle(title, date.strftime("%Y-%m-%d"), description, image_url, search_phrase_count, has_money)
                self.articles.append(article)
                logging.info("Extracted article: %s", article.title)
            except Exception as e:
                logging.error("Error extracting article: %s", str(e))

    def save_to_excel(self, output_file):
        # ... (implementation)
        pass

    def download_images(self, output_dir):
        # ... (implementation)
        pass

    def run(self, output_file, output_dir):
        # """Execute the entire news extraction process."""
        self.open_website("https://www.example.com")
        self.extract_news()
        self.save_to_excel(output_file)
        self.download_images(output_dir)
        self.browser.close_browser()
        logging.info("Extraction process completed.")

if __name__ == "__main__":
    # Retrieve parameters from Robocloud work item
    search_phrase = "Your search phrase"
    category = "Your news category/section/topic"
    months = 1  # Number of months

    extractor = NewsExtractor(search_phrase, category, months)
    extractor.run("output.xlsx", "output_images")