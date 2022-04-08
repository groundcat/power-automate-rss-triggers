import feedparser
import json
import sys
import requests
import os
import dotenv
import hashlib
from bs4 import BeautifulSoup
import random

# Validate CLI arguments
if len(sys.argv) < 2:
    print("Usage: main.py <twitter_handle> <keyword>")
    sys.exit(1)

# Parameters
dotenv.load_dotenv()
POWER_RETWEET_API_URL = os.getenv("POWER_RETWEET_API_URL")

# Get the RSS feed
def main():
    
    # Get the RSS feed URL
    twitter_handle = sys.argv[1]
    # Trim the handle
    twitter_handle = twitter_handle.replace("@", "")
    twitter_handle = twitter_handle.strip()

    # Get a random line from "nitter_instances.txt"
    with open("nitter_instances.txt", "r") as f:
        lines = f.readlines()
        # Remove the newline character
        lines = [line.rstrip('\n') for line in lines]
        random_line = lines[random.randint(0, len(lines) - 1)]
    
    # Get the RSS feed URL
    url = "https://" + random_line + "/" + twitter_handle + "/rss"
    print("==========================================================")
    print(f"URL: {url}")

    # Whether the keyword argument is set
    if len(sys.argv) > 2:
        keyword_enabled = True
        keyword = str(sys.argv[2])
        # Trim the keyword
        keyword = keyword.strip()
    else:
        keyword_enabled = False

    # Validate URL
    if not validate_url(url):
        print("Invalid URL")
        sys.exit(1)

    # Parse the RSS feed
    try:
        NewsFeed = feedparser.parse(url)
        entry = NewsFeed.entries[0]
    except:
        print ("Error")
        exit(1)

    # Get the RSS feed elements
    title = entry.title
    link = entry.link
    description = entry.description
    print(f"Title: {title}")

    # Determine if the description contains keyword
    if keyword_enabled:
        print(f"Looking for keyword: {keyword}")
        if keyword in title:
            print("Keyword found")
        else:
            print("Keyword not found")
            exit(1)

    # Encode the URL as a string with md5
    tmp_filename = hashlib.md5(twitter_handle.encode('utf-8')).hexdigest()

    # file path named after the md5 hash of the URL
    cwd = os.getcwd()
    file_path = cwd + "/tmp/" + tmp_filename + ".json"

    # Check if the file exists
    if os.path.isfile(file_path):
        # Read the file and decode the JSON as an dictionary
        with open(file_path, 'r', encoding='utf-8') as f:
            stored_data = json.load(f)
        # Compare data with entry
        if (stored_data['link'] == link or stored_data['title'] == title):
            print("No new data - matches stored data:")
            print(f"Title: {stored_data['title']}")
            print(f"Link: {stored_data['link']}")
            sys.exit(0)
        else:
            print("New data")

    # Write in uft-8 encoding to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False)

    # Get the status_id values from the link
    link_values = link.split("/")
    status_id = link_values[5]
    status_id = status_id.split("#")[0]
    print (f"status_id: {status_id}")

    # Encode the dictionary as payload
    payload = {
        "status_id": status_id,
    }

    # Send the data to the Azure Function
    response = requests.post(POWER_RETWEET_API_URL, json=payload)
    print(response.status_code)
    print(response.text)

    # Check for errors
    if response.status_code != 200:
        print(f"Error code: {response.status_code}")
        sys.exit(1)

    # Load the response as json
    print("Success")
    response_json = response.json()
    print(f"API response: {response_json}")

# Validate the URL
def validate_url(url):
    try:
        # Set a user-agent
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        # Get the response
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return True
        else:
            print(f"Error code: {r.status_code}")
            return False
    except:
        return False

# Call main function
if __name__ == "__main__":
    main()
