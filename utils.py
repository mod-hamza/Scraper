
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import json
import time


def load_config(config_path: str):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config


def start_firefox() -> webdriver.Firefox:
    config = load_config('config.json')
    geckodriver_path = config['Geckodriver Path']
    firefox_profile_path = config['Firefox Profile']

    profile = webdriver.FirefoxProfile(firefox_profile_path)

    options = Options()
    options.profile = profile

    service = Service(geckodriver_path)

    driver = webdriver.Firefox(
        service=service,
        options=options
    )

    return driver


def store_report(keywords_analysed, keywords_found, channels_analysed, channels_found, time_started):
    """
        Storing details in reports.md file
        With date and time started and ended
    """
    file = "reports.md"

    with open(file, "a") as f:
        f.write("\n---\n\n")
        f.write(f"Time started: {time.strftime('%I:%M %p, %d %B %Y', time.localtime(time_started))}\n")
        f.write(f"Time ended: {time.strftime('%I:%M %p, %d %B %Y', time.localtime())}\n\n")
        f.write(f"Keywords analysed: {keywords_analysed}\n")
        f.write(f"Keywords found: {keywords_found}\n")
        f.write(f"Channels analysed: {channels_analysed}\n")
        f.write(f"Channels found: {channels_found}\n\n")
