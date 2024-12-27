import os
import json
import re
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import sys


def load_config(file_path):
    """Carregar a configuração de um arquivo JSON."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}  # Retorna um dicionário vazio se o arquivo não existir


def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters and replacing spaces with underscores."""
    filename = re.sub(r'[\\/*?\"<>|]', '', filename)
    return filename.replace(' ', '_')


def download_file(file_url, save_path):
    """Download a file from a URL and save it to the specified path with a progress bar and retry logic."""
    max_retries = 5
    retry_delay = 5  # seconds
    attempt = 0

    while attempt < max_retries:
        try:
            print(f"Attempt {attempt + 1} to download {file_url}", flush=True)
            response = requests.get(file_url, stream=True)
            response.raise_for_status()

            # Get the total file size from headers
            total_size = int(response.headers.get('content-length', 0))

            # Set up the tqdm progress bar
            with open(save_path, 'wb') as f:
                with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc="Downloading",
                        leave=False  # Keep the progress bar on the same line
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            print(f"\nDownload {file_url} success", flush=True)
            return  # Exit the function if download is successful

        except Exception as e:
            attempt += 1
            print(f"Warning: Attempt {attempt} failed to download {file_url}: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Download failed after {max_retries} attempts.")


def process_post(post, base_folder):
    """Process a single post, downloading its files."""
    post_id = post.get("id")
    post_folder = os.path.join(base_folder, post_id)
    os.makedirs(post_folder, exist_ok=True)

    print(f"Processing post ID {post_id}")

    # Prepare downloads for this post
    downloads = []
    for file_index, file in enumerate(post.get("files", []), start=1):
        original_name = file.get("name")
        file_url = file.get("url")
        sanitized_name = sanitize_filename(original_name)
        new_filename = f"{file_index}-{sanitized_name}"
        file_save_path = os.path.join(post_folder, new_filename)
        downloads.append((file_url, file_save_path))

    # Download files using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        for file_url, file_save_path in downloads:
            executor.submit(download_file, file_url, file_save_path)

    print(f"Post {post_id} downloaded")


def main():
    if len(sys.argv) < 2:
        print("Usage: python down.py {json_path}")
        sys.exit(1)

    # Pega o caminho do arquivo JSON a partir do argumento da linha de comando
    json_file_path = sys.argv[1]

    # Verifica se o arquivo existe
    if not os.path.exists(json_file_path):
        print(f"Error: The file '{json_file_path}' was not found.")
        sys.exit(1)

    # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Base folder for posts
    base_folder = os.path.join(os.path.dirname(json_file_path), "posts")
    os.makedirs(base_folder, exist_ok=True)

    # Caminho para o arquivo de configuração
    config_file_path = os.path.join("config", "conf.json")

    # Carregar a configuração do arquivo JSON
    config = load_config(config_file_path)

    # Pegar o valor de 'process_from_oldest' da configuração
    process_from_oldest = config.get("process_from_oldest", True)  # Valor padrão é True

    posts = data.get("posts", [])
    if process_from_oldest:
        posts = reversed(posts)

    # Process each post sequentially
    for post_index, post in enumerate(posts, start=1):
        process_post(post, base_folder)
        time.sleep(2)  # Wait 2 seconds between posts


if __name__ == "__main__":
    main()
