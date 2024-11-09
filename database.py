from utils import load_config

import mysql.connector


# channel_id, channel_handle, channel_status, channel_researched, channel_subs

def next_channel() -> str | None:
    """
    Retrieves the next channel from the database that has not been researched in over 2 weeks.

    Function:
        Connects to the channel database, executes a query to select the next channel,
        and updates the researched date to the current date.

    Returns:
        The selected channel handle
    """
    config = load_config('config.json')
    mydb = mysql.connector.connect(
        host=config["Channel_DB_host"],
        user=config["Channel_DB_user"],
        database=config["Channel_DB_name"],
        password=config["Channel_DB_password"]
    )
    mycursor = mydb.cursor()

    query = """SELECT channel_handle FROM channels
               WHERE channel_researched IS NULL or 0
               OR channel_researched < NOW() - INTERVAL 20 DAY
               ORDER BY channel_researched ASC LIMIT 1"""
    mycursor.execute(query)
    result = mycursor.fetchone()

    if result:
        query = """UPDATE channels SET channel_researched = NOW() WHERE channel_handle = %s"""
        mycursor.execute(query, (result[0],))
        mydb.commit()

    mydb.close()
    return result[0] if result else None


# keyword_id, keyword_term, volume, competition, recency, keyword_from

def next_keyword() -> str | None:
    """
    Retrieves the next keyword from the database that has any null values.

    Returns:
        The next keyword (str) if found, otherwise None
    """
    config = load_config('config.json')
    mydb = mysql.connector.connect(
        host=config["Keyword_DB_host"],
        user=config["Keyword_DB_user"],
        database=config["Keyword_DB_name"],
        password=config["Keyword_DB_password"]
    )
    mycursor = mydb.cursor()

    query = """
    SELECT * FROM keywords
    WHERE keyword_term IS NULL
       OR volume IS NULL
       OR competition IS NULL
       OR recency IS NULL
       OR keyword_from IS NULL
    LIMIT 1;
    """

    mycursor.execute(query)
    result = mycursor.fetchone()

    if result:
        return result[1]
    else:
        return None


def remove_channel(channel_handle: str) -> None:
    """
    Removes a channel from the database based on the provided channel handle.

    Args:
        channel_handle (str): The handle of the channel to be removed.

    Returns:
        bool: True if the channel was successfully removed, False otherwise.
    """
    config = load_config('config.json')

    mydb = mysql.connector.connect(
        host=config["Channel_DB_host"],
        user=config["Channel_DB_user"],
        database=config["Channel_DB_name"],
        password=config["Channel_DB_password"]
    )
    mycursor = mydb.cursor()

    query = "DELETE FROM channels WHERE channel_handle = %s"
    mycursor.execute(query, (channel_handle,))
    mydb.commit()
    mydb.close()
    print(f"Removed channel: {channel_handle}")

    return


def remove_keyword(keyword_term: str) -> None:
    """
    Removes a keyword from the database based on the provided keyword term.

    Args:
        keyword_term (str): The term of the keyword to be removed.

    Returns:
        bool: True if the keyword was successfully removed, False otherwise.
    """
    config = load_config('config.json')

    mydb = mysql.connector.connect(
        host=config["Keyword_DB_host"],
        user=config["Keyword_DB_user"],
        database=config["Keyword_DB_name"],
        password=config["Keyword_DB_password"]
    )
    mycursor = mydb.cursor()

    query = "DELETE FROM keywords WHERE keyword_term = %s"
    mycursor.execute(query, (keyword_term,))
    mydb.commit()
    mydb.close()

    return


def add_null_keyword(keyword_term: str, channel_handle: str) -> None:
    """
    Adds a null keyword to the database based on the provided keyword term.

    Args:
        channel_handle (str): The handle of the channel to be added.
        keyword_term (str): The term of the keyword to be added.

    Returns:
        bool: True if the keyword was successfully added, False otherwise.
    """
    channel_handle = channel_handle.strip("@")
    channel_handle = "@" + channel_handle
    config = load_config('config.json')

    mydb = mysql.connector.connect(
        host=config["Keyword_DB_host"],
        user=config["Keyword_DB_user"],
        database=config["Keyword_DB_name"],
        password=config["Keyword_DB_password"]
    )
    mycursor = mydb.cursor()

    query = "INSERT INTO keywords (keyword_term, keyword_from) VALUES (%s, %s)"
    mycursor.execute(query, (keyword_term, channel_handle))

    mydb.commit()
    mydb.close()

    return


def update_channel(channel, subscribers) -> None:
    """
    Updates the subscribers of a channel in the database.

    Args:
        channel (str): The name of the channel.
        subscribers (int): The number of subscribers.

    Returns:
        None
    """
    config = load_config('config.json')

    mydb = mysql.connector.connect(
        host=config["Channel_DB_host"],
        user=config["Channel_DB_user"],
        database=config["Channel_DB_name"],
        password=config["Channel_DB_password"]
    )
    mycursor = mydb.cursor()

    query = "UPDATE channels SET channel_subs = %s WHERE channel_handle = %s"
    mycursor.execute(query, (subscribers, channel))

    mydb.commit()
    mydb.close()

    return


def clean_duplicate_keywords() -> None:
    config = load_config('config.json')

    mydb = mysql.connector.connect(
        host=config["Keyword_DB_host"],
        user=config["Keyword_DB_user"],
        database=config["Keyword_DB_name"],
        password=config["Keyword_DB_password"]
    )
    mycursor = mydb.cursor()

    # Query to delete duplicates based on keyword_term and keyword_from
    delete_duplicates_query = """
    DELETE k1 FROM keywords k1
    INNER JOIN keywords k2
    ON k1.keyword_term = k2.keyword_term
    AND k1.keyword_from = k2.keyword_from
    AND k1.keyword_id > k2.keyword_id
    """
    mycursor.execute(delete_duplicates_query)

    mydb.commit()
    mydb.close()

    return


def add_channel_to_db(channel_id: str, subscribers: int) -> None:
    """
    Adds a new channel to the database with the provided channel_id and subscribers.

    Args:
        channel_id (str): The ID of the channel to be added.
        subscribers (int): The number of subscribers of the channel.

    Returns:
        None
    """
    config = load_config('config.json')

    # Connect to the database
    mydb = mysql.connector.connect(
        host=config["Channel_DB_host"],
        user=config["Channel_DB_user"],
        database=config["Channel_DB_name"],
        password=config["Channel_DB_password"]
    )
    mycursor = mydb.cursor()

    query = """
        INSERT INTO channels (channel_handle, channel_researched, channel_subs)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            channel_researched = VALUES(channel_researched),
            channel_subs = VALUES(channel_subs)
    """

    mycursor.execute(query, (channel_id, 0, subscribers))

    mydb.commit()
    mydb.close()

    return


def clean_duplicate_channels() -> None:
    """
    Removes duplicate channels from the database, retaining the row with the smallest channel_id
    for each unique channel_handle.
    """
    config = load_config('config.json')

    mydb = mysql.connector.connect(
        host=config["Channel_DB_host"],
        user=config["Channel_DB_user"],
        database=config["Channel_DB_name"],
        password=config["Channel_DB_password"]
    )
    mycursor = mydb.cursor()

    # Query to delete duplicates based on channel_handle, keeping the one with the smallest channel_id
    delete_duplicates_query = """
    DELETE c1 FROM channels c1
    INNER JOIN channels c2
    ON c1.channel_handle = c2.channel_handle
    AND c1.channel_id > c2.channel_id
    """

    mycursor.execute(delete_duplicates_query)

    mydb.commit()
    mydb.close()

    return


# (keyword, volume, competition, recency)
def update_keyword(keyword_term: str, volume: int, competition: int, recency: int) -> None:
    """
    Updates the volume, competition, and recency of a keyword in the database.

    Args:
        keyword_term (str): The term of the keyword to be updated.
        volume (int): The new volume of the keyword.
        competition (int): The new competition of the keyword.
        recency (int): The new recency of the keyword.

    Returns:
        None
    """
    config = load_config('config.json')

    mydb = mysql.connector.connect(
        host=config["Keyword_DB_host"],
        user=config["Keyword_DB_user"],
        database=config["Keyword_DB_name"],
        password=config["Keyword_DB_password"]
    )
    mycursor = mydb.cursor()

    query = "UPDATE keywords SET volume = %s, competition = %s, recency = %s WHERE keyword_term = %s"
    mycursor.execute(query, (volume, competition, recency, keyword_term))

    mydb.commit()
    mydb.close()

    return
