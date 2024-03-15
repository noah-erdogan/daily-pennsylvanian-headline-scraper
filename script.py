"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru

def scrape_data_point():
    """
    Scrapes the main headline from The Daily Pennsylvanian home page.

    Returns:
        str: The headline text if found, otherwise an empty string.
    """
    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_element = soup.find("a", class_="frontpage-link")
        data_point = "" if target_element is None else target_element.text
        loguru.logger.info(f"Data point: {data_point}")
        return data_point

def scrape_academics_article_title():
    """
    Scrapes the title of the first article under the "Academics" section from The Daily Pennsylvanian website.

    Returns:
        str: The title of the first article if found, otherwise an empty string.
    """
    req = requests.get("https://www.thedp.com/section/academics")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_element = soup.find("h3", class_="standard-link")
        if target_element and target_element.find("a"):
            article_title = target_element.find("a").text.strip()  # Get the text and strip any extra whitespace
            loguru.logger.info(f"Article title: {article_title}")
            return article_title

    return ""  # Return an empty string if the article title wasn't found

if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor for main headline
    loguru.logger.info("Loading daily event monitor for main headline")
    dem_main = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_main_headlines.json"
    )

    # Load daily event monitor for academics article
    loguru.logger.info("Loading daily event monitor for academics article")
    dem_academics = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_academics_articles.json"
    )

    # Run scrape for main headline
    loguru.logger.info("Starting scrape for main headline")
    try:
        main_headline = scrape_data_point()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape main headline: {e}")
        main_headline = None

    # Save main headline data
    if main_headline is not None:
        dem_main.add_today(main_headline)
        dem_main.save()
        loguru.logger.info("Saved main headline daily event monitor")

    # Run scrape for academics article title
    loguru.logger.info("Starting scrape for academics article title")
    try:
        academics_article_title = scrape_academics_article_title()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape academics article title: {e}")
        academics_article_title = None

    # Save academics article title data
    if academics_article_title is not None:
        dem_academics.add_today(academics_article_title)
        dem_academics.save()
        loguru.logger.info("Saved academics article title daily event monitor")

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
