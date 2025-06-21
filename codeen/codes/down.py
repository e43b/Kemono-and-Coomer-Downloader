import os
import json
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor
import sys


def download_chunk(url, start, end, chunk_index):
    print(f"Starting download of chunk {chunk_index}...")
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)
    with open(f'temp_chunk_{chunk_index}', 'wb') as chunk_file:
        chunk_file.write(response.content)

def merge_chunks(output_file, num_chunks):
    with open(output_file, 'wb') as final_file:
        for i in range(num_chunks):
            with open(f'temp_chunk_{i}', 'rb') as chunk_file:
                final_file.write(chunk_file.read())


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

# def download_file(file_url, save_path):
#     """Download a file from a URL and save it to the specified path."""
#     try:
#         response = requests.get(file_url, stream=True)
#         response.raise_for_status()
#         with open(save_path, 'wb') as f:
#             for chunk in response.iter_content(chunk_size=8192):
#                 if chunk:
#                     f.write(chunk)
#     except Exception as e:
#         print(f"Download failed {file_url}: {e}")

def download_file(url, output_file, num_connections=20):
    # Check if the file already exists
    if os.path.exists(output_file):
        print(f"File '{output_file}' already exists. Skipping download.")
        return
    print(f"Downloading {url} to {output_file} using {num_connections} connections...")
    response = requests.head(url)
    file_size = int(response.headers.get('Content-Length', 0))
    chunk_size = file_size // num_connections

    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        futures = []
        for i in range(num_connections):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < num_connections - 1 else file_size - 1
            futures.append(executor.submit(download_chunk, url, start, end, i))

        for future in futures:
            future.result()  # Wait for all threads to complete

    merge_chunks(output_file, num_connections)


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
