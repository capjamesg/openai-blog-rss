import datetime
import os

import bs4
import requests
from feedgen.feed import FeedGenerator

HOME_DIR = "/var/www/jamesg.blog/"

url = "https://openai.com/blog"

page = requests.get(url)

soup = bs4.BeautifulSoup(page.content, "html.parser")

# traverse whole tree of A tags
urls = {}

for a in soup.find_all("a"):
    # if any child is h3, print it
    # get sr-only
    if a.find("span", class_="sr-only"):
        date = a.find("span", class_="sr-only").text
        # May 18, 2023
        date = datetime.datetime.strptime(date, "%B %d, %Y")
        # add PT timezone
        date = date.strftime("%Y-%m-%dT%H:%M:%S") + "-08:00"
    else:
        date = None

    if a.find("h3"):
        urls[a.find("h3").text] = {
            "url": "https://openai.com" + a["href"],
            "date": date,
        }

fg = FeedGenerator()
fg.id("https://openai.com/blog")
fg.title("OpenAI Blog")
fg.author({"name": "Open AI"})
fg.link(href="https://openai.com/blog", rel="alternate")
fg.logo("https://openai.com/favicon.ico")
fg.subtitle("OpenAI Blog posts.")
fg.link(href="https://jamesg.blog/openai.xml", rel="self")

# order urls by date
urls = dict(sorted(urls.items(), key=lambda item: item[1]["date"], reverse=False))

for link in urls:
    fe = fg.add_entry()
    fe.id(urls[link]["url"])
    fe.title(link)
    fe.link(href=urls[link]["url"])
    fe.description(link)
    fe.pubDate(urls[link]["date"])

fg.language("en")

fg.rss_file(os.path.join(HOME_DIR, "openai.xml"))
