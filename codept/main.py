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
        print(f"Erro: Arquivo {requirements_file} não encontrado.")
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
                    print(f"Instalando o pacote: {package}")
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

Criado por E43b
GitHub: https://github.com/e43b
Discord: https://discord.gg/GNJbxzD8bK
Repositório do Projeto: https://github.com/e43b/Kemono-and-Coomer-Downloader
Faça uma Doação: https://ko-fi.com/e43bs
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
        print(f"Erro ao normalizar caminho: {e}")
        return path

def run_download_script(json_path):
    """Roda o script de download com o JSON gerado e faz tracking detalhado em tempo real"""
    try:
        # Normalizar o caminho do JSON
        json_path = normalize_path(json_path)

        # Verificar se o arquivo JSON existe
        if not os.path.exists(json_path):
            print(f"Erro: Arquivo JSON não encontrado: {json_path}")
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
        print(f"Extração de posts concluída: {total_posts} posts encontrados")
        print(f"Número total de arquivos a baixar: {total_files}")
        print("Iniciando downloads de posts")

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
                        print(f"Post {post_id} baixado completamente ({current_files_count}/{expected_files_count} arquivos)")
                    else:
                        print(f"Post {post_id} parcialmente baixado: {current_files_count}/{expected_files_count} arquivos")

                except Exception as e:
                    print(f"Erro durante o download do post {post_id}: {e}")

                # Pequeno delay para evitar sobrecarga
                time.sleep(0.5)

        print("\nTodos os posts foram processados!")

    except Exception as e:
        print(f"Erro inesperado: {e}")
        # Adicionar mais detalhes para diagnóstico
        import traceback
        traceback.print_exc()

def download_specific_posts():
    """Opção para baixar posts específicos"""
    clear_screen()
    display_logo()
    print("Baixar 1 post ou alguns posts distintos")
    print("------------------------------------")
    print("Escolha o método de entrada:")
    print("1 - Digitar os links diretamente")
    print("2 - Carregar os links de um arquivo TXT")
    print("3 - Voltar para o menu principal")
    choice = input("\nDigite sua escolha (1/2/3): ")

    links = []

    if choice == '3':
        return
    
    elif choice == '1':
        print("Cole os links dos posts (separados por vírgula):")
        links = input("Links: ").split(',')
    elif choice == '2':
        file_path = input("Digite o caminho para o arquivo TXT: ").strip()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                links = content.split(',')
        else:
            print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
            input("\nPressione Enter para continuar...")
            return
    else:
        print("Opção inválida. Retornando ao menu anterior.")
        input("\nPressione Enter para continuar...")
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
                print(f"Domínio não suportado: {domain}")
                continue

            # Executa o script específico para o domínio
            subprocess.run(['python', script_path, link], check=True)
        except IndexError:
            print(f"Erro no formato do link: {link}")
        except subprocess.CalledProcessError:
            print(f"Erro ao baixar o post: {link}")

    input("\nPressione Enter para continuar...")

def download_profile_posts():
    """Opção para baixar posts de um perfil"""
    clear_screen()
    display_logo()
    print("Baixar Posts de um Perfil")
    print("-----------------------")
    print("1 - Baixar todos os posts de um perfil")
    print("2 - Baixar Posts de uma página específica")
    print("3 - Baixar posts de um intervalo de páginas")
    print("4 - Baixar posts entre dois posts específicos")
    print("5 - Voltar para o menu principal")
    
    choice = input("\nDigite sua escolha (1/2/3/4/5): ")
    
    if choice == '5':
        return
    
    profile_link = input("Cole o link do perfil: ")
    
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
                print("Nenhuma saída do subprocesso.")
        
        elif choice == '2':
            page = input("Digite o número da página (0 = primeira página, 50 = segunda, etc.): ")
            posts_process = subprocess.run(['python', os.path.join('codes', 'posts.py'), profile_link, page], 
                                           capture_output=True, text=True, check=True)
            for line in posts_process.stdout.split('\n'):
                if line.endswith('.json'):
                    json_path = line.strip()
                    break
        
        elif choice == '3':
            start_page = input("Digite a página inicial (start, 0, 50, 100, etc.): ")
            end_page = input("Digite a página final (ou use end, 300, 350, 400): ")
            posts_process = subprocess.run(['python', os.path.join('codes', 'posts.py'), profile_link, f"{start_page}-{end_page}"], 
                                           capture_output=True, text=True, check=True)
            for line in posts_process.stdout.split('\n'):
                if line.endswith('.json'):
                    json_path = line.strip()
                    break
        
        elif choice == '4':
            first_post = input("Cole o link ou ID do primeiro post: ")
            second_post = input("Cole o link ou ID do segundo post: ")
            
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
            print("Não foi possível encontrar o caminho do JSON.")
    
    except subprocess.CalledProcessError as e:
        print(f"Erro ao gerar JSON: {e}")
        print(e.stderr)
    
    input("\nPressione Enter para continuar...")

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
        print("Personalizar Configurações")
        print("------------------------")
        print(f"1 - Pegar posts vazios: {config['get_empty_posts']}")
        print(f"2 - Baixar posts mais antigos primeiro: {config['process_from_oldest']}")
        print(f"3 - Para posts individuais, criar arquivo com informações (título, descrição, etc.): {config['save_info']}")
        print(f"4 - Escolha o tipo de arquivo para salvar informações (Markdown ou TXT): {config['post_info']}")
        print(f"5 - Escolha o tipo de método de download (Wget ou Requests): {config['download_method']}")
        print("6 - Voltar ao menu principal")

        choice = input("\nEscolha uma opção (1/2/3/4/5/6): ")

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
            print("Opção inválida. Tente novamente.")

        # Salvar as configurações no arquivo
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        print("\nConfigurações atualizadas.")
        time.sleep(1)

def main_menu():
    """Menu principal do aplicativo"""
    while True:
        clear_screen()
        display_logo()
        print("Escolha uma opção:")
        print("1 - Baixar 1 post ou alguns posts distintos")
        print("2 - Baixar todos os posts de um perfil")
        print("3 - Personalizar as configurações do programa")
        print("4 - Sair do programa")
        
        choice = input("\nDigite sua escolha (1/2/3/4): ")
        
        if choice == '1':
            download_specific_posts()
        elif choice == '2':
            download_profile_posts()
        elif choice == '3':
            customize_settings()
        elif choice == '4':
            print("Saindo do programa. Até logo!")
            break
        else:
            input("Opção inválida. Pressione Enter para continuar...")

if __name__ == "__main__":
    print("Verificando dependências...")
    install_requirements()
    print("Dependências verificadas.\n")
    main_menu()
