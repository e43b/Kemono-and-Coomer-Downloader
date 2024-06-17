# Kemono and Coomer Downloader  [![Views](https://hits.sh/github.com/e43bkmncoom/hits.svg)](https://github.com/e43b/Anibunker-Downloader/)

###### [![](img/en-flag.svg) English](README.md) | [![](img/br.png) Português](README-ptbr.md)

### Faça uma doação
Acesse [link](https://oxapay.com/donate/40874860).

O **Kemono and Coomer Downloader** é uma ferramenta que permite baixar posts dos sites [Kemono](https://kemono.su/) e [Coomer](https://coomer.su/).

Com essa ferramenta, é possível baixar posts únicos, múltiplos posts sequencialmente, baixar todos os posts de um perfil e baixar todas as DMs de um perfil do Kemono. Também é possível configurar o que deseja salvar nos posts: anexos, vídeos, criar um arquivo `.txt` com informações sobre o post, entre outros. Para mais informações, acesse a [documentação](https://github.com/e43b/Kemono-and-Coomer-Downloader/blob/main/codept/doc.md).

## Como Usar

1. **Certifique-se de ter o Python instalado em seu sistema.**
2. **Clone este repositório:**

    ```sh
    git clone https://github.com/e43b/Kemono-and-Coomer-Downloader/
    ```

3. **Navegue até o diretório do projeto:**

    ```sh
    cd Kemono-and-Coomer-Downloader
    ```

4. **Selecione o idioma desejado:**

    - A pasta `codeen` contém a versão em inglês.
    - A pasta `codept` contém a versão em português.

5. **Execute o script principal:**

    ```sh
    python main.py
    ```

6. **Siga as instruções no menu para escolher o que deseja baixar ou personalizar o programa.**

## Bibliotecas

As bibliotecas necessárias são: `requests` e `beautifulsoup4`. Ao iniciar o script pela primeira vez, se as bibliotecas não estiverem instaladas, será solicitado que você as instale. Basta digitar "s" e elas serão instaladas automaticamente.

![Requirements](img/bibliotecas.png)

## Funcionalidades

### Página Inicial

A página inicial do projeto apresenta as principais opções disponíveis para facilitar a utilização da ferramenta.

![Página Inicial](img/home.png)

### Baixar Post

Para baixar posts específicos, basta inserir o link do post. Se desejar baixar vários posts, separe os links por vírgula. Exemplo:

```sh
https://kemono.su/patreon/user/133054/post/82477856 , https://coomer.su/fansly/user/285310079517863936/post/614339200069672960 , https://coomer.su/fansly/user/285310079517863936/post/611301068940255234
```

![Posts](img/posts.png)

### Baixar Todos os Posts de um Perfil

Insira o link de um perfil do Kemono ou Coomer, e o script iniciará o download de todos os posts que combinam com a configuração do programa para baixar todos os posts de um perfil.

![Profile](img/perfil.png)

### Baixar DMs

Funciona apenas em perfis do site Kemono, pois o Coomer não possui essa função. Basta colocar o link do perfil, e todas as DMs serão extraídas em `.txt` e salvas na pasta `dm`.

![DM](img/dm.png)
![DM arquivos](img/dmarchives.png)

## Organização dos Arquivos

Os posts são salvos em pastas para facilitar a organização. A estrutura das pastas é a seguinte:

1. **Plataforma:** Uma pasta principal é criada para a plataforma (Kemono ou Coomer).
2. **Autor:** Dentro da pasta da plataforma, é criada uma pasta para cada autor.
3. **Posts:** Dentro da pasta do autor, há uma pasta `posts` onde são salvos os posts. Cada post é salvo em uma subpasta identificada pelo ID do post.
4. **DMs:** Dentro da pasta do autor, há também uma pasta `DMs` onde são salvos os arquivos `.txt` das DMs.

Exemplo da estrutura de pastas:

```
Kemono-and-Coomer-Downloader/
│
├── kemono/                               # Pasta da plataforma Kemono
│   ├── autor1/                           # Pasta do autor 1
│   │   ├── posts/                        # Pasta de posts do autor 1
│   │   │   ├── postID1/                  # Pasta do post com ID 1
│   │   │   │   ├── conteudo_do_post      # Conteúdo do post
│   │   │   │   └── ...                   # Outros arquivos do post
│   │   │   └── postID2/                  # Pasta do post com ID 2
│   │   │       ├── conteudo_do_post      # Conteúdo do post
│   │   │       └── ...                   # Outros arquivos do post
│   │   └── DMs/                          # Pasta de DMs do autor 1
│   │       ├── dm1.txt                   # DM 1
│   │       ├── dm2.txt                   # DM 2
│   │       └── ...                       # Outras DMs
│   └── autor2/                           # Pasta do autor 2
│       ├── posts/                        # Pasta de posts do autor 2
│       └── DMs/                          # Pasta de DMs do autor 2
│
└── coomer/                               # Pasta da plataforma Coomer
    ├── autor1/                           # Pasta do autor 1
    │   ├── posts/                        # Pasta de posts do autor 1
    │   └── DMs/                          # Pasta de DMs do autor 1 (se aplicável)
    └── autor2/                           # Pasta do autor 2
        ├── posts/                        # Pasta de posts do autor 2
        └── DMs/                          # Pasta de DMs do autor 2 (se aplicável)
```

![Arquivos](img/arquivo.png)

## Configuração

A página de configuração permite que você personalize o programa de acordo com suas necessidades.

![Settings](img/configure.png)

### Configuração de Posts

No modo de configuração de posts, o usuário pode definir várias opções, incluindo:

- **Baixar Anexos:** Escolha se deseja baixar ou não anexos.
- **Baixar Vídeos:** Escolha se deseja baixar vídeos quando disponíveis.
- **Salvar Informações:** Salve informações em um arquivo `.txt`, como título, data de postagem, data de importação e conteúdo.
- **Salvar Comentários:** Salve comentários do post no arquivo `.txt`. Para salvar os comentários, a opção de salvar informações deve estar ativada.

![Settings](img/postconfig.png)

### Configuração de Perfil

No modo de configuração de perfil, o usuário pode definir o que deseja baixar dos posts, de maneira similar às opções de configuração de posts. O diferencial é que o usuário pode filtrar por posts que tenham ou não tenham imagens, podendo escolher uma ou outra, ou ambas as versões.

![Settings](img/configprofile.png)

Para mais detalhes, consulte a [documentação](https://github.com/e43b/Kemono-and-Coomer-Downloader/blob/main/codept/doc.md).

## Contribuições

Este projeto é de código aberto e você é encorajado a contribuir para melhorias e novas funcionalidades. Sinta-se à vontade para enviar sugestões, relatar problemas ou enviar pull requests através do [repositório oficial no GitHub](https://github.com/e43b/Kemono-and-Coomer-Downloader/) ou por meio do nosso [Discord](https://discord.gg/TaPhfXawcE)

## Autor

Desenvolvido e mantido por [E43b](https://github.com/e43b), o Kemono and Coomer Downloader visa simplificar o processo de download de posts do Kemono e Coomer, proporcionando uma experiência mais acessível e organizada.

## Suporte

Caso tenha problemas ou encontre bugs, acesse o [Discord](https://discord.gg/TaPhfXawcE).

Caso queira fazer uma doação acesse [link](https://oxapay.com/donate/40874860).

## Links

- Repositório do Projeto: [https://github.com/e43b/Kemono-and-Coomer-Downloader/](https://github.com/e43b/Kemono-and-Coomer-Downloader/)
- Site Kemono: [https://kemono.su/](https://kemono.su/)
- Site Coomer: [https://coomer.su/](https://coomer.su/)

---

Esperamos que esta ferramenta seja útil para você!
