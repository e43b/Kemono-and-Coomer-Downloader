import os
import re
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote, parse_qs
import json
import time
import random

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=10,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

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

def get_total_posts(soup):
    total_posts_text = soup.find('small')
    if total_posts_text:
        total_posts = int(total_posts_text.text.strip().split(' of ')[1])
    else:
        total_posts = None
    return total_posts

def sanitize_filename(filename, max_length=130):
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    base, ext = os.path.splitext(filename)
    if len(base) + len(ext) > max_length:
        base = base[:max_length - len(ext)]
    return base + ext

def ensure_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename

def get_filename_from_url(url):
    parsed_url = urlparse(url)
    base_filename, base_ext = os.path.splitext(os.path.basename(parsed_url.path))
    query_params = parse_qs(parsed_url.query)
    alternative_filename = query_params.get('f', [None])[0]
    if alternative_filename:
        alternative_filename = unquote(alternative_filename).split('?')[0]
        filename, ext = os.path.splitext(os.path.basename(alternative_filename))
        if not ext:
            ext = base_ext
        elif ext.lower() != base_ext.lower():
            ext = base_ext
        filename = sanitize_filename(filename)
    else:
        ext = base_ext
        filename = sanitize_filename(base_filename)

    return f"{filename}{ext}"

def truncate_path_if_long(path, max_length=130):
    directory, filename_with_ext = os.path.split(path)
    filename, ext = os.path.splitext(filename_with_ext)
    max_filename_length = max_length - len(ext)
    if len(filename) > max_filename_length:
        filename = filename[:max_filename_length]
    truncated_path = os.path.join(directory, filename + ext)
    return truncated_path

def save_posts_to_file(posts, filename="posts_info.txt"):
    with open(filename, 'w', encoding='utf-8') as f:
        for post in posts:
            f.write(f"Link: {post['link']}\n")
            f.write(f"Title: {post['title']}\n")
            f.write(f"Number of attachments: {post['attachments']}\n")
            f.write(f"Post date: {post['date']}\n")
            f.write(f"Cover image: {post['image']}\n")
            f.write("\n" + "-"*40 + "\n\n")

# Helper function to download an image and return the local filename
def download_image(url, save_dir, post_id, config):
    img_name = os.path.basename(url)
    if not config.get("no_folders", False):
        img_name = f"{post_id}_{img_name}"
    local_path = os.path.join(save_dir, img_name)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as file:
            file.write(response.content)
        return img_name
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def clean_url(url):
    cleaned_url = url.replace(r'\\', r'').replace(r'\.', '.')
    return cleaned_url

def update_image_sources(content, image_mapping, base_url):
    for src, local_filename in image_mapping.items():
        src_cleaned = clean_url(src)
        content = content.replace(src_cleaned, local_filename)
    return content

def save_post_info(soup, post_path, post_id, config, base_url):
    title_tag = soup.find("h1", class_="post__title")
    title = title_tag.text.strip() if title_tag else "Untitled Post"
    published_tag = soup.find("div", class_="post__published")
    published_date = published_tag.text.strip().split(":", 1)[-1].strip() if published_tag else "Unknown Date"
    imported_tag = soup.find("div", class_="post__added")
    imported_date = imported_tag.text.strip().split(":", 1)[-1].strip() if imported_tag else "Unknown Date"
    tags_section = soup.find("section", id="post-tags")
    tags = [tag.text.strip() for tag in tags_section.find_all("a")] if tags_section else []
    content_section = soup.find("div", class_="post__content")
    image_mapping = {}

    if content_section:
        content_html = str(content_section)
        image_tags = content_section.find_all("img")
        image_urls = [img['src'] for img in image_tags]

        # Image downloading and mapping
        image_dir = post_path
        os.makedirs(image_dir, exist_ok=True)
        for image_url in image_urls:
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif not image_url.startswith(('http://', 'https://')):
                absolute_url = urljoin(base_url, image_url)
                local_filename = os.path.basename(absolute_url)
                if not local_filename.startswith(post_id + "_"):
                    local_filename = post_id + "_" + local_filename
                local_filename = download_image(absolute_url, image_dir, post_id, config)
                if local_filename:
                    image_mapping[image_url] = local_filename
                    image_mapping[absolute_url] = local_filename
            else:
                # Handle absolute URLs directly
                local_filename = os.path.basename(image_url)
                if not local_filename.startswith(post_id + "_"):
                    local_filename = post_id + "_" + local_filename
                local_filename = download_image(image_url, image_dir, post_id, config)
                if local_filename:
                    image_mapping[image_url] = local_filename
                    image_mapping[urljoin(base_url, image_url)] = local_filename

        content_html = update_image_sources(content_html, image_mapping, base_url)
    else:
        content_html = "<p>No content available</p>"

    attachments = soup.find_all("a", class_="post__attachment-link")
    attachment_links = [attachment["href"] for attachment in attachments] if attachments else []
    thumbnail_tags = soup.find_all("div", class_="post__thumbnail")
    
    # Handle thumbnails and their filenames
    thumbnail_srcs = []
    for tag in thumbnail_tags:
        img_tag = tag.find("img")
        if img_tag:
            src = img_tag["src"]
            if src.startswith('//'):
                src = 'https:' + src
            absolute_src = urljoin(base_url, src)
            fileThumb_url = tag.find("a", class_="fileThumb")["href"]
            fileThumb_filename = get_filename_from_url(fileThumb_url)
            fileThumb_filename = sanitize_filename(fileThumb_filename)
            if config.get("no_folders", False):
                local_filename = f"{fileThumb_filename}"
            else:
                local_filename = f"{post_id}_{fileThumb_filename}"
            thumbnail_srcs.append(local_filename)
            # Map the thumbnail source to the local filename
            image_mapping[absolute_src] = local_filename
    
    # Extract embed-view content and parent link
    embed_view = soup.find("div", class_="embed-view")
    if embed_view:
        embed_view_content = str(embed_view)
        embed_view_parent = embed_view.find_parent("a")
        embed_view_link = embed_view_parent["href"] if embed_view_parent else "No Link Available"
        embed_view_section = (
            '<div class="post__embed">\n'
            '    <a href="{}" target="_blank" class"embed-view">\n'
            '    {}\n'
            '    </a>\n'
            '</div>\n'
        ).format(embed_view_link, embed_view_content)
    else:
        embed_view_section = ""

    # Generate the HTML content with correct filenames
    comments = soup.find_all("article", class_="comment")
    comment_sections = []
    for comment in comments:
        commenter = comment.find("a", class_="comment__name").text.strip() if comment.find("a", class_="comment__name") else "Anonymous"
        message = comment.find("p", class_="comment__message").text.strip() if comment.find("p", class_="comment__message") else "No message"
        timestamp = comment.find("time", class_="timestamp").text.strip() if comment.find("time", class_="timestamp") else "Unknown Date"
        comment_sections.append(
            '<article class="comment">\n'
            '    <header class="comment__header">\n'
            '        <a class="fancy-link fancy-link--local comment__name">{}</a>\n'
            '    </header>\n'
            '    <section class="comment__body">\n'
            '        <p class="comment__message">{}</p>\n'
            '    </section>\n'
            '    <footer class="comment__footer">\n'
            '        <time class="timestamp" datetime="{}">{}</time>\n'
            '    </footer>\n'
            '</article>\n'.format(commenter, message, timestamp, timestamp)
        )

    # List all HTML files in the current directory
    all_html_files = sorted(
        [f for f in os.listdir(post_path) if f.endswith('.html')],
        key=lambda x: re.sub(r'\D', '', x)
    )

    # Determine the current file's position in the list
    current_filename = f"{post_id}_{sanitize_filename(title)}.html".replace('/', '_').replace('\\', '_')
    current_index = all_html_files.index(current_filename) if current_filename in all_html_files else -1

    # Determine previous and next file names
    prev_file = all_html_files[current_index + 1] if current_index < len(all_html_files) - 1 else ''
    if config.get("no_folders", False):
        prev_link = f''
    else:
        prev_link = f'<li class="post__nav-item"><a class="post__nav-link prev" href="{prev_file}">‹ previous</a></li>' if prev_file else '<li class="post__nav-item subtitle">‹ previous</li>'

    html_content = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '    <title>{}</title>\n'
        '    <link rel="stylesheet" href="style.css">\n'
        '    <link rel="stylesheet" href="../style.css">\n'
        '    <link rel="stylesheet" href="../../style.css">\n'
        '    <link rel="stylesheet" href="../../../style.css">\n'
        '</head>\n'
        '<body>\n'
        '    <div class="content-wrapper shifted">\n'
        '        <main class="main">\n'
        '            <nav class="post__nav-links">\n'
        '                <ul class="post__nav-list">\n'
        '                    {}\n'
        '                </ul>\n'
        '            </nav>\n'
        '            <header class="post__header">\n'
        '                <div class="post__info">\n'
        '                    <h1 class="post__title">{}</h1>\n'
        '                    <div class="post__published" style="margin: 0.125rem 0;">\n'
        '                        <div style="width: 89px; display: inline-block;">Published:</div> {}\n'
        '                    </div>\n'
        '                    <div class="post__added" style="margin: 0.125rem 0;">\n'
        '                        <div style="width: 89px; display: inline-block;">Imported: </div> {}\n'
        '                    </div>\n'
        '                    <section id="post-tags">\n'
        '                        <span id="label">Tags: </span>\n'
        '                        <div>\n'
        '                            {}\n'
        '                        </div>\n'
        '                    </section>\n'
        '                </div>\n'
        '            </header>\n'
        '            <div class="post__body">\n'
        '                <div class="post__content">\n'
        '                    <h2>Content</h2>\n'
        '                    {}\n'
        '                </div>\n'
        '                {}'
        '                {}'
        '                {}\n'
        '            </div>\n'
        '            <footer class="post__footer">\n'
        '                <h2 class="site-section__subheading">Comments</h2>\n'
        '                <div class="post__comments">\n'
        '                    {}\n'
        '                </div>\n'
        '            </footer>\n'
        '        </main>\n'
        '    </div>\n'
        '</body>\n'
        '</html>'
    ).format(
        title,
        prev_link,
        title,
        published_date,
        imported_date,
        ''.join('<a>{}</a>'.format(tag) for tag in tags),
        content_html,
        '<ul class="post__attachments">\n'
        '    <h2>Downloads</h2>\n'
        '    {}'
        '</ul>\n'.format('\n'.join('<li><a href="{}">{}</a></li>'.format(link, link) for link in attachment_links)) if attachment_links else '',
        '<div class="post__thumbnails">\n'
        '    <h2>Files</h2>\n'
        '    {}'
        '</div>\n'.format('\n'.join('<div class="post__thumbnail"><img src="{}"></div>'.format(filename) for filename in thumbnail_srcs)) if thumbnail_srcs else '',
        embed_view_section,
        ''.join(comment_sections)
    )

    # Save the HTML content to a file
    sanitized_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
    if config.get("no_folders", False):
        filename = f"{sanitized_title}.html"
    else:
        filename = f"{post_id}_{sanitized_title}.html"
    filename = filename.replace('/', '_').replace('\\', '_')
    info_file_path = os.path.join(post_path, filename)
    with open(info_file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

user_agent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

user_agents = random.choice(user_agent)

def download_content(url, config):
    session = create_session()

    headers = {
        'User-Agent': user_agents,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    try:
        response = session.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        parsed_url = urlparse(url)
        base_folder = "Kemono" if "kemono.su" in parsed_url.netloc or "kemono.party" in parsed_url.netloc else "Coomer"
        author_tag = soup.find("a", class_="post__user-name")
        if author_tag:
            author_name = author_tag.text.strip()
        else:
            meta_tag = soup.find("meta", property="og:image")
            if meta_tag:
                author_name = meta_tag["content"].split("/")[-1].split("-")[0]
            else:
                author_name = "UnknownAuthor"
        platform_name = urlparse(soup.find("meta", property="og:image")["content"]).path.split("/")[2] if soup.find("meta", property="og:image") else "UnknownPlatform"
        post_id = soup.find("meta", attrs={"name": "id"})["content"]
        if config.get("no_folders", False):
            post_path = os.path.abspath(os.path.join(base_folder, f"{author_name}-{platform_name}", "posts", post_id))
        else:
            post_path = os.path.abspath(os.path.join(base_folder, f"{author_name}-{platform_name}", "posts"))
        if not os.path.exists(post_path):
            os.makedirs(post_path)
        if config.get("save_info_txt", False):
            save_post_info(soup, post_path, post_id, config, base_url)
        downloaded_links = set()
        image_tags = soup.find_all("a", class_="fileThumb")
        for img_tag in image_tags:
            image_url = img_tag["href"]
            filename = sanitize_filename(get_filename_from_url(image_url))
            filename_with_id = f"{post_id}_{filename}" if not config.get("no_folders", False) else filename
            file_path = os.path.join(post_path, filename_with_id)
            file_path = truncate_path_if_long(file_path)
            unique_filename = ensure_unique_filename(post_path, filename_with_id)
            file_path = os.path.join(post_path, unique_filename)
            if not os.path.exists(file_path):
                try:
                    image_response = session.get(image_url, timeout=60)
                    image_response.raise_for_status()
                    with open(file_path, "wb") as f:
                        f.write(image_response.content)
                    downloaded_links.add(image_url)
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download image {image_url}: {e}")
                except OSError as e:
                    print(f"OSError: {e} - File path: {file_path}")
        if config.get("download_attachments", False):
            attachment_tags = soup.find_all("a", class_="post__attachment-link")
            for attachment_tag in attachment_tags:
                attachment_url = attachment_tag["href"]
                filename = sanitize_filename(get_filename_from_url(attachment_url))
                filename_with_id = f"{post_id}_{filename}" if not config.get("no_folders", False) else filename
                file_path = os.path.join(post_path, filename_with_id)
                file_path = truncate_path_if_long(file_path)
                unique_filename = ensure_unique_filename(post_path, filename_with_id)
                file_path = os.path.join(post_path, unique_filename)
                if not os.path.exists(file_path):
                    try:
                        attachment_response = session.get(attachment_url, timeout=60)
                        attachment_response.raise_for_status()
                        with open(file_path, "wb") as f:
                            f.write(attachment_response.content)
                        downloaded_links.add(attachment_url)
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to download attachment {attachment_url}: {e}")
        if config.get("download_videos", False):
            video_tags = soup.find_all("a", class_="post__attachment-link")
            for video_tag in video_tags:
                video_url = video_tag["href"]
                filename = sanitize_filename(get_filename_from_url(video_url))
                filename_with_id = f"{post_id}_{filename}" if not config.get("no_folders", False) else filename
                file_path = os.path.join(post_path, filename_with_id)
                file_path = truncate_path_if_long(file_path)
                unique_filename = ensure_unique_filename(post_path, filename_with_id)
                file_path = os.path.join(post_path, unique_filename)
                if not os.path.exists(file_path):
                    try:
                        video_response = session.get(video_url, timeout=60)
                        video_response.raise_for_status()
                        with open(file_path, "wb") as f:
                            f.write(video_response.content)
                        downloaded_links.add(video_url)
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to download video {video_url}: {e}")
        print(f"Post content from {url} successfully downloaded!")
    except requests.exceptions.ChunkedEncodingError as e:
        print(f"ChunkedEncodingError occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"RequestException occurred: {e}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"General error occurred: {req_err}")

with open("code/profileconfig.json", "r") as f:
    config = json.load(f)

base_url = input("Please enter the Profile URL: ")

all_posts = []

session = create_session()
page_number = 0
while True:
    if page_number == 0:
        url = base_url
    else:
        url = f"{base_url}?o={page_number * 50}"

    headers = {
        'User-Agent': user_agents,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        response = session.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        if page_number == 0:
            total_posts = get_total_posts(soup)
            if total_posts:
                total_pages = (total_posts + 49) // 50
            else:
                total_pages = 1
        post_cards = soup.find_all('article', class_='post-card post-card--preview')
        if not post_cards:
            print(f"No more post cards found on page {page_number}. Ending pagination.")  # Debug print statement
            break
        for post_card in post_cards:
            post_info = extract_post_info(post_card, base_url)
            all_posts.append(post_info)
        if page_number >= total_pages - 1:
            break
        page_number += 1

        # Sleep for a few seconds after processing each page to avoid DDoS-Guard
        time.sleep(random.uniform(6, 18))

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page {page_number}: {e}")
        break

filtered_posts = []
for post in all_posts:
    has_media = post['image'] != "No image available" or post['attachments'] != "No attachments"
    if config.get('both'):
        filtered_posts.append(post)
    elif config.get('files_only') and has_media:
        filtered_posts.append(post)
    elif config.get('no_files') and not has_media:
        filtered_posts.append(post)

save_posts_to_file(filtered_posts)

for post in filtered_posts:
    download_content(post['link'], config)

print(f"Information from {len(filtered_posts)} posts saved and content downloaded successfully!")