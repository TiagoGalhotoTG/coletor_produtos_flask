# Teste de ambiente Python.

# Importa a blioteca flask, utilizada para criar aplicações web com Python
import flask 

# Importa a blioteca requests, utilizada para fazer requisições HTTP, e 
# acessar informações de sites e APIs
import requests

# Importa a biblioteca BeautifulSoup4, utilizada para analisar e extrair 
# informações de documentos HTML e XML.
import bs4


#Exibe a versão das bibliotecas instaladas, para verificar se o ambiente 
# está configurado corretamente.

print("Ambiente configurado com sucesso!")
print("Flask instalado:", flask.__version__)
print("Requests instalado:", requests.__version__)
print("BeautifulSoup4 instalado:", bs4.__version__)
