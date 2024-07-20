import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

# Load configurations from JSON file
with open("code/config.json", "r") as f:
    config = json.load(f)

download_attachments = config["download_attachments"]
download_videos = config["download_videos"]
save_info_txt = config["save_info_txt"]
save_comments_txt = config["save_comments_txt"]

# Request URL(s) or JSON file path from the user
input_choice = input("Enter 1 to input URLs directly or 2 to provide a JSON file path: ")

if input_choice == "1":
    urls_input = input("Please enter the post URL or URLs separated by commas: ")
    urls = [url.strip() for url in urls_input.split(",")]
elif input_choice == "2":
    json_path = input("Please enter the JSON file path: ")
    with open(json_path, "r") as f:
        data = json.load(f)
        urls = []
        for page in data.get("pages", []):
            urls.extend(page.get("posts", []))
else:
    print("Invalid choice. Exiting.")
    exit()

# Function to download content from a URL
def baixar_conteudo(url):
    # Making the HTTP request and getting the HTML content
    response = requests.get(url)
    html_content = response.text

    # Parsing the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Determining the base folder (Kemono or Coomer)
    parsed_url = urlparse(url)
    if "kemono.su" in parsed_url.netloc or "kemono.party" in parsed_url.netloc:
        base_folder = "Kemono"
    elif "coomer.su" in parsed_url.netloc or "coomer.party" in parsed_url.netloc:
        base_folder = "Coomer"
    else:
        base_folder = "Others"

    # Finding the author name
    author_tag = soup.find("a", class_="post__user-name")
    if author_tag:
        author_name = author_tag.text.strip()
    else:
        author_meta_tag = soup.find("meta", property="og:image")
        author_content = author_meta_tag["content"]
        author_name = author_content.split("/")[-1].split("-")[0]

    # Getting the platform
    platform_meta_tag = soup.find("meta", property="og:image")
    platform_content = platform_meta_tag["content"]
    platform_name = urlparse(platform_content).path.split("/")[2]

    # Creating the author's folder name with the platform
    author_folder = f"{author_name}-{platform_name}"

    # Getting the post ID
    post_id_meta_tag = soup.find("meta", attrs={"name": "id"})
    post_id = post_id_meta_tag["content"]

    # Creating the post folder name
    post_folder = post_id

    # Full path of the post folder
    post_path = os.path.join(base_folder, author_folder, "posts", post_folder)

    # Creating the folders if they don't exist
    os.makedirs(post_path, exist_ok=True)

    # Function to save post information in a text file
    def salvar_info_post(soup, folder):
        info_file_path = os.path.join(folder, "info.txt")
        with open(info_file_path, "w", encoding="utf-8") as f:
            # Title
            title_tag = soup.find("h1", class_="post__title")
            if title_tag:
                title = " ".join([span.text for span in title_tag.find_all("span")])
                f.write(f"Title: {title}\n\n")

            # Publication date
            published_tag = soup.find("div", class_="post__published")
            if published_tag:
                published_date = published_tag.text.strip().split(": ")[1]
                f.write(f"Publication date: {published_date}\n\n")

            # Import date
            imported_tag = soup.find("div", class_="post__added")
            if imported_tag and ": " in imported_tag.text:
                imported_date = imported_tag.text.strip().split(": ")[1]
                f.write(f"Import date: {imported_date}\n\n")

            # Post content
            content_section = soup.find("div", class_="post__content")
            if content_section:
                content = content_section.get_text(strip=True)
                f.write(f"Content:\n{content}\n\n")

            # Tags
            tags_section = soup.find("section", id="post-tags")
            if tags_section:
                tags = [a.text for a in tags_section.find_all("a")]
                f.write(f"Tags: {', '.join(tags)}\n\n")

            # Attachments
            attachment_tags = soup.find_all("a", class_="post__attachment-link")
            if attachment_tags:
                f.write("Attachments:\n")
                for attachment_tag in attachment_tags:
                    attachment_url = attachment_tag["href"]
                    attachment_name = attachment_tag.text.strip().split(" ")[-1]
                    f.write(f"- {attachment_name}: {attachment_url}\n")
                    # Check if there is a "browse" link
                    browse_tag = attachment_tag.find_next("a", href=True, string="browse »")
                    if browse_tag:
                        browse_url = urlparse(url)._replace(path=browse_tag["href"]).geturl()
                        f.write(f"  Attachment content: {browse_url}\n")
                        browse_response = requests.get(browse_url)
                        browse_soup = BeautifulSoup(browse_response.text, "html.parser")

            f.write("\n")  # Adds a line break after attachments

            # Comments
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

    # Save post information if the user wants to
    if save_info_txt:
        salvar_info_post(soup, post_path)

    # Set to store already downloaded links
    links_baixados = set()

    # Finding image tags
    image_tags = soup.find_all("a", class_="fileThumb")

    # Iterating over image tags
    for index, img_tag in enumerate(image_tags):
        # Getting the image URL
        image_url = img_tag["href"]
        # Checking if the image has already been downloaded
        if image_url not in links_baixados:
            # Downloading the image
            image_response = requests.get(image_url)
            # Getting the file name
            filename = f"image_{index + 1}.jpg"
            # Saving the image in the post folder
            with open(os.path.join(post_path, filename), "wb") as f:
                f.write(image_response.content)
            # Adding the URL to the set of downloaded links
            links_baixados.add(image_url)

    # Checking if the user wants to download post attachments
    if download_attachments:
        # Finding attachment tags
        attachment_tags = soup.find_all("a", class_="post__attachment-link")
        # Iterating over attachment tags
        for index, attachment_tag in enumerate(attachment_tags):
            # Getting the attachment URL
            attachment_url = attachment_tag["href"]
            # Checking if the attachment has already been downloaded
            if attachment_url not in links_baixados:
                # Downloading the attachment
                attachment_response = requests.get(attachment_url)
                # Getting the file name
                filename = attachment_tag["download"]
                # Saving the attachment in the post folder
                with open(os.path.join(post_path, filename), "wb") as f:
                    f.write(attachment_response.content)
                # Adding the URL to the set of downloaded links
                links_baixados.add(attachment_url)

    # Checking if the user wants to download videos
    if download_videos:
        # Finding video tags
        video_tags = soup.find_all("a", class_="post__attachment-link")
        # Iterating over video tags
        for index, video_tag in enumerate(video_tags):
            # Getting the video URL
            video_url = video_tag["href"]
            # Checking if the video has already been downloaded
            if video_url not in links_baixados:
                # Downloading the video
                video_response = requests.get(video_url)
                # Getting the file name
                filename = video_tag["download"]
                # Saving the video in the post folder
                with open(os.path.join(post_path, filename), "wb") as f:
                    f.write(video_response.content)
                # Adding the URL to the set of downloaded links
                links_baixados.add(video_url)

    print(f"Content from post {url} downloaded successfully!")

# Iterate over all provided URLs and download the content
for url in urls:
    baixar_conteudo(url)
