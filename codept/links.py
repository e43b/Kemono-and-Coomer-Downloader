import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse
import argparse
import os

# Função para obter o número total de posts
def get_total_posts(profile_url):
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    paginator_info = soup.find('div', {'class': 'paginator'})
    if paginator_info and paginator_info.find('small'):
        total_posts_text = paginator_info.find('small').text
        total_posts = int(re.search(r'of (\d+)', total_posts_text).group(1))
    else:
        # Contar posts diretamente se o paginator não estiver presente
        total_posts = len(soup.find_all('article', {'class': 'post-card'}))

    return total_posts

# Função para obter links dos posts de uma página específica
def get_posts_links(profile_url, page_number):
    offset = page_number * 50
    page_url = f"{profile_url}?o={offset}"
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    domain = re.search(r'https?://[^/]+', profile_url).group(0)

    posts = []
    for article in soup.find_all('article', {'class': 'post-card'}):
        post_link = article.find('a')['href']
        posts.append(f"{domain}{post_link}")

    return posts

# Função para obter nome do autor, domínio do site e plataforma
def get_author_platform_info(profile_url):
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Obter nome do autor
    author_tag = soup.find("a", class_="post__user-name")
    if author_tag:
        author_name = author_tag.text.strip()
    else:
        author_meta_tag = soup.find("meta", property="og:image")
        author_content = author_meta_tag["content"]
        author_name = author_content.split("/")[-1].split("-")[0]

    # Obter domínio do site e nome da plataforma
    parsed_url = urlparse(profile_url)
    domain_name = parsed_url.netloc.replace('.', '_')
    platform_name = parsed_url.path.split("/")[1]

    return author_name, domain_name, platform_name

# Função para processar os argumentos de linha de comando e determinar as páginas a serem extraídas
def process_pages(total_pages, pages_arg):
    if pages_arg == 'all':
        return list(range(1, total_pages + 1))

    include_pages = set()
    exclude_pages = set()

    for part in pages_arg.split(','):
        part = part.strip()
        if 'to' in part:
            start, end = map(int, part.replace('-', '').split('to'))
            pages = set(range(start, end + 1))
            if part.startswith('-'):
                exclude_pages.update(pages)
            else:
                include_pages.update(pages)
        else:
            page = int(part.replace('-', ''))
            if part.startswith('-'):
                exclude_pages.add(page)
            else:
                include_pages.add(page)

    if include_pages:
        return sorted(include_pages - exclude_pages)
    else:
        return sorted(set(range(1, total_pages + 1)) - exclude_pages)

# Função principal
def scrape_fansly(profile_url, pages_arg):
    total_posts = get_total_posts(profile_url)
    total_pages = (total_posts + 49) // 50  # Para cobrir todos os posts, arredondar para cima
    pages_to_scrape = process_pages(total_pages, pages_arg)
    data = {'profile_url': profile_url, 'pages': [], 'command': f'{profile_url} {pages_arg}'}

    for page in pages_to_scrape:
        posts = get_posts_links(profile_url, page - 1)  # Ajuste para índice de página
        data['pages'].append({
            'page_number': page,
            'posts': posts
        })

    author_name, domain_name, platform_name = get_author_platform_info(profile_url)

    # Criar o nome do arquivo JSON dinamicamente
    json_filename = f"links/{domain_name}_{author_name}_{platform_name}.json"

    # Criar pasta 'links' se não existir
    if not os.path.exists('links'):
        os.makedirs('links')

    # Salvar dados em um arquivo JSON
    with open(json_filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Scraping complete. Data saved to {json_filename}")

# Função para processar os argumentos da linha de comando
def main():
    parser = argparse.ArgumentParser(description='Scrape posts links from a profile.')
    parser.add_argument('profile_url', type=str, help='URL of the profile to scrape')
    parser.add_argument('pages', type=str, nargs='?', default='all', help='Pages to scrape, e.g., "all", "1 to 5", "-8 to -10, -25"')
    args = parser.parse_args()
    scrape_fansly(args.profile_url, args.pages)

if __name__ == "__main__":
    main()
