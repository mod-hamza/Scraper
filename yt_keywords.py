
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from database import add_channel_to_db
from selenium import webdriver
from utils import load_config
from termcolor import colored
from fuzzywuzzy import fuzz
from typing import Tuple
from typing import Any

import re

recency_ratings = {
    1: "Hot",
    2: "Standard",
    3: "Old",
    4: "Very Old",
}


def keyword_search(keyword: str, driver: webdriver.Firefox) -> bool:
    """
    Searches for a keyword on YouTube using the provided keyword and a Firefox WebDriver.
    It searches with the filter of "Videos" enabled so that only videos are displayed.

    Parameters:
        keyword (str): The keyword to search for on YouTube.
        driver (webdriver.Firefox): A Firefox WebDriver instance.

    Returns:
        bool: True if the search was successful, False otherwise.
    """
    try:
        driver.get(f"https://www.youtube.com/results?search_query={keyword}&sp=EgIQAQ%253D%253D")
        return True
    except Exception as e:
        print(f"Error searching for keyword: {e}")
        return False


def views_to_int(views: str) -> int:
    """
    Convert views to an integer value.

    Parameters:
        views (str): The string representation of the views.

    Returns:
        int: The integer value of the views.
    """
    views = views.strip("views").strip("view").strip()
    if 'K' in views:
        return int(float(views.replace('K', '')) * 1000)
    elif 'M' in views:
        return int(float(views.replace('M', '')) * 1000000)
    else:
        try:
            return int(views)
        except:  #If views = "No views"
            return 0


def get_title_views_recency(driver: webdriver.Firefox, index: int) -> Tuple[str, int, float]:
    """
    Retrieves the title, views, and recency of a YouTube video using the provided Firefox WebDriver and index.

    Parameters:
        driver (webdriver.Firefox): A Firefox WebDriver instance.
        index (int): The index of the video in the YouTube search results.

    Returns:
        tuple: A tuple containing the title of the video as a string, the views as an integer, and the recency as a float.
    """
    config = load_config('config.json')
    wait = WebDriverWait(driver, config["Timeout"])

    # Wait for the video title to be present
    title_xpath = f'/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[{index}]/div[1]/div/div[1]/div/h3/a/yt-formatted-string'
    title_element = wait.until(ec.presence_of_element_located((By.XPATH, title_xpath)))

    title = title_element.text.split(" by ")[0].strip()

    # Wait for the video views to be present
    views_xpath = f"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[{index}]/div[1]/div/div[1]/ytd-video-meta-block/div[1]/div[2]/span[1]"
    views_element = wait.until(ec.presence_of_element_located((By.XPATH, views_xpath)))
    views_data = views_element.text.strip("views")
    views = views_to_int(views_data)

    # Wait for the recency information to be present
    recency_xpath = f"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[{index}]/div[1]/div/div[1]/ytd-video-meta-block/div[1]/div[2]/span[2]"
    recency_element = wait.until(ec.presence_of_element_located((By.XPATH, recency_xpath)))
    recency_data = recency_element.text
    recency_match = re.search(r'(\d+)\s(hours?|days?|minutes?|weeks?|months?|years?)\sago', recency_data)

    # Convert recency to days if matched
    recency_in_days = convert_recency_to_days(recency_match.group(1), recency_match.group(2)) if recency_match else 0.01

    return title, views, recency_in_days


def convert_recency_to_days(amount: str, unit: str) -> float:
    """
    Converts a YouTube video recency from a string format to a float format in days.

    Parameters:
        amount (str): The amount of time in the unit provided.
        unit (str): The unit of time.
    """
    amount = int(amount)
    if "minute" in unit:
        return round(amount / 1440, 4)
    elif "hour" in unit:
        return round(amount / 24, 4)
    elif "day" in unit:
        return float(amount)
    elif "week" in unit:
        return float(amount * 7)
    elif "month" in unit:
        return float(amount * 30)
    elif "year" in unit:
        return float(amount * 365)
    return 0.0


def get_subscribers(driver: webdriver.Firefox, index: int) -> int:
    """
    Retrieves the number of subscribers of the channel of a video.

    Parameters:
        driver (webdriver.Firefox): A Firefox WebDriver instance.
        index (int): The index of the video in the YouTube search results page.

    Returns:
        int: The number of subscribers of the channel of the video.
    """
    config = load_config('config.json')
    wait = WebDriverWait(driver, config["Timeout"])

    # In case of any issue (e.g., empty or invalid text), return the maximum subscriber count to avoid adding the channel and bugging out later
    try:
        xpath = f'/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[{index}]/div[1]/div/div[2]/div/div/div[1]'
        subscribers_element = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        subscribers_text = subscribers_element.text

    except:
        return config["Max_Subscriber_Count"]+1

    try:
        if 'K' in subscribers_text:
            return int(float(subscribers_text.replace('K', '').replace(',', '').strip()) * 1000)
        elif 'M' in subscribers_text:
            return int(float(subscribers_text.replace('M', '').replace(',', '').strip()) * 1000000)
        else:
            return int(subscribers_text.replace(',', '').strip())

    except:
        return config["Max_Subscriber_Count"]+1


def get_channel_id(driver: webdriver.Firefox, index: int) -> str:
    """
    Retrieves the channel ID of the channel of a video.

    Parameters:
        driver (webdriver.Firefox): A Firefox WebDriver instance.

    Returns:
        str: The channel ID of the channel of the video.
    """
    config = load_config('config.json')
    wait = WebDriverWait(driver, config["Timeout"])

    xpath_to_channel = f"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[{index}]/div[1]/div/div[2]/ytd-channel-name/div/div/yt-formatted-string/a"
    wait.until(ec.element_to_be_clickable((By.XPATH, xpath_to_channel))).click()

    xpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-tabbed-page-header/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/div/div[2]/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-content-metadata-view-model/div[1]/span"

    try:
        handle_element = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))

        handle = handle_element.text.replace("subscribers", "").strip()
        return handle
    except Exception as e:
        return ""


def get_video_duration(driver: webdriver.Firefox, index: int) -> float:
    """
    Retrieves the duration of a video and converts it to minutes.

    Parameters:
        driver (webdriver.Firefox): A Firefox WebDriver instance.
        index (int): The index of the video in the YouTube search results.

    Returns:
        float: The duration of the video in minutes.
    """
    config = load_config('config.json')
    wait = WebDriverWait(driver, config["Timeout"])

    try:
        xpath = f"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[{index}]/div[1]/ytd-thumbnail/a/div[1]/ytd-thumbnail-overlay-time-status-renderer/div[1]/badge-shape/div"
        duration_element = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))

        duration_text = duration_element.text.strip()
        return convert_duration_to_minutes(duration_text)
    except Exception as e:
        return 0.01


def convert_duration_to_minutes(duration: str) -> float:
    """
    Converts a duration string to minutes.

    Parameters:
        duration (str): The duration as a string, in the format "1:23", "12:34", "1:23:45".

    Returns:
        float: The duration in minutes.
    """
    pattern = re.compile(r'(?:(\d+):)?(\d+):(\d+)')
    match = pattern.match(duration)

    if not match:
        raise ValueError("Invalid duration format")

    hours, minutes, seconds = match.groups()

    hours = int(hours or 0)
    minutes = int(minutes)
    seconds = int(seconds)

    total_minutes = hours * 60 + minutes + seconds / 60
    return total_minutes


def calculate_similarity_weight(title: str, keyword: str) -> float:
    """
    Calculates the similarity weight between the video title and the keyword.
    Uses the fuzz library to compare the two strings.

    Args:
        title (str): The title of the video.
        keyword (str): The search keyword.

    Returns:
        float: Similarity weight as a percentage.
    """
    similarity = fuzz.partial_ratio(title.lower(), keyword.lower())
    return similarity


def calculate_video_rating(title: str, keyword: str, views: int, recency: float, duration: float, subscribers: int) -> Tuple[float, float, int]:
    """
    Calculates the video rating score based on the video title, keyword, views, recency, duration, and subscribers.

    Parameters:
        title (str): The title of the video.
        keyword (str): The search keyword.
        views (int): The number of views of the video.
        recency (float): The number of days since the video was uploaded.
        duration (float): The duration of the video in minutes.
        subscribers (int): The number of subscribers of the channel of the video.

    Returns:
        tuple: A tuple containing the volume score, competition score, and recency score of the video.
    """
    similarity_weight = calculate_similarity_weight(title, keyword) / 100

    volume_score = int(views / recency)

    if subscribers < 250:
        channel_score = 0
    elif subscribers < 1000:
        channel_score = 1
    elif subscribers < 2000:
        channel_score = 2
    elif subscribers < 3000:
        channel_score = 3
    elif subscribers < 5000:
        channel_score = 4
    elif subscribers < 7000:
        channel_score = 5
    elif subscribers < 15000:
        channel_score = 6
    elif subscribers < 30000:
        channel_score = 7
    elif subscribers < 50000:
        channel_score = 8
    elif subscribers < 100000:
        channel_score = 9
    else:
        channel_score = 10

    if duration < 2:
        length_score = 0
    elif duration < 5:
        length_score = 1
    elif duration < 8:
        length_score = 2
    else:
        length_score = 3

    competition_score = (channel_score + length_score) * similarity_weight

    if recency <= 1:
        recency_score = 1
    elif recency <= 11:
        recency_score = 2
    elif recency <= 24:
        recency_score = 3
    else:
        recency_score = 4

    return volume_score, competition_score, recency_score


def scrape_keyword_data(keyword: str, driver: webdriver.Firefox) -> Any:
    """
    Scrapes the title, views, and recency for the top 3 videos for a given keyword.

    Parameters:
        keyword (str): The keyword to search for on YouTube.
        driver (webdriver.Firefox): A Firefox WebDriver instance.

    Returns:
        list[dict]: A list of dictionaries, each containing the title, views, and recency of a video.
    """
    config = load_config('config.json')

    # Default values
    volume_total = 0
    competition_total = 0
    recency_rating_total = 0

    for i in range(1, config["Max_Videos_Scraped"]+1):
        title, views, recency = get_title_views_recency(driver, i)
        duration = round(get_video_duration(driver, i), 2)

        subscribers = get_subscribers(driver, i)

        if subscribers < config.get('Max_Subscriber_Count', 5000):
            print(colored("⏳  | Subscriber count under threshold, storing in database...", "yellow"))
            channel_id = get_channel_id(driver, i)
            driver.back()
            if channel_id != "":
                add_channel_to_db(channel_id, subscribers)

        volume, competition, recency_score = calculate_video_rating(keyword, title, views, recency, duration, subscribers)
        competition = round(competition)

        volume_total += volume
        competition_total += competition
        recency_rating_total += recency_score


    volume = round(volume_total/config["Max_Videos_Scraped"])
    competition = round(competition_total/config["Max_Videos_Scraped"])
    recency_rating = round(recency_rating_total/config["Max_Videos_Scraped"])
    recency_rating = recency_ratings.get(recency_rating)
    return [volume, competition, recency_rating]
