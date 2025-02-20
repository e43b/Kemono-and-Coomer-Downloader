import os
import sys
import json
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def save_json(file_path, data):
    """Helper function to save JSON files with UTF-8 encoding and pretty formatting"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_config(file_path):
    """Carregar a configuração de um arquivo JSON."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}  # Retorna um dicionário vazio se o arquivo não existir

def get_base_config(profile_url):
    """
    Dynamically configure base URLs and directories based on the profile URL domain
    """
    # Extract domain from the profile URL
    domain = profile_url.split('/')[2]
    
    if domain not in ['kemono.su', 'coomer.su']:
        raise ValueError(f"Unsupported domain: {domain}")
    
    BASE_API_URL = f"https://{domain}/api/v1"
    BASE_SERVER = f"https://{domain}"
    BASE_DIR = domain.split('.')[0]  # 'kemono' or 'coomer'
    
    return BASE_API_URL, BASE_SERVER, BASE_DIR

def is_offset(value):
    """Determina se o valor é um offset (até 5 dígitos) ou um ID."""
    try:
        # Tenta converter para inteiro e verifica o comprimento
        return isinstance(int(value), int) and len(value) <= 5
    except ValueError:
        # Se não for um número, não é offset
        return False

def parse_fetch_mode(fetch_mode, total_count):
    """
    Analisa o modo de busca e retorna os offsets correspondentes
    """
    # Caso especial: buscar todos os posts
    if fetch_mode == "all":
        return list(range(0, total_count, 50))
    
    # Se for um número único (página específica)
    if fetch_mode.isdigit():
        if is_offset(fetch_mode):
            return [int(fetch_mode)]
        else:
            # Se for um ID específico, retorna como tal
            return ["id:" + fetch_mode]
    
    # Caso seja um intervalo
    if "-" in fetch_mode:
        start, end = fetch_mode.split("-")
        
        # Tratar "start" e "end" especificamente
        if start == "start":
            start = 0
        else:
            start = int(start)
        
        if end == "end":
            end = total_count
        else:
            end = int(end)
        
        # Se os valores são offsets
        if start <= total_count and end <= total_count:
            # Calcular o número de páginas necessárias para cobrir o intervalo
            # Usa ceil para garantir que inclua a página final
            import math
            num_pages = math.ceil((end - start) / 50)
            
            # Gerar lista de offsets
            return [start + i * 50 for i in range(num_pages)]
        
        # Se parecem ser IDs, retorna o intervalo de IDs
        return ["id:" + str(start) + "-" + str(end)]
    
    raise ValueError(f"Modo de busca inválido: {fetch_mode}")

def get_artist_info(profile_url):
    # Extrair serviço e user_id do URL
    parts = profile_url.split("/")
    service = parts[-3]
    user_id = parts[-1]
    return service, user_id

def fetch_posts(base_api_url, service, user_id, offset=0):
    # Buscar posts da API
    url = f"{base_api_url}/{service}/user/{user_id}/posts-legacy?o={offset}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_json_incrementally(file_path, new_posts, start_offset, end_offset):
    # Criar um novo dicionário com os posts atuais
    data = {
        "total_posts": len(new_posts),
        "posts": new_posts
    }
    
    # Salvar o novo arquivo, substituindo o existente
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def process_posts(posts, previews, attachments_data, page_number, offset, base_server, save_empty_files=True, id_filter=None):
    # Processar posts e organizar os links dos arquivos
    processed = []
    for post in posts:
        # Filtro de ID se especificado
        if id_filter and not id_filter(post['id']):
            continue

        result = {
            "id": post["id"],
            "user": post["user"],
            "service": post["service"],
            "title": post["title"],
            "link": f"{base_server}/{post['service']}/user/{post['user']}/post/{post['id']}",
            "page": page_number,
            "offset": offset,
            "files": []
        }

        # Combina previews e attachments_data em uma única lista para busca
        all_data = previews + attachments_data

        # Processar arquivos no campo file
        if "file" in post and post["file"]:
            matching_data = next(
                (item for item in all_data if item["path"] == post["file"]["path"]),
                None
            )
            if matching_data:
                file_url = f"{matching_data['server']}/data{post['file']['path']}"
                if file_url not in [f["url"] for f in result["files"]]:
                    result["files"].append({"name": post["file"]["name"], "url": file_url})

        # Processar arquivos no campo attachments
        for attachment in post.get("attachments", []):
            matching_data = next(
                (item for item in all_data if item["path"] == attachment["path"]),
                None
            )
            if matching_data:
                file_url = f"{matching_data['server']}/data{attachment['path']}"
                if file_url not in [f["url"] for f in result["files"]]:
                    result["files"].append({"name": attachment["name"], "url": file_url})

        # Ignorar posts sem arquivos se save_empty_files for False
        if not save_empty_files and not result["files"]:
            continue

        processed.append(result)

    return processed

def sanitize_filename(value):
    """Remove caracteres que podem quebrar a criação de pastas."""
    return value.replace("/", "_").replace("\\", "_")

def main():
    # Verificar argumentos de linha de comando
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python posts.py <profile_url> [fetch_mode]")
        print("Possible search modes:")
        print("- all")
        print("- <page number>")
        print("- start-end")
        print("- <start_id>-<end_id>")
        sys.exit(1)

    # Definir profile_url do argumento
    profile_url = sys.argv[1]
    
    # Definir FETCH_MODE (padrão para "all" se não especificado)
    FETCH_MODE = sys.argv[2] if len(sys.argv) == 3 else "all"
    
    config_file_path = os.path.join("config", "conf.json")

    # Carregar a configuração do arquivo JSON
    config = load_config(config_file_path)

    # Pegar o valor de 'process_from_oldest' da configuração
    SAVE_EMPTY_FILES = config.get("get_empty_posts", False)  # Alterar para True se quiser salvar posts sem arquivos

    # Configurar base URLs dinamicamente
    BASE_API_URL, BASE_SERVER, BASE_DIR = get_base_config(profile_url)
    
    # Pasta base
    base_dir = BASE_DIR
    os.makedirs(base_dir, exist_ok=True)

    # Atualizar o arquivo profiles.json
    profiles_file = os.path.join(base_dir, "profiles.json")
    if os.path.exists(profiles_file):
        with open(profiles_file, "r", encoding="utf-8") as f:
            profiles = json.load(f)
    else:
        profiles = {}

    # Buscar primeiro conjunto de posts para informações gerais
    service, user_id = get_artist_info(profile_url)
    initial_data = fetch_posts(BASE_API_URL, service, user_id, offset=0)
    name = initial_data["props"]["name"]
    count = initial_data["props"]["count"]

    # Salvar informações do artista
    artist_info = {
        "id": user_id,
        "name": name,
        "service": service,
        "indexed": initial_data["props"]["artist"]["indexed"],
        "updated": initial_data["props"]["artist"]["updated"],
        "public_id": initial_data["props"]["artist"]["public_id"],
        "relation_id": initial_data["props"]["artist"]["relation_id"],
    }
    profiles[user_id] = artist_info
    save_json(profiles_file, profiles)

    # Sanitizar os valores
    safe_name = sanitize_filename(name)
    safe_service = sanitize_filename(service)
    safe_user_id = sanitize_filename(user_id)

    # Pasta do artista
    artist_dir = os.path.join(base_dir, f"{safe_name}-{safe_service}-{safe_user_id}")
    os.makedirs(artist_dir, exist_ok=True)

    # Processar modo de busca
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        offsets = parse_fetch_mode(FETCH_MODE, count)
    except ValueError as e:
        print(e)
        return

    # Verificar se é busca por ID específico
    id_filter = None
    found_ids = set()
    if isinstance(offsets[0], str) and offsets[0].startswith("id:"):
        # Extrair IDs para filtro
        id_range = offsets[0].split(":")[1]
        
        if "-" in id_range:
            id1, id2 = map(str, sorted(map(int, id_range.split("-"))))
            id_filter = lambda x: id1 <= str(x) <= id2
        else:
            id_filter = lambda x: x == id_range

        # Redefinir offsets para varrer todas as páginas
        offsets = list(range(0, count, 50))

    # Nome do arquivo JSON com range de offsets
    if len(offsets) > 1:
        file_path = os.path.join(artist_dir, f"posts-{offsets[0]}-{offsets[-1]}-{today}.json")
    else:
        file_path = os.path.join(artist_dir, f"posts-{offsets[0]}-{today}.json")

    new_posts= []
    # Processamento principal
    for offset in offsets:
        page_number = (offset // 50) + 1
        post_data = fetch_posts(BASE_API_URL, service, user_id, offset=offset)
        posts = post_data["results"]
        previews = [item for sublist in post_data.get("result_previews", []) for item in sublist]
        attachments = [item for sublist in post_data.get("result_attachments", []) for item in sublist]

        processed_posts = process_posts(
            posts, 
            previews, 
            attachments, 
            page_number, 
            offset, 
            BASE_SERVER,
            save_empty_files=SAVE_EMPTY_FILES,
            id_filter=id_filter
        )
        new_posts.extend(processed_posts)
        # Salvar posts incrementais no JSON
        if processed_posts:
            save_json_incrementally(file_path, new_posts, offset, offset+50)
            
            # Verificar se encontrou os IDs desejados
            if id_filter:
                found_ids.update(post['id'] for post in processed_posts)
                
                # Verificar se encontrou ambos os IDs
                if (id1 in found_ids) and (id2 in found_ids):
                    print(f"Found both IDs: {id1} e {id2}")
                    break

    # Imprimir o caminho completo do arquivo JSON gerado
    print(f"{os.path.abspath(file_path)}")

if __name__ == "__main__":
    main()
