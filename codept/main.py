import os

# Função para limpar a tela do console
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para baixar posts específicos
def baixar_posts():
    limpar_tela()
    print("Executando script para baixar posts específicos...")
    os.system('python code/post.py')
    input("\nPressione Enter para voltar ao menu...")

# Função para baixar todos os posts de um perfil
def baixar_todos_posts_perfil():
    limpar_tela()
    print("Executando script para baixar todos os posts de um perfil...")
    os.system('python code/profile.py')
    input("\nPressione Enter para voltar ao menu...")

# Função para baixar DMs de um perfil
def baixar_dms():
    limpar_tela()
    print("Executando script para baixar DMs de um perfil...")
    os.system('python code/dm.py')
    input("\nPressione Enter para voltar ao menu...")

# Função para personalizar as configurações de download
def personalizar_configuracoes():
    limpar_tela()
    print("Executando script para personalizar as configurações de download...")
    os.system('python settings.py')
    input("\nPressione Enter para voltar ao menu...")

# Verificar e instalar as dependências necessárias
def verificar_instalar_dependencias():
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Bibliotecas necessárias não encontradas.")
        choice = input("Deseja instalar as bibliotecas necessárias? (s/n): ").strip().lower()
        if choice == 's':
            os.system('pip install -r requirements.txt')
        else:
            print("Instalação cancelada. O programa pode não funcionar corretamente.")
            input("\nPressione Enter para continuar...")

# Menu principal
def menu():
    verificar_instalar_dependencias()

    while True:
        limpar_tela()
        print("""
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
Discord: https://discord.gg/TaPhfXawcE
Repositório do Projeto: https://github.com/e43b/Kemono-and-Coomer-Downloader

Com este script é possível baixar vários posts ou todos os posts de um perfil no Kemono ou Coomer, também sendo possível baixar DMs de perfis do Kemono:

Escolha uma opção:
1 - Baixar 1 post ou alguns posts distintos
2 - Baixar todos os posts de um perfil
3 - Baixar DMs de um perfil (atualmente apenas o Kemono tem sistema de DMs)
4 - Personalizar as configurações de download do programa
5 - Sair do programa
""")
        opcao = input("Digite sua escolha (1/2/3/4/5): ")

        if opcao == '1':
            baixar_posts()
        elif opcao == '2':
            baixar_todos_posts_perfil()
        elif opcao == '3':
            baixar_dms()
        elif opcao == '4':
            personalizar_configuracoes()
        elif opcao == '5':
            break
        else:
            print("Opção inválida! Digite 1, 2, 3, 4 ou 5.")
            input("Pressione Enter para continuar...")

# Executar o programa
if __name__ == "__main__":
    menu()
