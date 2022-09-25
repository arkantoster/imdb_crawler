# RECUPERACAO DA INFORMACAO NA WEB E EM REDES SOCIAIS

Esse repositório é para demonstrar as habilidades e conhecimentos adquiridos na matéria de Recuperacao da Informacao na Web e em Redes Sociais.
Os pacotes utilizados foram:

- scrapy
Utilizado para raspagem de dados no IMDB
- jsonlines
Utilizado para fazer a leitura do arquivo exportado com os dados da raspagem
- stop-words
Utilizado como biblioteca para "palavras de parada"
- wordcloud
Utilizado gerar a nuvem de palavras

## Como rodar?

O projeto foi feito em duas partes. A primeira é a raspagem de dados, a segunda é gerar a nuvem de palavras.

### Raspagem de Dados

Para rodar, rode o seguinte comando:

    scrapy crawl movie_data -O imdbTop.jl

O comando irá rodar o crawler `movie_data` e irá exportar o resultado em `imdbTop.jl`

### Nuvem de palavras

Para gerar a nuvem de palavras, rode o seguinte comando:

    python3 ./cloudWords/wordcloud_builder.py

O comando irá gerar a nuvem, e exibi-lá.
