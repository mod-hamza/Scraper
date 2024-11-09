r"""
 _  __                                 _   __  __            _
| |/ / ___  _  _ __ __ __ ___  _ _  __| | |  \/  | __ _  ___| |_  ___  _ _
| ' < / -_)| || |\ V  V // _ \| '_|/ _` | | |\/| |/ _` |(_-<|  _|/ -_)| '_|
|_|\_\\___| \_, | \_/\_/ \___/|_|  \__,_| |_|  |_|\__,_|/__/ \__|\___||_|
            |__/
"""
# Coded by : https://github.com/mod-hamza/
# Date : 6/9/2024

from termcolor import colored
from yt_keywords import *
from database import *
from youtube import *
from utils import *

import time
import sys


def main():
    """
    Main function to start the script.

    This function cleans duplicate keywords from the database,
    prints the YouTube ASCII and the Keyword Master ASCII,
    and enters a loop where it checks the database for keywords.
    If a keyword is found, it scrapes the keyword data and adds it to the database.
    Then it moves on to channel selection.
    Scrapes channels for keywords
    """
    try:
        clean_duplicate_keywords()
        clean_duplicate_channels()

        config = load_config('config.json')
        print(colored(config["YouTube ASCII"], "red"))
        print(colored(config["Keyword Master"], "green"))

        print(colored("⏳  | Starting Firefox...", "yellow"))
        driver = start_firefox()
        driver.get("https://www.youtube.com/")
        time_start = time.time()

        keywords_analysed, keywords_found, channels_analysed, channels_found = 0, 0, 0, 0

        while True:
            print(colored("-"*50, "white"))
            keyword = next_keyword()

            if keyword:
                print(colored(f"✅  | Keyword selected: {keyword}", "green"))

                count = 0
                while not keyword_search(keyword, driver):
                    count += 1

                    if count == 3:
                        print(colored("❌  | Keyword not found", "red"))
                        remove_keyword(keyword)
                        continue

                time.sleep(10)
                print(colored("⏳  | Analyzing Keyword...", "yellow"))
                volume, competition, recency = scrape_keyword_data(keyword, driver)
                print(colored("✅  | Keyword analyzed...", "green"))

                update_keyword(keyword, volume, competition, recency)
                time_end = time.time()
                print(colored(f"🕒  | Time running: {time_end - time_start:.2f} seconds", "yellow"))

            else:
                channel = next_channel()
                if channel is None:
                    print(colored("🚫  | No keyword or channel found", "red"))
                    break

                print(colored(f"✅  | Channel selected: {channel}", "green"))

                count = 0
                while not search_youtube_channel(channel, driver):
                    print(colored(f"⏳  | Searching YouTube for channel...", "yellow"))
                    count += 1

                    if count == 3:
                        print(colored("❌  | Channel not found", "red"))
                        remove_channel(channel)
                        continue

                channel_subs = get_channel_subs(driver)
                print(colored(f"✅  | Subscribers: {channel_subs}", "green"))
                update_channel(channel, channel_subs)

                print(colored("⏳  | Scraping videos...", "yellow"))
                video_data = get_channel_videos(driver)

                if video_data:
                    for videos in video_data:
                        keywords = videos.get("keywords")
                        for keyword in keywords:
                            add_null_keyword(keyword, channel)

                    clean_duplicate_keywords()
                print(colored("✅  | Videos scraped, keywords stored", "green"))
                time_end = time.time()
                print(colored(f"🕒  | Time running: {time_end - time_start:.2f} seconds", "yellow"))

    except KeyboardInterrupt:
        store_report(keywords_analysed, keywords_found, channels_analysed, channels_found, time_start)
        print(colored("✅  | Report stored in reports.md", "green"))
        print(colored("🛑  | Exiting...", "red"))
        sys.exit()

if __name__ == "__main__":
    main()
