from scraper import NewsScraper

#================= Info =====================
# Project Structure:
# news_scraper/
# │
# ├── main.py             # Main script to run the scraper
# ├── scraper.py          # Module for scraping functionality
# ├── data_handler.py     # Module for handling data storage
# └── utils.py            # Module for utility functions like logging and assertions


def main():
    
    search_phrase = "dacueba"
    category = "Newest"
    months = 0

    scraper = NewsScraper(search_phrase, category, months)
    scraper.run()

if __name__ == "__main__":
    main()
