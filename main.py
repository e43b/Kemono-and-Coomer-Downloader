import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# URL do HTML fornecido
url = "https://coomer.su/onlyfans/user/kerriepix/post/711168336"

# Variáveis para permitir que o usuário escolha o que baixar
baixar_anexos = True  # Define como False se não deseja baixar anexos
baixar_videos = True  # Define como False se não deseja baixar vídeos

# Fazendo a requisição HTTP e obtendo o conteúdo HTML
response = requests.get(url)
html_content = response.text

# Parsing do HTML usando BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Verificando se o link pertence a kemono.su ou kemono.party
if "kemono.su" in url or "kemono.party" in url:
    # Se sim, encontrar o nome do autor na tag <a> com a classe "post__user-name"
    author_tag = soup.find("a", class_="post__user-name")
    author_name = author_tag.text.strip()
else:
    # Caso contrário, extrair o nome do autor do link do meta tag
    author_meta_tag = soup.find("meta", property="og:image")
    author_content = author_meta_tag["content"]
    author_name = author_content.split("/")[-1].split("-")[0]

# Obtendo a plataforma
platform_meta_tag = soup.find("meta", property="og:image")
platform_content = platform_meta_tag["content"]
platform_name = urlparse(platform_content).path.split("/")[2]

# Criando o nome da pasta do autor com a plataforma
author_folder = f"{author_name}-{platform_name}"

# Encontrando o ID do post
post_id_meta_tag = soup.find("meta", attrs={"name": "id"})
post_id = post_id_meta_tag["content"]

# Criando o nome da pasta do post
post_folder = post_id

# Criando as pastas se não existirem
if not os.path.exists(author_folder):
    os.makedirs(author_folder)
if not os.path.exists(os.path.join(author_folder, post_folder)):
    os.makedirs(os.path.join(author_folder, post_folder))

# Conjunto para armazenar os links já baixados
links_baixados = set()

# Encontrando as tags de imagem
image_tags = soup.find_all("a", class_="fileThumb")

# Iterando sobre as tags de imagem
for index, img_tag in enumerate(image_tags):
    # Obtendo a URL da imagem
    image_url = img_tag["href"]
    # Verificando se a imagem já foi baixada
    if image_url not in links_baixados:
        # Fazendo o download da imagem
        image_response = requests.get(image_url)
        # Obtendo o nome do arquivo
        filename = f"image_{index + 1}.jpg"
        # Salvando a imagem na pasta do post
        with open(os.path.join(author_folder, post_folder, filename), "wb") as f:
            f.write(image_response.content)
        # Adicionando a URL ao conjunto de links baixados
        links_baixados.add(image_url)

# Verificando se o usuário deseja baixar anexos do post
if baixar_anexos:
    # Encontrando as tags de anexo
    attachment_tags = soup.find_all("a", class_="post__attachment-link")
    # Iterando sobre as tags de anexo
    for index, attachment_tag in enumerate(attachment_tags):
        # Obtendo a URL do anexo
        attachment_url = attachment_tag["href"]
        # Verificando se o anexo já foi baixado
        if attachment_url not in links_baixados:
            # Fazendo o download do anexo
            attachment_response = requests.get(attachment_url)
            # Obtendo o nome do arquivo
            filename = attachment_tag["download"]
            # Salvando o anexo na pasta do post
            with open(os.path.join(author_folder, post_folder, filename), "wb") as f:
                f.write(attachment_response.content)
            # Adicionando a URL ao conjunto de links baixados
            links_baixados.add(attachment_url)

# Verificando se o usuário deseja baixar vídeos
if baixar_videos:
    # Encontrando as tags de vídeo
    video_tags = soup.find_all("a", class_="post__attachment-link")
    # Iterando sobre as tags de vídeo
    for index, video_tag in enumerate(video_tags):
        # Obtendo a URL do vídeo
        video_url = video_tag["href"]
        # Verificando se o vídeo já foi baixado
        if video_url not in links_baixados:
            # Fazendo o download do vídeo
            video_response = requests.get(video_url)
            # Obtendo o nome do arquivo
            filename = video_tag["download"]
            # Salvando o vídeo na pasta do post
            with open(os.path.join(author_folder, post_folder, filename), "wb") as f:
                f.write(video_response.content)
            # Adicionando a URL ao conjunto de links baixados
            links_baixados.add(video_url)

print("Conteúdo baixado com sucesso!")
