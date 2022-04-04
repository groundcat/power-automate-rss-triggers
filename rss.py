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
    print("Usage: main.py <rss_feed_url> <mode>")
    print("Mode: 'title' - Use title, 'description' - Use description")
    sys.exit(1)

# Parameters
dotenv.load_dotenv()
POWER_API_URL = os.getenv("POWER_API_URL")
TRANSLATION_ENABLED = os.getenv("POWER_API_URL")
DEEPL_API_URL = os.getenv("DEEPL_API_URL")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_TARGET_LANGUAGE = os.getenv("DEEPL_TARGET_LANGUAGE")

# Get the RSS feed
def main():
    
    # Get the RSS feed URL
    url = sys.argv[1]

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

    # Use description or title
    if (sys.argv[1] == "title"):
        # Use title
        body = title
    else:
        # Use description
        body = description

    # Get Chinese social media title
    body = get_chinese_sm_title(body)

    # Get text from HTML
    body = get_text_from_html(body)

    # Cap the body to be 250 characters or less
    if len(body) > 250:
        body = body[:250] + "..."

    # Translate the RSS feed elements
    print(f"Translating: {body}")
    if TRANSLATION_ENABLED:
        body = deepl_translation(body, DEEPL_TARGET_LANGUAGE)

    # Encode the dictionary as payload
    payload = {
        "link": link,
        "body": body
    }

    # Send the data to the Azure Function
    response = requests.post(POWER_API_URL, json=payload)
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

def deepl_translation(text, target_language):
    # Make a POST request with form data
    form_data = {
        "text": text,
        "target_lang": target_language,
        "auth_key": DEEPL_API_KEY
    }
    response = requests.post(DEEPL_API_URL, data=form_data, headers={"Authorization": DEEPL_API_KEY})

    # Check for errors
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        sys.exit(1)

    # Load the response as json
    response_json = response.json()

    # Print the translated text
    translated_text = response_json['translations'][0]['text']
    print(f"Translated text: {translated_text}")

    # Return the translated text
    return translated_text

def get_text_from_html(html_text):
    # Remove HTML tags
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    # Replace 
    text = text.replace("#", " ")
    text = text.replace("【", "")
    text = text.replace("】", " ")
    text = text.replace("@", "")
    return text

def get_chinese_sm_title(text):
    # If the text start with 【
    if text[0] == "【":
        print("Chinese social media title")
        # Get the text between the parens
        text = text.split("【")[1]
        text = text.split("】")[0]
    return text

# Call main function
if __name__ == "__main__":
    main()



