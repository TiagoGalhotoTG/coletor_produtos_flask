# Importa os recursos do Flask
from flask import Flask, render_template, request

# Biblioteca utilizada para acessar páginas da Web
import requests

# Biblioteca utilizada para interpretar o HTML
from bs4 import BeautifulSoup

# Biblioteca utilizada para interpretar dados JSON
import json

# Biblioteca utilizada para controlar o intervalo entre requisições
import time


# Cria a aplicação Flask
app = Flask(__name__)


# ==========================================================
# CONFIGURAÇÕES DO PROJETO
# ==========================================================

# Endereço principal do site
BASE = "https://scrapingsandbox.com"

# Identificação da aplicação durante as requisições
HEADERS = {
    "User-Agent": "Mozilla/5.0 (atividade de web scraping)"
}

# Lista de categorias disponíveis para pesquisa
CATEGORIAS = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports",
    "Books",
    "Toys",
    "Beauty",
    "Automotive",
    "Health",
    "Food & Beverage",
    "Jewelry",
    "Office Supplies",
    "Pet Supplies",
    "Music",
    "Art"
]


# ==========================================================
# FUNÇÃO RESPONSÁVEL POR EXTRAIR OS DADOS DOS PRODUTOS
# ==========================================================

def extrair_produto(id_produto):

    # Monta o endereço da página individual do produto
    url = f"{BASE}/product/{id_produto}"

    try:

        # Realiza a requisição para o site
        resposta = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        # Verifica se conseguimos acessar a página
        if resposta.status_code != 200:
            return None

        # Interpreta o HTML recebido
        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )

        # Procura os dados estruturados em JSON
        tags = soup.find_all(
            ["pre", "code", "script"]
        )

        # Percorre as tags encontradas
        for tag in tags:

            # Extrai o conteúdo textual da tag
            conteudo = tag.get_text(strip=True)

            # Verifica se o conteúdo parece ser um JSON de produto
            if conteudo.startswith("{") and '"sku"' in conteudo.lower():

                try:

                    # Converte o conteúdo JSON em um dicionário Python
                    dados = json.loads(conteudo)

                    # Cria um registro com os dados do produto
                    produto = {
                        "id": dados.get("id", id_produto),
                        "nome": dados.get("title", ""),
                        "fornecedor": dados.get("vendor", ""),
                        "categoria": dados.get("category", ""),
                        "preco": float(dados.get("price", 0)),
                        "avaliacao": float(dados.get("rating", 0)),
                        "sku": dados.get("sku", ""),
                        "link": url
                    }

                    # Retorna os dados extraídos
                    return produto

                except json.JSONDecodeError:
                    pass

        # Retorna None caso não encontre os dados esperados
        return None

    except requests.RequestException as erro:

        # Mostra o erro no terminal
        print(f"Erro no produto {id_produto}: {erro}")

        return None


# ==========================================================
# FUNÇÃO RESPONSÁVEL POR COLETAR OS PRODUTOS
# ==========================================================

def coletar_produtos():

    # Lista que armazenará todos os produtos encontrados
    produtos = []

    # Define a quantidade de produtos que será pesquisada
    total_produtos = 500

    # Define quantos produtos serão processados por lote
    tamanho_lote = 24

    # Percorre os produtos em lotes de 24
    for inicio in range(1, total_produtos + 1, tamanho_lote):

        # Define o último produto do lote atual
        fim = min(inicio + tamanho_lote - 1, total_produtos)

        # Mostra no terminal o progresso da coleta
        print(f"Coletando produtos {inicio} até {fim}")

        # Percorre os produtos do lote atual
        for id_produto in range(inicio, fim + 1):

            # Extrai os dados do produto
            produto = extrair_produto(id_produto)

            # Verifica se o produto foi encontrado
            if produto:

                # Adiciona o produto à lista
                produtos.append(produto)

            # Aguarda antes de realizar a próxima requisição
            time.sleep(0.2)

    # Retorna a lista completa de produtos
    return produtos


# ==========================================================
# FUNÇÃO RESPONSÁVEL POR ANALISAR OS PRODUTOS
# ==========================================================

def analisar_produtos(produtos):

    # Verifica se existem produtos para analisar
    if not produtos:
        return None

    # Localiza o produto com o menor preço
    menor_preco = min(
        produtos,
        key=lambda produto: produto["preco"]
    )

    # Localiza o produto com o maior preço
    maior_preco = max(
        produtos,
        key=lambda produto: produto["preco"]
    )

    # Calcula a média dos preços
    media = sum(
        produto["preco"] for produto in produtos
    ) / len(produtos)

    # Localiza o produto com a melhor avaliação
    melhor_avaliacao = max(
        produtos,
        key=lambda produto: produto["avaliacao"]
    )

    # Cria um dicionário com os resultados da análise
    analise = {
        "quantidade": len(produtos),
        "menor_preco": menor_preco,
        "maior_preco": maior_preco,
        "media": media,
        "melhor_avaliacao": melhor_avaliacao
    }

    # Retorna os resultados
    return analise


# ==========================================================
# PÁGINA INICIAL
# ==========================================================

@app.route("/")
def inicio():

    # Mostra a página que contém o formulário
    # Envia também a lista de categorias disponíveis
    return render_template(
        "index.html",
        categorias=CATEGORIAS
    )


# ==========================================================
# ROTA RESPONSÁVEL PELA PESQUISA
# ==========================================================

@app.route("/pesquisar", methods=["POST"])
def pesquisar():

    # Recebe a categoria escolhida no formulário
    categoria = request.form.get("categoria", "").strip()

    # Verifica se a categoria selecionada é válida
    if categoria not in CATEGORIAS:

        # Retorna uma mensagem de erro ao HTML
        return render_template(
            "resultados.html",
            erro="Categoria inválida.",
            produtos=[],
            analise=None,
            categoria=categoria
        )

    # Coleta os produtos disponíveis no site
    todos_produtos = coletar_produtos()

    # Lista que armazenará somente os produtos da categoria escolhida
    produtos_filtrados = []

    # Percorre todos os produtos coletados
    for produto in todos_produtos:

        # Verifica se o produto pertence à categoria selecionada
        if produto["categoria"].lower() == categoria.lower():

            # Adiciona o produto à lista filtrada
            produtos_filtrados.append(produto)

    # Realiza as análises dos produtos encontrados
    analise = analisar_produtos(produtos_filtrados)

    # Envia os resultados para a página HTML
    return render_template(
        "resultados.html",
        categoria=categoria,
        produtos=produtos_filtrados,
        analise=analise,
        erro=None
    )


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)
