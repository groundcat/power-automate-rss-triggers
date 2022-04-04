# Power Automate triggers

RSS custom triggers for your Microsoft Power Automate flows

**rss.py**

Triggers a PA flow (e.g. post new tweet) when a new RSS item is found.

Usage:

```
Usage: main.py <rss_feed_url> <mode>
```

**retweet.py**

Triggers a PA flow (e.g. post retweet) when a Twitter user made a new tweet that contains a certain keyword by monitoring with a [Nitter](https://nitter.net/) instance's RSS feed.

Usage:

```
Usage: main.py <nitter_rss_feed_url> <keyword>
```

## Requirements

Install dependencies from `requirements.txt`.

```
pip3 install -r requirements.txt
```

Create an automated flow, use `When a HTTP request is received` as your PA flow trigger and use `*_schema.json` as the `Request Body JSON Schema`.

Update config in `.env`.
