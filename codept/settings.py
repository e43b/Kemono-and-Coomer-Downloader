import os
import json

# URL da documentação
DOCUMENTACAO_URL = "https://github.com/e43b/Kemono-and-Coomer-Downloader/blob/main/codept/doc.md"

# Função para carregar as configurações de um arquivo JSON
def carregar_configuracoes(nome_arquivo):
    try:
        with open(nome_arquivo, 'r') as arquivo:
            configuracoes = json.load(arquivo)
    except FileNotFoundError:
        configuracoes = {}
    return configuracoes

# Função para salvar as configurações em um arquivo JSON
def salvar_configuracoes(configuracoes, nome_arquivo):
    with open(nome_arquivo, 'w') as arquivo:
        json.dump(configuracoes, arquivo, indent=4)

# Função para exibir o menu principal e obter a escolha do usuário
def exibir_menu_principal():
    limpar_console()
    print("Configurar o Sistema\n")
    print("Digite 1 para configurar o sistema de baixar posts")
    print("Digite 2 para configurar o sistema de baixar todos os posts de um perfil")
    print("Digite 3 para voltar para home")
    print("Digite 4 para sair do programa")

    escolha = input("\nDigite sua escolha: ")
    return escolha

# Função para limpar a tela do console de forma multiplataforma e exibir a documentação
def limpar_console():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')
    print(f"\nCaso tenha alguma dúvida, acesse a documentação em {DOCUMENTACAO_URL}\n")

# Função para adicionar o link da documentação ao final do arquivo doc.txt
def adicionar_link_doc_txt():
    with open('doc.txt', 'a') as arquivo:
        arquivo.write(f"\n\nCaso tenha alguma dúvida, acesse a documentação em {DOCUMENTACAO_URL}.")

# Função para configurar o sistema de baixar posts (opção 1)
def configurar_sistema_geral():
    configuracoes = carregar_configuracoes('code/config.json')

    limpar_console()
    print("Configuração do Sistema de Baixar Posts:\n")
    print("1. Baixar Anexos:", "Ativo" if configuracoes.get('baixar_anexos', True) else "Desativado")
    print("2. Baixar Vídeos:", "Ativo" if configuracoes.get('baixar_videos', True) else "Desativado")
    print("3. Salvar Informações:", "Ativo" if configuracoes.get('salvar_info_txt', True) else "Desativado")
    print("4. Salvar Comentários:", "Ativo" if configuracoes.get('salvar_comentarios_txt', True) else "Desativado")

    opcao = input("\nDigite o número da opção que deseja configurar ou '0' para voltar: ")

    if opcao == '1':
        configuracoes['baixar_anexos'] = not configuracoes.get('baixar_anexos', True)
    elif opcao == '2':
        configuracoes['baixar_videos'] = not configuracoes.get('baixar_videos', True)
    elif opcao == '3':
        configuracoes['salvar_info_txt'] = not configuracoes.get('salvar_info_txt', True)
    elif opcao == '4':
        configuracoes['salvar_comentarios_txt'] = not configuracoes.get('salvar_comentarios_txt', True)
    elif opcao == '0':
        return

    salvar_configuracoes(configuracoes, 'code/config.json')
    configurar_sistema_geral()

# Função para configurar o sistema de baixar todos os posts de um perfil (opção 2)
def configurar_sistema_perfil():
    configuracoes = carregar_configuracoes('code/profileconfig.json')

    limpar_console()
    print("Configuração do Sistema de Baixar Posts de Perfil:\n")
    print("1. Baixar Anexos:", "Ativo" if configuracoes.get('baixar_anexos', True) else "Desativado")
    print("2. Baixar Vídeos:", "Ativo" if configuracoes.get('baixar_videos', True) else "Desativado")
    print("3. Salvar Informações:", "Ativo" if configuracoes.get('salvar_info_txt', True) else "Desativado")
    print("4. Salvar Comentários:", "Ativo" if configuracoes.get('salvar_comentarios_txt', True) else "Desativado")
    print("5. Salvar Apenas Posts com Arquivos:", "Ativo" if configuracoes.get('arquivos', False) else "Desativado")
    print("6. Salvar Apenas Posts sem Arquivos:", "Ativo" if configuracoes.get('sem_arquivos', False) else "Desativado")
    print("7. Salvar Ambos os Tipos de Posts:", "Ativo" if configuracoes.get('ambos', True) else "Desativado")

    opcao = input("\nDigite o número da opção que deseja configurar ou '0' para voltar: ")

    if opcao == '1':
        configuracoes['baixar_anexos'] = not configuracoes.get('baixar_anexos', True)
    elif opcao == '2':
        configuracoes['baixar_videos'] = not configuracoes.get('baixar_videos', True)
    elif opcao == '3':
        configuracoes['salvar_info_txt'] = not configuracoes.get('salvar_info_txt', True)
    elif opcao == '4':
        configuracoes['salvar_comentarios_txt'] = not configuracoes.get('salvar_comentarios_txt', True)
    elif opcao == '5':
        configuracoes['arquivos'] = not configuracoes.get('arquivos', False)
        if configuracoes['arquivos']:
            configuracoes['sem_arquivos'] = False
            configuracoes['ambos'] = False
    elif opcao == '6':
        configuracoes['sem_arquivos'] = not configuracoes.get('sem_arquivos', False)
        if configuracoes['sem_arquivos']:
            configuracoes['arquivos'] = False
            configuracoes['ambos'] = False
    elif opcao == '7':
        configuracoes['ambos'] = not configuracoes.get('ambos', True)
        if configuracoes['ambos']:
            configuracoes['arquivos'] = False
            configuracoes['sem_arquivos'] = False
    elif opcao == '0':
        return

    salvar_configuracoes(configuracoes, 'code/profileconfig.json')
    configurar_sistema_perfil()

# Função principal que controla o fluxo do programa
def main():
    adicionar_link_doc_txt()  # Adiciona o link da documentação ao arquivo doc.txt

    while True:
        escolha = exibir_menu_principal()

        if escolha == '1':
            configurar_sistema_geral()
        elif escolha == '2':
            configurar_sistema_perfil()
        elif escolha == '3':
            # Aqui você colocaria a execução do script main.py
            print("\nExecutando script main.py...")
            os.system('python main.py')
        elif escolha == '4':
            print("\nSaindo do programa...")
            break
        else:
            print("\nOpção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
