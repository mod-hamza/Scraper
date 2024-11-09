
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium import webdriver
from termcolor import colored
from utils import load_config
from typing import Any

import pyperclip
import time


def search_youtube_channel(channel: str, driver: webdriver.Firefox) -> bool:
    """
    Searches for a YouTube channel using the provided channel name and a Firefox WebDriver.

    Parameters:
        channel (str): The name of the channel to search for.
        driver (webdriver.Firefox): A Firefox WebDriver instance.

    Returns:
        bool: True if the channel was found, False otherwise.
    """
    channel = channel.strip("@")

    try:
        driver.get(f"https://www.youtube.com/@{channel}/videos")
        return True

    except:
        return False


def get_channel_subs(driver: webdriver.Firefox) -> int:
    """
    Retrieves the number of subscribers for a YouTube channel.

    Parameters:
        driver (webdriver.Firefox): A Firefox WebDriver instance used to interact with the YouTube page.

    Returns:
        int: The number of subscribers for the channel. Returns 0 if an error occurs.
    """
    config = load_config('config.json')
    wait = WebDriverWait(driver, config["Timeout"])

    try:
        subscribers_element = wait.until(ec.presence_of_element_located(
            (By.XPATH,
             '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-tabbed-page-header/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/div/div[2]/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-content-metadata-view-model/div[2]/span[1]')
        ))

        subscribers = str(subscribers_element.text).replace("subscribers", "").strip()

        if 'K' in subscribers:
            return int(float(subscribers.replace('K', '')) * 1000)
        elif 'M' in subscribers:
            return int(float(subscribers.replace('M', '')) * 1000000)
        else:
            return int(subscribers)

    except Exception as e:
        return 0


def get_channel_videos(driver: webdriver.Firefox) -> list[dict]:
    """
    Retrieves a list of video data from a YouTube channel.

    This function clicks on the "Videos" tab, scrapes video titles, views, and dates,
    and extracts keywords from each video. It continues to load more videos until
    it encounters a video older than two months.

    Parameters:
        driver (webdriver): A WebDriver instance used to interact with the YouTube page.

    Returns:
        list[dict]: A list of dictionaries containing video data, including title, views,
        upload date, and keywords. If an error occurs, an empty list is returned.
    """

    video_data: list[dict[str, Any]] = []
    config = load_config("config.json")
    try:
        two_months_ago = datetime.now() - timedelta(days=config["Days"])

        while True:
            # Scrape video titles, views, and dates
            video_titles = driver.find_elements(By.XPATH, '//*[@id="video-title"]')
            video_views = driver.find_elements(By.XPATH, '//*[@id="metadata-line"]/span[1]')
            video_dates = driver.find_elements(By.XPATH, '//*[@id="metadata-line"]/span[2]')

            for title, views, date in zip(video_titles, video_views, video_dates):
                upload_date = parse_upload_date(date.text)
                if upload_date and upload_date < two_months_ago:
                    return video_data

                view = views.text.strip("views").strip("view").strip()
                if 'K' in view:
                    view = int(float(views.replace('K', '')) * 1000)
                elif 'M' in view:
                    view = int(float(views.replace('M', '')) * 1000000)
                else:
                    try:
                        view = int(view)
                    except:
                        view = 0

                # Open the video in a new tab, extract keywords, and close the tab
                extracted_data = open_video(driver, title.text)
                video_data.append({
                    "title": title.text,
                    "views": views.text,
                    "upload_date": date.text,
                    "keywords": extracted_data.get("keywords", [])  # Add only the keywords
                })

            # Scroll down to load more videos
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")
        return video_data


def parse_upload_date(date_str: str) -> datetime | None:
    """
    Parse a string representing the time ago and return a datetime object representing the time.

    Args:
        date_str (str): A string representing the time ago, such as "2 days ago", "1 month ago", etc.

    Returns:
        datetime | None: A datetime object representing the time if the string is in the correct format, None otherwise.
    """

    date_str = date_str.lower()

    if "seconds ago" in date_str or "second ago" in date_str:
        seconds = int(date_str.split()[0])
        return datetime.now() - timedelta(seconds=seconds)

    elif "minutes ago" in date_str or "minute ago" in date_str:
        minutes = int(date_str.split()[0])
        return datetime.now() - timedelta(minutes=minutes)

    elif "days ago" in date_str or "day ago" in date_str:
        days = int(date_str.split()[0])
        return datetime.now() - timedelta(days=days)

    elif "weeks ago" in date_str or "week ago" in date_str:
        weeks = int(date_str.split()[0])
        return datetime.now() - timedelta(weeks=weeks)

    elif "months ago" in date_str or "month ago" in date_str:
        months = int(date_str.split()[0])
        return datetime.now() - timedelta(days=months * 30)

    elif "years ago" in date_str or "year ago" in date_str:
        years = int(date_str.split()[0])
        return datetime.now() - timedelta(days=years * 365)

    else:
        return None


def extract_from_clipboard() -> str:
    """
    Retrieves the current contents of the system clipboard.

    Returns:
        str: The contents of the clipboard as a string. If the pyperclip module is not installed, an empty string is returned.
    """
    try:
        return pyperclip.paste()

    except ImportError:
        print("pyperclip module is not installed.")
        return ""


def extract_keywords(driver) -> dict:
    """
    Extracts the keywords from a YouTube video.

    Args:
        driver (WebDriver): The WebDriver instance used to interact with the YouTube video.

    Returns:
        dict: A dictionary containing the extracted keywords. The dictionary has a single key "keywords" which is a list of strings.
    """
    config = load_config('config.json')
    keywords_button_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[2]/div[1]/div/div[8]/div[2]/div/div[1]/div[2]'
    expand_button_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[2]/div[1]/div/div[1]/div[2]'

    wait = WebDriverWait(driver, config["Timeout"])

    try:
        keywords_button = wait.until(ec.element_to_be_clickable((By.XPATH, keywords_button_xpath)))
        keywords_button.click()

    except TimeoutException:
        print(colored("⚠️  | Could not find keywords button, trying again...", "red"))
        try:
            expand_button = wait.until(ec.element_to_be_clickable((By.XPATH, expand_button_xpath)))
            expand_button.click()

            keywords_button = wait.until(ec.element_to_be_clickable((By.XPATH, keywords_button_xpath)))
            keywords_button.click()
            keywords = extract_from_clipboard()

            if keywords:
                keyword_list = [keyword.strip() for keyword in keywords.split(',')]
                return {"keywords": keyword_list}

        except TimeoutException as e:
            print(colored(f"⚠️  | No keywords for this video...", "red"))
            return {"keywords": []}

    return {"keywords": []}


def open_video(driver: webdriver.Firefox, video_title) -> dict:
    """
    Opens a video in a new browser window, extracts its keywords, and returns the extracted data.

    Args:
        driver (webdriver.Firefox): The Firefox webdriver instance used to interact with the browser.
        video_title (str): The title of the video to be opened.

    Returns:
        dict: A dictionary containing the extracted keywords.
    """
    try:
        video_element = driver.find_element(By.LINK_TEXT, video_title)
        video_element.send_keys(Keys.CONTROL + Keys.RETURN)

        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(5)

        extracted_data = extract_keywords(driver)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return extracted_data

    except Exception as e:
        print(f"Error while processing video '{video_title}': {e}")
        return {}
