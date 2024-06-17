# Kemono and Coomer Downloader

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

## Funcionalidades

### Página Inicial

A página inicial do projeto apresenta as principais opções disponíveis para facilitar a utilização da ferramenta.

### Baixar Post

Para baixar posts específicos, basta inserir o link do post. Se desejar baixar vários posts, separe os links por vírgula. Exemplo:

```sh
https://kemono.su/patreon/user/133054/post/82477856 , https://coomer.su/fansly/user/285310079517863936/post/614339200069672960 , https://coomer.su/fansly/user/285310079517863936/post/611301068940255234
```

### Baixar Todos os Posts de um Perfil

Insira o link de um perfil do Kemono ou Coomer, e o script iniciará o download de todos os posts que combinam com a configuração do programa para baixar todos os posts de um perfil.

### Baixar DMs

Funciona apenas em perfis do site Kemono, pois o Coomer não possui essa função. Basta colocar o link do perfil, e todas as DMs serão extraídas em `.txt` e salvas na pasta `dm`.

## Configuração

### Configuração de Posts

No modo de configuração de posts, o usuário pode definir algumas opções, como:

- Baixar ou não anexos.
- Baixar vídeos quando disponíveis.
- Salvar informações em um arquivo `.txt`, como título, data de postagem, data de importação e conteúdo.
- Salvar comentários do post no arquivo `.txt`. Para salvar os comentários, a opção de salvar informações deve estar ativada.

### Configuração de Perfil

No modo de configuração de perfil, o usuário pode definir o que deseja baixar dos posts, similar às opções de configuração de posts. O diferencial é que o usuário pode filtrar por posts que tenham ou não tenham imagens, podendo escolher uma ou outra, ou ambas as versões.

Para mais detalhes, consulte a [documentação](https://github.com/e43b/Kemono-and-Coomer-Downloader/blob/main/codept/doc.md).

## Suporte

Caso tenha problemas ou encontre bugs, acesse o [Discord](https://discord.gg/TaPhfXawcE).

Caso queira doar algo em criptomoedas, acesse o [link](https://oxapay.com/donate/40874860).

---

Esperamos que esta ferramenta seja útil para você!
