import datetime
import os

import bs4
from feedgen.feed import FeedGenerator
from playwright.sync_api import sync_playwright

HOME_DIR = "/var/www/jamesg.blog/"

url = "https://openai.com/news"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_extra_http_headers(headers)
    page.goto(url)
    html = page.content()
    browser.close()

soup = bs4.BeautifulSoup(html, "html.parser")

urls = {}

for a in soup.find_all("a"):
    
    if not a.has_attr("href"):
        continue

    if not a["href"].startswith("/index"):
        continue

    title = a.get("aria-label", None)

    if title is None:
        continue

    date = None

    for span in a.find_all("span"):
        if span.has_attr("class") and "text-small" in span["class"]:
            try:
                date = datetime.datetime.strptime(span.text, "%b %d, %Y")
            except ValueError:
                pass

    if date is None:
        continue

    date = date.replace(tzinfo=datetime.timezone.utc)

    urls[title] = {
        "url": "https://openai.com" + a["href"],
        "date": date,
    }

urls = {url: urls[url] for url in urls if urls[url]["date"] is not None}

fg = FeedGenerator()
fg.id("https://openai.com/blog")
fg.title("OpenAI Blog")
fg.author({"name": "Open AI"})
fg.link(href="https://openai.com/blog", rel="alternate")
fg.logo("https://openai.com/favicon.ico")
fg.subtitle("OpenAI Blog posts.")
fg.link(href="https://jamesg.blog/openai.xml", rel="self")

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
