import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

# Carregar configurações do arquivo JSON
with open("code/config.json", "r") as f:
    config = json.load(f)

baixar_anexos = config["baixar_anexos"]
baixar_videos = config["baixar_videos"]
salvar_info_txt = config["salvar_info_txt"]
salvar_comentarios_txt = config["salvar_comentarios_txt"]

# Solicitar URL(s) ou caminho do arquivo JSON ao usuário
input_choice = input("Digite 1 para inserir URLs diretamente ou 2 para fornecer o caminho de um arquivo JSON: ")

if input_choice == "1":
    urls_input = input("Por favor, insira a URL do post ou as URLs separadas por vírgulas: ")
    urls = [url.strip() for url in urls_input.split(",")]
elif input_choice == "2":
    json_path = input("Por favor, insira o caminho do arquivo JSON: ")
    with open(json_path, "r") as f:
        data = json.load(f)
        urls = []
        for page in data.get("pages", []):
            urls.extend(page.get("posts", []))
else:
    print("Escolha inválida. Saindo.")
    exit()

# Função para baixar conteúdo de uma URL
def baixar_conteudo(url):
    # Fazendo a requisição HTTP e obtendo o conteúdo HTML
    response = requests.get(url)
    html_content = response.text

    # Parsing do HTML usando BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Determinando a pasta base (Kemono ou Coomer)
    parsed_url = urlparse(url)
    if "kemono.su" in parsed_url.netloc or "kemono.party" in parsed_url.netloc:
        base_folder = "Kemono"
    elif "coomer.su" in parsed_url.netloc or "coomer.party" in parsed_url.netloc:
        base_folder = "Coomer"
    else:
        base_folder = "Outros"

    # Encontrar o nome do autor
    author_tag = soup.find("a", class_="post__user-name")
    if author_tag:
        author_name = author_tag.text.strip()
    else:
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

    # Caminho completo da pasta do post
    post_path = os.path.join(base_folder, author_folder, "posts", post_folder)

    # Criando as pastas se não existirem
    os.makedirs(post_path, exist_ok=True)

    # Função para salvar informações do post em um arquivo de texto
    def salvar_info_post(soup, folder):
        info_file_path = os.path.join(folder, "info.txt")
        with open(info_file_path, "w", encoding="utf-8") as f:
            # Título
            title_tag = soup.find("h1", class_="post__title")
            if title_tag:
                title = " ".join([span.text for span in title_tag.find_all("span")])
                f.write(f"Título: {title}\n\n")

            # Data de publicação
            published_tag = soup.find("div", class_="post__published")
            if published_tag:
                published_date = published_tag.text.strip().split(": ")[1]
                f.write(f"Data de publicação: {published_date}\n\n")

            # Data de importação
            imported_tag = soup.find("div", class_="post__added")
            if imported_tag and ": " in imported_tag.text:
                imported_date = imported_tag.text.strip().split(": ")[1]
                f.write(f"Data de importação: {imported_date}\n\n")

            # Conteúdo do post
            content_section = soup.find("div", class_="post__content")
            if content_section:
                content = content_section.get_text(strip=True)
                f.write(f"Conteúdo:\n{content}\n\n")

            # Tags
            tags_section = soup.find("section", id="post-tags")
            if tags_section:
                tags = [a.text for a in tags_section.find_all("a")]
                f.write(f"Tags: {', '.join(tags)}\n\n")

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

            f.write("\n")  # Adiciona uma quebra de linha após os anexos

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
                            f.write(f"- {comment_author} ({comment_date}): {comment_text}\n\n")

    # Salvar informações do post se o usuário desejar
    if salvar_info_txt:
        salvar_info_post(soup, post_path)

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
            with open(os.path.join(post_path, filename), "wb") as f:
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
                with open(os.path.join(post_path, filename), "wb") as f:
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
                with open(os.path.join(post_path, filename), "wb") as f:
                    f.write(video_response.content)
                # Adicionando a URL ao conjunto de links baixados
                links_baixados.add(video_url)

    print(f"Conteúdo do post {url} baixado com sucesso!")

# Iterar sobre todas as URLs fornecidas e baixar o conteúdo
for url in urls:
    baixar_conteudo(url)
