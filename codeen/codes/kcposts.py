import os
import sys
import json
import requests
import re
from html.parser import HTMLParser
from urllib.parse import quote, urlparse, unquote

def load_config(config_path='config/conf.json'):
    """
    Carrega as configurações do arquivo conf.json
    Se o arquivo não existir, retorna configurações padrão
    """
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        return {
            'post_info': config.get('post_info', 'md'),  # Padrão para md se não especificado
            'save_info': config.get('save_info', True)   # Padrão para True se não especificado
        }
    except FileNotFoundError:
        # Configurações padrão se o arquivo não existir
        return {
            'post_info': 'md',
            'save_info': True
        }
    except json.JSONDecodeError:
        print(f"Error decoding {config_path}. Using default settings.")
        return {
            'post_info': 'md',
            'save_info': True
        }

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_profiles(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            return json.load(file)
    return {}

def save_profiles(path, profiles):
    with open(path, 'w') as file:
        json.dump(profiles, file, indent=4)

def extract_data_from_link(link):
    """
    Extract service, user_id, and post_id from both kemono.su and coomer.su links
    """
    # Pattern for both kemono.su and coomer.su
    match = re.match(r"https://(kemono|coomer)\.su/([^/]+)/user/([^/]+)/post/([^/]+)", link)
    if not match:
        raise ValueError("Invalid link format")
    
    # Unpack the match groups
    domain, service, user_id, post_id = match.groups()
    
    return domain, service, user_id, post_id

def get_api_base_url(domain):
    """
    Dynamically generate API base URL based on the domain
    """
    return f"https://{domain}.su/api/v1/"

def fetch_profile(domain, service, user_id):
    """
    Fetch user profile with dynamic domain support
    """
    api_base_url = get_api_base_url(domain)
    url = f"{api_base_url}{service}/user/{user_id}/profile"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_post(domain, service, user_id, post_id):
    """
    Fetch post data with dynamic domain support
    """
    api_base_url = get_api_base_url(domain)
    url = f"{api_base_url}{service}/user/{user_id}/post/{post_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

class HTMLToMarkdown(HTMLParser):
    """Parser to convert HTML content to Markdown and plain text."""
    def __init__(self):
        super().__init__()
        self.result = []
        self.raw_content = []
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            self.current_link = href
            self.result.append("[")  # Markdown link opening
        elif tag in ("p", "br"):
            self.result.append("\n")  # New line for Markdown
        self.raw_content.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link:
            self.result.append(f"]({self.current_link})")
            self.current_link = None
        self.raw_content.append(f"</{tag}>")

    def handle_data(self, data):
        # Append visible text to the Markdown result
        if self.current_link:
            self.result.append(data.strip())
        else:
            self.result.append(data.strip())
        # Append all raw content for reference
        self.raw_content.append(data)

    def get_markdown(self):
        """Return the cleaned Markdown content."""
        return "".join(self.result).strip()

    def get_raw_content(self):
        """Return the raw HTML content."""
        return "".join(self.raw_content).strip()

def clean_html_to_text(html):
    """Converts HTML to Markdown and extracts raw HTML."""
    parser = HTMLToMarkdown()
    parser.feed(html)
    return parser.get_markdown(), parser.get_raw_content()

def adapt_file_name(name):
    """
    Sanitize file name by removing special characters and reducing its size.
    """
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', unquote(name).split('.')[0])
    return sanitized[:50]  # Limit length to 50 characters


def download_files(file_list, folder_path):
    """
    Download files from a list of URLs and save them with unique names in the folder_path.

    :param file_list: List of tuples with original name and URL [(name, url), ...]
    :param folder_path: Directory to save downloaded files
    """
    seen_files = set()

    for idx, (original_name, url) in enumerate(file_list, start=1):
        # Check if URL is from allowed domains
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.split('.')[-2] + '.' + parsed_url.netloc.split('.')[-1]  # Get main domain
        if domain not in ['kemono.su', 'coomer.su']:
            print(f"⚠️ Ignoring not allowed domain URL: {url}")
            continue

        # Derive file extension
        extension = os.path.splitext(parsed_url.path)[1] or '.bin'

        # Handle case where no original name is provided
        if not original_name or original_name.strip() == "":
            sanitized_name = str(idx)
        else:
            sanitized_name = adapt_file_name(original_name)

        # Generate unique file name
        file_name = f"{idx}-{sanitized_name}{extension}"
        if file_name in seen_files:
            continue  # Skip duplicates

        seen_files.add(file_name)
        file_path = os.path.join(folder_path, file_name)

        # Download the file
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded: {file_name}")
        except Exception as e:
            print(f"Download failed {url}: {e}")


def save_post_content(post_data, folder_path, config):
    """
    Save post content and download files based on configuration settings.
    
    :param post_data: Dictionary containing post information
    :param folder_path: Path to save the post files
    :param config: Configuration dictionary with 'post_info' and 'save_info' keys
    """
    ensure_directory(folder_path)

    # Verify if content should be saved based on save_info
    if not config['save_info']:
        return  # Do not save anything if save_info is False

    # Use post_info configuration to define format
    file_format = config['post_info'].lower()
    file_extension = ".md" if file_format == "md" else ".txt"
    file_name = f"files{file_extension}"

    # Process title and content
    title, raw_title = clean_html_to_text(post_data['post']['title'])
    content, raw_content = clean_html_to_text(post_data['post']['content'])

    # Path to save the main file
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        # Formatted title
        if file_format == "md":
            file.write(f"# {title}\n\n")
        else:
            file.write(f"Title: {title}\n\n")
        
        # Formatted content
        file.write(f"{content}\n\n")

        # Process embed
        embed = post_data['post'].get('embed')
        if embed:
            if file_format == "md":
                file.write("## Embedded Content\n")
            else:
                file.write("Embedded Content:\n")
            file.write(f"- URL: {embed.get('url', 'N/A')}\n")
            file.write(f"- Subject: {embed.get('subject', 'N/A')}\n")
            file.write(f"- Description: {embed.get('description', 'N/A')}\n")

        # Separator
        file.write("\n---\n\n")

        # Raw Title and Content
        if file_format == "md":
            file.write("## Raw Title and Content\n\n")
        else:
            file.write("Raw Title and Content:\n\n")
        file.write(f"Raw Title: {raw_title}\n\n")
        file.write(f"Raw Content:\n{raw_content}\n\n")

        # Process attachments
        attachments = post_data.get('attachments', [])
        if attachments:
            if file_format == "md":
                file.write("## Attachments\n\n")
            else:
                file.write("Attachments:\n\n")
            for attach in attachments:
                server_url = f"{attach['server']}/data{attach['path']}?f={adapt_file_name(attach['name'])}"
                file.write(f"- {attach['name']}: {server_url}\n")

        # Process videos
        videos = post_data.get('videos', [])
        if videos:
            if file_format == "md":
                file.write("## Videos\n\n")
            else:
                file.write("Videos:\n\n")
            for video in videos:
                server_url = f"{video['server']}/data{video['path']}?f={adapt_file_name(video['name'])}"
                file.write(f"- {video['name']}: {server_url}\n")

        # Process images
        seen_paths = set()
        images = []
        for preview in post_data.get("previews", []):
            if 'name' in preview and 'server' in preview and 'path' in preview:
                server_url = f"{preview['server']}/data{preview['path']}"
                images.append((preview.get('name', ''), server_url))

        if images:
            if file_format == "md":
                file.write("## Images\n\n")
            else:
                file.write("Images:\n\n")
            for idx, (name, image_url) in enumerate(images, 1):
                if file_format == "md":
                    file.write(f"![Image {idx}]({image_url}) - {name}\n")
                else:
                    file.write(f"Image {idx}: {image_url} (Name: {name})\n")

    # Consolidate all files for download
    all_files_to_download = []

    for attach in post_data.get('attachments', []):
        if 'name' in attach and 'server' in attach and 'path' in attach:
            url = f"{attach['server']}/data{attach['path']}?f={adapt_file_name(attach['name'])}"
            all_files_to_download.append((attach['name'], url))

    for video in post_data.get('videos', []):
        if 'name' in video and 'server' in video and 'path' in video:
            url = f"{video['server']}/data{video['path']}?f={adapt_file_name(video['name'])}"
            all_files_to_download.append((video['name'], url))

    for image in post_data.get('previews', []):
        if 'name' in image and 'server' in image and 'path' in image:
            url = f"{image['server']}/data{image['path']}"
            all_files_to_download.append((image.get('name', ''), url))

    # Remove duplicates based on URL
    unique_files_to_download = list({url: (name, url) for name, url in all_files_to_download}.values())

    # Download files to the specified folder
    download_files(unique_files_to_download, folder_path)
    
def main():
    # Carregar configurações
    config = load_config()

    # Verificar se links foram passados por linha de comando
    if len(sys.argv) < 2:
        print("Please provide at least one link as an argument.")
        print("Example: python kcposts.py https://kemono.su/link1, https://coomer.su/link2")
        sys.exit(1)

    # Processar cada link passado
    links = sys.argv[1:]
    
    for user_link in links:
        try:
            print(f"\n--- Processing link: {user_link} ---")
            
            # Extract data from the link
            domain, service, user_id, post_id = extract_data_from_link(user_link)

            # Setup paths
            base_path = domain  # Use domain as base path (kemono or coomer)
            profiles_path = os.path.join(base_path, "profiles.json")

            ensure_directory(base_path)

            # Load existing profiles
            profiles = load_profiles(profiles_path)

            # Fetch and save profile if not already in profiles.json
            if user_id not in profiles:
                profile_data = fetch_profile(domain, service, user_id)
                profiles[user_id] = profile_data
                save_profiles(profiles_path, profiles)
            else:
                profile_data = profiles[user_id]

            # Create user-specific folder
            user_name = profile_data.get("name", "unknown_user")
            user_folder = os.path.join(base_path, f"{user_name}-{service}-{user_id}")
            ensure_directory(user_folder)

            # Create posts folder and post-specific folder
            posts_folder = os.path.join(user_folder, "posts")
            ensure_directory(posts_folder)

            post_folder = os.path.join(posts_folder, post_id)
            ensure_directory(post_folder)

            # Fetch post data
            post_data = fetch_post(domain, service, user_id, post_id)
            
            # Salvar conteúdo do post usando as configurações
            save_post_content(post_data, post_folder, config)

            print(f"\n✅ Link processed successfully: {user_link}")

        except Exception as e:
            print(f"❌ Error processing link {user_link}: {e}")
            import traceback
            traceback.print_exc()
            continue  # Continua processando próximos links mesmo se um falhar

if __name__ == "__main__":
    main()