import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# URL do HTML fornecido
url = "https://kemono.su/patreon/user/36104732/post/105773468"

# Variáveis para permitir que o usuário escolha o que baixar
baixar_anexos = True  # Define como False se não deseja baixar anexos
baixar_videos = True  # Define como False se não deseja baixar vídeos
salvar_info_txt = True  # Define como False se não deseja salvar informações do post em um txt
salvar_comentarios_txt = True  # Define como False se não deseja salvar comentários em um txt

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

# Obtendo o ID do post
post_id_meta_tag = soup.find("meta", attrs={"name": "id"})
post_id = post_id_meta_tag["content"]

# Criando o nome da pasta do post
post_folder = post_id

# Criando as pastas se não existirem
if not os.path.exists(author_folder):
    os.makedirs(author_folder)
if not os.path.exists(os.path.join(author_folder, post_folder)):
    os.makedirs(os.path.join(author_folder, post_folder))

# Função para salvar informações do post em um arquivo de texto
def salvar_info_post(soup, folder):
    info_file_path = os.path.join(folder, "info.txt")
    with open(info_file_path, "w", encoding="utf-8") as f:
        # Título
        title_tag = soup.find("h1", class_="post__title")
        title = " ".join([span.text for span in title_tag.find_all("span")])
        f.write(f"Título: {title}\n")

        # Data de publicação
        published_tag = soup.find("div", class_="post__published")
        published_date = published_tag.text.strip().split(": ")[1]
        f.write(f"Data de publicação: {published_date}\n")

        # Data de importação
        imported_tag = soup.find("div", class_="post__added")
        imported_date = imported_tag.text.strip().split(": ")[1]
        f.write(f"Data de importação: {imported_date}\n")

        # Tags
        tags_section = soup.find("section", id="post-tags")
        tags = [a.text for a in tags_section.find_all("a")]
        f.write(f"Tags: {', '.join(tags)}\n")

        # Anexos
        attachment_tags = soup.find_all("a", class_="post__attachment-link")
        if attachment_tags:
            f.write("Anexos:\n")
            for attachment_tag in attachment_tags:
                attachment_url = attachment_tag["href"]
                attachment_name = attachment_tag.text.strip().split(" ")[-1]
                f.write(f"- {attachment_name}: {attachment_url}\n")
                # Verifica se existe um link "browse"
                browse_tag = attachment_tag.find_next("a", href=True, string="browse »")
                if browse_tag:
                    browse_url = urlparse(url)._replace(path=browse_tag["href"]).geturl()
                    f.write(f"  Conteúdo do anexo: {browse_url}\n")
                    browse_response = requests.get(browse_url)
                    browse_soup = BeautifulSoup(browse_response.text, "html.parser")
                    file_list = browse_soup.find("section", id="password").next_sibling.strip()
                    f.write(f"  Arquivos do Post:\n{file_list}\n")

        # Comentários
        if salvar_comentarios_txt:
            comments_section = soup.find("footer", class_="post__footer")
            if comments_section:
                comments = comments_section.find_all("article", class_="comment")
                if comments:
                    f.write("Comentários:\n")
                    for comment in comments:
                        comment_author = comment.find("a", class_="comment__name").text.strip()
                        comment_text = comment.find("p", class_="comment__message").text.strip()
                        comment_date = comment.find("time", class_="timestamp")["datetime"]
                        f.write(f"- {comment_author} ({comment_date}): {comment_text}\n")

# Salvar informações do post se o usuário desejar
if salvar_info_txt:
    salvar_info_post(soup, os.path.join(author_folder, post_folder))

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
