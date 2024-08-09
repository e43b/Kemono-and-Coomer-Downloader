import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import zipfile

# Function to extract information from a post
def extract_post_info(post_card, base_url):
    post_info = {}
    post_info['link'] = urljoin(base_url, post_card.find('a')['href'])
    post_info['title'] = post_card.find('header', class_='post-card__header').text.strip()

    attachments_div = post_card.find('div', string=lambda x: x and 'attachments' in x.lower())
    post_info['attachments'] = attachments_div.text.strip() if attachments_div else "No attachments"

    time_tag = post_card.find('time')
    post_info['date'] = time_tag['datetime'] if time_tag else "No date available"

    image_tag = post_card.find('img', class_='post-card__image')
    post_info['image'] = urljoin(base_url, image_tag['src']) if image_tag else "No image available"

    return post_info

# Function to extract the total number of posts
def get_total_posts(soup):
    total_posts_text = soup.find('small')
    if total_posts_text:
        total_posts = int(total_posts_text.text.strip().split(' of ')[1])
    else:
        total_posts = None
    return total_posts

# Function to save posts in a text file
def save_posts_to_file(posts, filename="posts_info.txt"):
    with open(filename, 'w', encoding='utf-8') as f:
        for post in posts:
            f.write(f"Link: {post['link']}\n")
            f.write(f"Título: {post['title']}\n")
            f.write(f"Número de arquivos: {post['attachments']}\n")
            f.write(f"Data do post: {post['date']}\n")
            f.write(f"Capa: {post['image']}\n")
            f.write("\n" + "-"*40 + "\n\n")

# Function to save post information to a text file
def salvar_info_post(soup, folder, save_comments_txt):
    info_file_path = os.path.join(folder, "info.txt")
    with open(info_file_path, "w", encoding="utf-8") as f:
        title_tag = soup.find("h1", class_="post__title")
        if title_tag:
            title = " ".join([span.text for span in title_tag.find_all("span")])
            f.write(f"Título: {title}\n\n")

        published_tag = soup.find("div", class_="post__published")
        if published_tag:
            published_date = published_tag.text.strip().split(": ")[1]
            f.write(f"Publication date: {published_date}\n\n")

        imported_tag = soup.find("div", class_="post__added")
        if imported_tag and ": " in imported_tag.text:
            imported_date = imported_tag.text.strip().split(": ")[1]
            f.write(f"Publication date: {imported_date}\n\n")

        tags_section = soup.find("section", id="post-tags")
        if tags_section:
            tags = [a.text for a in tags_section.find_all("a")]
            f.write(f"Tags: {', '.join(tags)}\n\n")

        attachment_tags = soup.find_all("a", class_="post__attachment-link")
        if attachment_tags:
            f.write("Attachments:\n")
            for attachment_tag in attachment_tags:
                attachment_url = attachment_tag["href"]
                attachment_name = attachment_tag.text.strip().split(" ")[-1]
                f.write(f"- {attachment_name}: {attachment_url}\n")
                browse_tag = attachment_tag.find_next("a", href=True, string="browse »")
                if browse_tag:
                    browse_url = urlparse(url)._replace(path=browse_tag["href"]).geturl()
                    f.write(f"  Conteúdo do anexo: {browse_url}\n")

        content_div = soup.find("div", class_="post__content")
        if content_div:
            content_pre = content_div.find("pre")
            if content_pre:
                content_text = content_pre.text.strip()
                f.write(f"\nPost Content:\n{content_text}\n\n")

        if save_comments_txt:
            comments_section = soup.find("footer", class_="post__footer")
            if comments_section:
                comments = comments_section.find_all("article", class_="comment")
                if comments:
                    f.write("Comments:\n")
                    for comment in comments:
                        comment_author = comment.find("a", class_="comment__name").text.strip()
                        comment_text = comment.find("p", class_="comment__message").text.strip()
                        comment_date = comment.find("time", class_="timestamp")["datetime"]
                        f.write(f"- {comment_author} ({comment_date}): {comment_text}\n\n")

# Function to download content from a URL
def baixar_conteudo(url, config):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    parsed_url = urlparse(url)
    base_folder = "Kemono" if "kemono.su" in parsed_url.netloc or "kemono.party" in parsed_url.netloc else "Coomer"

    author_tag = soup.find("a", class_="post__user-name")
    author_name = author_tag.text.strip() if author_tag else soup.find("meta", property="og:image")["content"].split("/")[-1].split("-")[0]

    platform_name = urlparse(soup.find("meta", property="og:image")["content"]).path.split("/")[2]
    author_folder = f"{author_name}-{platform_name}"

    post_id = soup.find("meta", attrs={"name": "id"})["content"]
    post_folder = post_id
    post_path = os.path.join(base_folder, author_folder, "posts", post_folder)
    os.makedirs(post_path, exist_ok=True)

    if config["save_info_txt"]:
        salvar_info_post(soup, post_path, config["save_comments_txt"])

    links_baixados = set()
    image_tags = soup.find_all("a", class_="fileThumb")

    for index, img_tag in enumerate(image_tags):
        image_url = img_tag["href"]
        if image_url not in links_baixados:
            image_response = requests.get(image_url)
            filename = f"image_{index + 1}.jpg"
            with open(os.path.join(post_path, filename), "wb") as f:
                f.write(image_response.content)
            links_baixados.add(image_url)

    # Cleanup filenames
    def sanitize_filename(filename):
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "")
        words_to_filter = ["Download"]
        for word in words_to_filter:
            filename = filename.replace(word, "")
        return filename.strip()
    
    if config["download_attachments"]:
        attachment_tags = soup.find_all("a", class_="post__attachment-link")
        for index, attachment_tag in enumerate(attachment_tags):
            attachment_url = attachment_tag["href"]
            if attachment_url not in links_baixados:
                attachment_response = requests.get(attachment_url)
                filename = attachment_tag.text.strip()
                filename = sanitize_filename(filename)
                with open(os.path.join(post_path, filename), "wb") as f:
                    f.write(attachment_response.content)
                links_baixados.add(attachment_url)

    if config["download_videos"]:
        video_tags = soup.find_all("a", class_="post__attachment-link")
        for index, video_tag in enumerate(video_tags):
            video_url = video_tag["href"]
            if video_url not in links_baixados:
                video_response = requests.get(video_url)
                filename = video_tag["download"]
                with open(os.path.join(post_path, filename), "wb") as f:
                    f.write(video_response.content)
                links_baixados.add(video_url)

    print(f"Content from post {url} downloaded successfully!")
    

    # Unzip all potential Zip files
    if config["unzip"]:
        for dirpath, _, filenames in os.walk(post_path):
            for filename in filenames:
                if filename.lower().endswith('.zip'):
                    file_path = os.path.join(dirpath, filename)
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            # Set the extraction path
                            #extraction_path = extract_to if extract_to else dirpath
                            print(f"Extracting {file_path} to {dirpath}")
                            zip_ref.extractall(dirpath)
                        os.remove(file_path)
                    except zipfile.BadZipFile:
                        print(f"Warning: '{file_path}' is not a valid zip file.")
                    except Exception as e:
                        print(f"Error extracting '{file_path}': {e}")

# Load settings from JSON file
with open("code/profileconfig.json", "r") as f:
    config = json.load(f)

# Load settings from profileconfig.json
with open("code/profileconfig.json", "r") as f:
    profile_config = json.load(f)

# URL base provided
base_url = input("Please enter Profile URL: ")

# Variable to store all posts
all_posts = []

# Iterate over pages to collect all posts
page_number = 0
while True:
    url = f"{base_url}?o={page_number * 50}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    if page_number == 0:
        total_posts = get_total_posts(soup)
        if total_posts:
            total_pages = (total_posts + 49) // 50
        else:
            total_pages = 1

    post_cards = soup.find_all('article', class_='post-card post-card--preview')
    if not post_cards:
        break

    for post_card in post_cards:
        post_info = extract_post_info(post_card, base_url)
        all_posts.append(post_info)

    if page_number >= total_pages - 1:
        break

    page_number += 1

# Filter posts based on profileconfig.json settings
filtered_posts = []
for post in all_posts:
    has_media = post['image'] != "No image available" or post['attachments'] != "No attachments"

    if profile_config['both']:
        filtered_posts.append(post)
    elif profile_config['files_only'] and has_media:
        filtered_posts.append(post)
    elif profile_config['no_files'] and not has_media:
        filtered_posts.append(post)

# Save filtered post information to a text file
save_posts_to_file(filtered_posts)

# Iterate over all the links in the filtered posts and download the content
for post in filtered_posts:
    baixar_conteudo(post['link'], config)

print(f"Information from {len(filtered_posts)} posts saved and content downloaded successfully!")
