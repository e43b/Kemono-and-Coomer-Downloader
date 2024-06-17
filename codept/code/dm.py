import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Função para determinar a pasta base (Kemono ou Coomer)
def determinar_pasta_base(url):
    parsed_url = urlparse(url)
    if "kemono.su" in parsed_url.netloc or "kemono.party" in parsed_url.netloc:
        return "Kemono"
    elif "coomer.su" in parsed_url.netloc or "coomer.party" in parsed_url.netloc:
        return "Coomer"
    else:
        return "Outros"

# Função para encontrar o nome do autor e a plataforma
def obter_autor_e_plataforma(soup):
    # Encontrar o nome do autor
    author_meta_tag = soup.find("meta", attrs={"name": "artist_name"})
    if author_meta_tag:
        author_name = author_meta_tag["content"].strip()
    else:
        # Se não encontrar, utilize a lógica anterior
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

# Função para corrigir o link
def corrigir_link(link):
    if not link.endswith("dms"):
        link += "/dms"
    return link

# Função para extrair o conteúdo dos artigos e criar arquivos de texto
def extrair_conteudo(link, base_folder, author_folder):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("article", class_="dm-card")

    dm_folder = os.path.join(base_folder, author_folder, "DMs")
    os.makedirs(dm_folder, exist_ok=True)  # Criar pasta se não existir

    for i, article in enumerate(articles, start=1):
        content = article.find("div", class_="dm-card__content").text.strip()
        published_date = article.find("div", class_="dm-card__added").text.strip()

        # Formatar o título do arquivo sem espaços extras
        file_title = f"{i}_{published_date.replace(':', '-')}".replace(" ", "")

        file_path = os.path.join(dm_folder, f"{file_title}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
            file.write(f"\n\nPublished: {published_date}")

# Solicitar URL(s) ao usuário
link = input('Digite o Link do Perfil que deseja baixar as DMs: ')
link = corrigir_link(link)

# Fazer a requisição HTTP e obter o conteúdo HTML
response = requests.get(link)
html_content = response.text

# Parsing do HTML usando BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Determinar a pasta base (Kemono ou Coomer)
base_folder = determinar_pasta_base(link)

# Encontrar o nome do autor e a plataforma
author_name, platform_name = obter_autor_e_plataforma(soup)

# Criar o nome da pasta do autor com a plataforma
author_folder = f"{author_name}-{platform_name}"

# Extrair conteúdo e criar arquivos de texto
extrair_conteudo(link, base_folder, author_folder)
