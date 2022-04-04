import feedparser
import json
import sys
import requests
import os
import dotenv
import hashlib
from bs4 import BeautifulSoup

# Validate CLI arguments
if len(sys.argv) < 2:
    print("Usage: main.py <nitter_rss_feed_url> <keyword>")
    sys.exit(1)

# Parameters
dotenv.load_dotenv()
POWER_RETWEET_API_URL = os.getenv("POWER_RETWEET_API_URL")

# Get the RSS feed
def main():
    
    # Get the RSS feed URL
    url = sys.argv[1]

    # Whether the keyword argument is set
    if len(sys.argv) > 2:
        keyword_enabled = True
        keyword = sys.argv[2]
    else:
        keyword_enabled = False

    # Validate URL
    if not validate_url(url):
        print("Invalid URL")
        sys.exit(1)

    # Parse the RSS feed
    try:
        NewsFeed = feedparser.parse(sys.argv[1])
        entry = NewsFeed.entries[0]
    except:
        print ("Error")
        exit(1)

    # Get the RSS feed elements
    title = entry.title
    link = entry.link
    description = entry.description

    # Determine if the description contains keyword
    if keyword_enabled:
        if keyword in description:
            print("Keyword found")
        else:
            print("Keyword not found")
            exit(1)

    # Encode the URL as a string with md5
    tmp_filename = hashlib.md5(link.encode('utf-8')).hexdigest()

    # file path named after the md5 hash of the URL
    cwd = os.getcwd()
    file_path = cwd + "/tmp/" + tmp_filename + ".json"

    # Check if the file exists
    if os.path.isfile(file_path):
        # Read the file and decode the JSON as an dictionary
        with open(file_path, 'r', encoding='utf-8') as f:
            stored_data = json.load(f)
        # Compare data with entry
        if (stored_data['link'] == link):
            print("No new data")
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
        r = requests.get(url)
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False

# Call main function
if __name__ == "__main__":
    main()
