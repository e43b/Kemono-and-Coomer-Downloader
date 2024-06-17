import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Function to determine the base folder (Kemono or Coomer)
def determine_base_folder(url):
    parsed_url = urlparse(url)
    if "kemono.su" in parsed_url.netloc or "kemono.party" in parsed_url.netloc:
        return "Kemono"
    elif "coomer.su" in parsed_url.netloc or "coomer.party" in parsed_url.netloc:
        return "Coomer"
    else:
        return "Others"

# Function to find the author name and platform
def get_author_and_platform(soup):
    # Find the author name
    author_meta_tag = soup.find("meta", attrs={"name": "artist_name"})
    if author_meta_tag:
        author_name = author_meta_tag["content"].strip()
    else:
        # If not found, use the previous logic
        author_tag = soup.find("a", class_="post__user-name")
        if author_tag:
            author_name = author_tag.text.strip()
        else:
            author_meta_tag = soup.find("meta", property="og:image")
            author_content = author_meta_tag["content"]
            author_name = author_content.split("/")[-1].split("-")[0]

    platform_meta_tag = soup.find("meta", property="og:image")
    platform_content = platform_meta_tag["content"]
    platform_name = urlparse(platform_content).path.split("/")[2]

    return author_name, platform_name

# Function to correct the link
def correct_link(link):
    if not link.endswith("dms"):
        link += "/dms"
    return link

# Function to extract article content and create text files
def extract_content(link, base_folder, author_folder):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("article", class_="dm-card")

    dm_folder = os.path.join(base_folder, author_folder, "DMs")
    os.makedirs(dm_folder, exist_ok=True)  # Create folder if it doesn't exist

    for i, article in enumerate(articles, start=1):
        content = article.find("div", class_="dm-card__content").text.strip()
        published_date = article.find("div", class_="dm-card__added").text.strip()

        # Format the file title without extra spaces
        file_title = f"{i}_{published_date.replace(':', '-')}".replace(" ", "")

        file_path = os.path.join(dm_folder, f"{file_title}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
            file.write(f"\n\nPublished: {published_date}")

# Request URL(s) from the user
link = input('Enter the profile link you want to download DMs from: ')
link = correct_link(link)

# Make the HTTP request and get the HTML content
response = requests.get(link)
html_content = response.text

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Determine the base folder (Kemono or Coomer)
base_folder = determine_base_folder(link)

# Find the author name and platform
author_name, platform_name = get_author_and_platform(soup)

# Create the author's folder name with the platform
author_folder = f"{author_name}-{platform_name}"

# Extract content and create text files
extract_content(link, base_folder, author_folder)
