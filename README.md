# YouTube Keyword and Channel Scraper

## Introduction
This project is a YouTube keyword and channel scraper that uses Selenium WebDriver to automate the process of gathering data from YouTube. It scrapes video titles, views, recency, and other relevant information for a given keyword or channel.

## Description
The scraper is designed to help users analyze YouTube keywords and channels by collecting data such as video views, upload dates, and channel subscribers. The data is then stored in a database for further analysis.

## Creation
- **Author**: [mod-hamza](https://github.com/mod-hamza)
- **Date**: 6/9/2024

## Features
- Scrapes YouTube for video titles, views, recency, and duration.
- Retrieves channel subscriber counts.
- Stores data in a MySQL database.
- Analyzes keywords and channels for further insights.
- Generates reports with the analysis results.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/mod-hamza/youtube-keyword-scraper.git
    cd yt-scraper
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a copy of `config.json` and name it as `config.json`. Make sure to fill it in with all details.
    ```sh
    cp config copy.json config.json
    ```

4. Ensure you have the necessary WebDriver for Firefox (geckodriver) installed and configured in your PATH. Alternatively it can be placed in the `./assets` folder.

## Usage
1. Configure the `config.json` file with your settings (see Configuration section).
2. Run the main script:
    ```sh
    python main.py
    ```

## Configuration
The `config.json` file contains various settings for the scraper. Below is an example configuration:

```json
{
    "Firefox Profile": "path\\to\\firefox\\profile",
    "Geckodriver Path": "assets\\geckodriver.exe",
    "Channel_DB_host": "",
    "Channel_DB_name": "",
    "Channel_DB_user": "",
    "Channel_DB_password": "",
    "Keyword_DB_host": "",
    "Keyword_DB_name": "",
    "Keyword_DB_user": "",
    "Keyword_DB_password": "",
    "YouTube ASCII": "ASCII already provided in config.json",
    "Keyword Master": "ASCII already provided in config.json",
    "Max_Subscriber_Count": 5000,
    "Days": 0.5,
    "Max_Videos_Scraped": 3,
    "Timeout": 30,
    "Views_threshold": 20
}
```

## Contributing
Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.MD) file for details.
