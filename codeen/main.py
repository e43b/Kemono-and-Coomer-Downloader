import os
import sys
import subprocess
import re
import json
import time
import importlib

def install_requirements():
    """Verifica e instala as dependências do requirements.txt."""
    requirements_file = "requirements.txt"

    if not os.path.exists(requirements_file):
        print(f"Error: File {requirements_file} not found.")
        return

    with open(requirements_file, 'r', encoding='utf-8') as req_file:
        for line in req_file:
            # Lê cada linha, ignora vazias ou comentários
            package = line.strip()
            if package and not package.startswith("#"):
                try:
                    # Tenta importar o pacote para verificar se já está instalado
                    package_name = package.split("==")[0]  # Ignora versão específica na importação
                    importlib.import_module(package_name)
                except ImportError:
                    # Se falhar, instala o pacote usando pip
                    print(f"Installing the package: {package}")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def clear_screen():
    """Limpa a tela do console de forma compatível com diferentes sistemas operacionais"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_logo():
    """Exibe o logo do projeto"""
    logo = """
 _  __                                                   
| |/ /___ _ __ ___   ___  _ __   ___                     
| ' // _ \ '_ ` _ \ / _ \| '_ \ / _ \                    
| . \  __/ | | | | | (_) | | | | (_) |                   
|_|\_\___|_| |_| |_|\___/|_| |_|\___/                    
 / ___|___   ___  _ __ ___   ___ _ __                    
| |   / _ \ / _ \| '_ ` _ \ / _ \ '__|                   
| |__| (_) | (_) | | | | | |  __/ |                      
 \____\___/ \___/|_| |_| |_|\___|_|          _           
|  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __ 
| | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
| |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
|____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   

Created by E43b
GitHub: https://github.com/e43b
Discord: https://discord.gg/GNJbxzD8bK
Project Repository: https://github.com/e43b/Kemono-and-Coomer-Downloader
Donate: https://ko-fi.com/e43bs
"""
    print(logo)

def normalize_path(path):
    """
    Normaliza o caminho do arquivo para lidar com caracteres não-ASCII
    """
    try:
        # Se o caminho original existir, retorna ele
        if os.path.exists(path):
            return path
            
        # Extrai o nome do arquivo e os componentes do caminho
        filename = os.path.basename(path)
        path_parts = path.split(os.sep)
        
        # Identifica se está procurando em kemono ou coomer
        base_dir = None
        if 'kemono' in path_parts:
            base_dir = 'kemono'
        elif 'coomer' in path_parts:
            base_dir = 'coomer'
            
        if base_dir:
            # Procura em todos os subdiretórios do diretório base
            for root, dirs, files in os.walk(base_dir):
                if filename in files:
                    return os.path.join(root, filename)
        
        # Se ainda não encontrou, tenta o caminho normalizado
        return os.path.abspath(os.path.normpath(path))

    except Exception as e:
        print(f"Error when normalizing path: {e}")
        return path

def run_download_script(json_path):
    """Roda o script de download com o JSON gerado e faz tracking detalhado em tempo real"""
    try:
        # Normalizar o caminho do JSON
        json_path = normalize_path(json_path)

        # Verificar se o arquivo JSON existe
        if not os.path.exists(json_path):
            print(f"Error: JSON file not found: {json_path}")
            return

        # Ler configurações
        config_path = normalize_path(os.path.join('config', 'conf.json'))
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)

        # Ler o JSON de posts
        with open(json_path, 'r', encoding='utf-8') as posts_file:
            posts_data = json.load(posts_file)

        # Análise inicial
        total_posts = posts_data['total_posts']
        post_ids = [post['id'] for post in posts_data['posts']]

        # Contagem de arquivos
        total_files = sum(len(post['files']) for post in posts_data['posts'])

        # Imprimir informações iniciais
        print(f"Post extraction completed: {total_posts} posts found")
        print(f"Total number of files to download: {total_files}")
        print("Starting post downloads")

        # Determinar ordem de processamento
        if config['process_from_oldest']:
            post_ids = sorted(post_ids)  # Ordem do mais antigo ao mais recente
        else:
            post_ids = sorted(post_ids, reverse=True)  # Ordem do mais recente ao mais antigo

        # Pasta base para posts usando normalização de caminho
        posts_folder = normalize_path(os.path.join(os.path.dirname(json_path), 'posts'))
        os.makedirs(posts_folder, exist_ok=True)

        # Processar cada post
        for idx, post_id in enumerate(post_ids, 1):
            # Encontrar dados do post específico
            post_data = next((p for p in posts_data['posts'] if p['id'] == post_id), None)

            if post_data:
                # Pasta do post específico com normalização
                post_folder = normalize_path(os.path.join(posts_folder, post_id))
                os.makedirs(post_folder, exist_ok=True)

                # Contar número de arquivos no JSON para este post
                expected_files_count = len(post_data['files'])

                # Contar arquivos já existentes na pasta
                existing_files = [f for f in os.listdir(post_folder) if os.path.isfile(os.path.join(post_folder, f))]
                existing_files_count = len(existing_files)

                # Se já tem todos os arquivos, pula o download
                if existing_files_count == expected_files_count:
                    continue
                
                try:
                    # Normalizar caminho do script de download
                    download_script = normalize_path(os.path.join('codes', 'down.py'))
                    
                    # Use subprocess.Popen com caminho normalizado e suporte a Unicode
                    download_process = subprocess.Popen(
                        [sys.executable, download_script, json_path, post_id], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT, 
                        universal_newlines=True,
                        encoding='utf-8'
                    )

                    # Capturar e imprimir output em tempo real
                    while True:
                        output = download_process.stdout.readline()
                        if output == '' and download_process.poll() is not None:
                            break
                        if output:
                            print(output.strip())

                    # Verificar código de retorno
                    download_process.wait()

                    # Após o download, verificar novamente os arquivos
                    current_files = [f for f in os.listdir(post_folder) if os.path.isfile(os.path.join(post_folder, f))]
                    current_files_count = len(current_files)

                    # Verificar o resultado do download
                    if current_files_count == expected_files_count:
                        print(f"Post {post_id} downloaded completely ({current_files_count}/{expected_files_count} files)")
                    else:
                        print(f"Post {post_id} partially downloaded: {current_files_count}/{expected_files_count} files")

                except Exception as e:
                    print(f"Error while downloading post {post_id}: {e}")

                # Pequeno delay para evitar sobrecarga
                time.sleep(0.5)

        print("\nAll posts have been processed!")

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Adicionar mais detalhes para diagnóstico
        import traceback
        traceback.print_exc()

def download_specific_posts():
    """Opção para baixar posts específicos"""
    clear_screen()
    display_logo()
    print("Download 1 post or a few separate posts")
    print("------------------------------------")
    print("Choose the input method:")
    print("1 - Enter the links directly")
    print("2 - Loading links from a TXT file")
    print("3 - Back to the main menu")
    choice = input("\nEnter your choice (1/2/3): ")

    links = []

    if choice == '3':
        return
    
    elif choice == '1':
        print("Paste the links to the posts (separated by commas):")
        links = input("Links: ").split(',')
    elif choice == '2':
        file_path = input("Enter the path to the TXT file: ").strip()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                links = content.split(',')
        else:
            print(f"Error: The file '{file_path}' was not found.")
            input("\nPress Enter to continue...")
            return
    else:
        print("Invalid option. Return to the previous menu.")
        input("\nPress Enter to continue...")
        return

    links = [link.strip() for link in links if link.strip()]

    for link in links:
        try:
            domain = link.split('/')[2]
            if domain == 'kemono.su':
                script_path = os.path.join('codes', 'kcposts.py')
            elif domain == 'coomer.su':
                script_path = os.path.join('codes', 'kcposts.py')
            else:
                print(f"Domain not supported: {domain}")
                continue

            # Executa o script específico para o domínio
            subprocess.run(['python', script_path, link], check=True)
        except IndexError:
            print(f"Link format error: {link}")
        except subprocess.CalledProcessError:
            print(f"Error downloading the post: {link}")

    input("\nPress Enter to continue...")

def download_profile_posts():
    """Opção para baixar posts de um perfil"""
    clear_screen()
    display_logo()
    print("Download Profile Posts")
    print("-----------------------")
    print("1 - Download all posts from a profile")
    print("2 - Download posts from a specific page")
    print("3 - Downloading posts from a range of pages")
    print("4 - Downloading posts between two specific posts")
    print("5 - Back to the main menu")
    
    choice = input("\nEnter your choice (1/2/3/4/5): ")
    
    if choice == '5':
        return
    
    profile_link = input("Paste the profile link: ")
    
    try:
        json_path = None

        if choice == '1':
            posts_process = subprocess.run(
                ['python', os.path.join('codes', 'posts.py'), profile_link, 'all'],
                capture_output=True,
                text=True,
                encoding='utf-8',  # Certifique-se de que a saída é decodificada corretamente
                check=True
            )

            # Verificar se stdout contém dados
            if posts_process.stdout:
                for line in posts_process.stdout.split('\n'):
                    if line.endswith('.json'):
                        json_path = line.strip()
                        break
            else:
                print("No output from the sub-process.")
        
        elif choice == '2':
            page = input("Enter the page number (0 = first page, 50 = second, etc.): ")
            posts_process = subprocess.run(['python', os.path.join('codes', 'posts.py'), profile_link, page], 
                                           capture_output=True, text=True, check=True)
            for line in posts_process.stdout.split('\n'):
                if line.endswith('.json'):
                    json_path = line.strip()
                    break
        
        elif choice == '3':
            start_page = input("Enter the start page (start, 0, 50, 100, etc.): ")
            end_page = input("Enter the final page (or use end, 300, 350, 400): ")
            posts_process = subprocess.run(['python', os.path.join('codes', 'posts.py'), profile_link, f"{start_page}-{end_page}"], 
                                           capture_output=True, text=True, check=True)
            for line in posts_process.stdout.split('\n'):
                if line.endswith('.json'):
                    json_path = line.strip()
                    break
        
        elif choice == '4':
            first_post = input("Paste the link or ID of the first post: ")
            second_post = input("Paste the link or ID from the second post: ")
            
            first_id = first_post.split('/')[-1] if '/' in first_post else first_post
            second_id = second_post.split('/')[-1] if '/' in second_post else second_post
            
            posts_process = subprocess.run(['python', os.path.join('codes', 'posts.py'), profile_link, f"{first_id}-{second_id}"], 
                                           capture_output=True, text=True, check=True)
            for line in posts_process.stdout.split('\n'):
                if line.endswith('.json'):
                    json_path = line.strip()
                    break
        
        # Se um JSON foi gerado, roda o script de download
        if json_path:
            run_download_script(json_path)
        else:
            print("The JSON path could not be found.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error generating JSON: {e}")
        print(e.stderr)
    
    input("\nPress Enter to continue...")

def customize_settings():
    """Opção para personalizar configurações"""
    config_path = os.path.join('config', 'conf.json')
    import json

    # Carregar o arquivo de configuração
    with open(config_path, 'r') as f:
        config = json.load(f)

    while True:
        clear_screen()
        display_logo()
        print("Customize Settings")
        print("------------------------")
        print(f"1 - Take empty posts: {config['get_empty_posts']}")
        print(f"2 - Download older posts first: {config['process_from_oldest']}")
        print(f"3 - For individual posts, create a file with information (title, description, etc.): {config['save_info']}")
        print(f"4 - Choose the type of file to save the information (Markdown or TXT): {config['post_info']}")
        print(f"5 - Choose the type of  (Wget or Requests): {config['download_method']}")
        print("6 - Back to the main menu")

        choice = input("\nChoose an option (1/2/3/4/5/6): ")

        if choice == '1':
            config['get_empty_posts'] = not config['get_empty_posts']
        elif choice == '2':
            config['process_from_oldest'] = not config['process_from_oldest']
        elif choice == '3':
            config['save_info'] = not config['save_info']
        elif choice == '4':
            # Alternar entre "md" e "txt"
            config['post_info'] = 'txt' if config['post_info'] == 'md' else 'md'
        elif choice == '5':
            # Alternar entre "request" e "wget"
            config['download_method'] = 'request' if config['download_method'] == 'wget' else 'wget'
        elif choice == '6':
            # Sair do menu de configurações
            break
        else:
            print("Invalid option. Please try again.")

        # Salvar as configurações no arquivo
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        print("\nUpdated configurations.")
        time.sleep(1)

def main_menu():
    """Menu principal do aplicativo"""
    while True:
        clear_screen()
        display_logo()
        print("Choose an option:")
        print("1 - Download 1 post or a few separate posts")
        print("2 - Download all posts from a profile")
        print("3 - Customize the program settings")
        print("4 - Exit the program")
        
        choice = input("\nEnter your choice (1/2/3/4): ")
        
        if choice == '1':
            download_specific_posts()
        elif choice == '2':
            download_profile_posts()
        elif choice == '3':
            customize_settings()
        elif choice == '4':
            print("Leaving the program. See you later!")
            break
        else:
            input("Invalid option. Press Enter to continue...")

if __name__ == "__main__":
    print("Checking dependencies...")
    install_requirements()
    print("Verified dependencies.\n")
    main_menu()
