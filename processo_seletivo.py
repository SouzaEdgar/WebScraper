from bs4 import BeautifulSoup as bs
import requests
import json

url = 'https://storage.googleapis.com/infosimples-public/commercia/case/product.html'

resposta_final = {}

response = requests.get(url)

parsed_html = bs(response.content, 'html.parser')

# Title
resposta_final['title'] = parsed_html.select_one('h2#product_title').getText()

# Brand
resposta_final['brand'] = parsed_html.select_one('div.brand').getText()

# Categories
resposta_final['categories'] = []
for a in parsed_html.select('nav.current-category > a'):
    resposta_final['categories'].append(a.getText())

# Description
resposta_final['description'] = parsed_html.select_one('div.product-details > p').getText().strip().replace("\n            ","")

# Skus
resposta_final['skus'] = []
for i in parsed_html.select('div.skus-area > div > div'):
    # Nome
    name = i.select_one('div.sku-name').getText().strip()

    # Preço atual
    if i.select_one('div.sku-current-price'):
        current = i.select_one('div.sku-current-price').getText().strip()
        current = float(current.replace("$ ",""))
    else:
        current = None
    
    # Preço antigo
    if i.select_one('div.sku-old-price'):
        old = i.select_one('div.sku-old-price').getText().strip()
        old = float(old.replace("$ ",""))
    else:
        old = None
    
    # Disponivel
    if i.select_one('i'):
        available = False
    else:
        available = True
    
    prod = [name, current, old, available]
    resposta_final['skus'].append(prod)

# Properties
resposta_final['properties'] = []
n = 0
for j in parsed_html.select('table.pure-table'):
    n+=1
    if n == 1: # Primeira tabela de propriedades
        for k in j.select('td'):
            if k.select_one('b'):
                lbl = k.select_one('b').getText() # label
            else:
                value = k.getText()
                # O append esta dentro do else para que a Label e Value sejam inseridas juntas
                # visto que primeiro vem a Label ('b') e depois o text ('td') no arquivo
                prop = [lbl, value]
                resposta_final['properties'].append(prop)

# Reviews
resposta_final['reviews'] = []
for m in parsed_html.select('div#comments > div.review-box'):
    name = m.select_one('span.review-username').getText()
    date = m.select_one('span.review-date').getText()
    score = m.select_one('span.review-stars').getText().count("★") #Unicode U+2605
    text = m.select_one('p').getText()

    review = [name, date, score, text]
    resposta_final['reviews'].append(review)

# Reviews_Average_Score
ras = parsed_html.select_one('div#comments > h4').getText()

barra = ras.find("/")    # Localizar a posição da / (que divide a média do total)
espaço = ras.find(": ")  # Localizar os : pois é após eles que vem os numeros
                         # +1 para pegar a posição depois do ": " que é onde inicia o numero desejado
resposta_final['reviews_average_score'] = float(ras[espaço+1:barra])

# URL
# Não consegui entender muito bem como esta parte deveria ser feita
# Fiquei em duvida se eu deveria encontrar a URL de forma automatica ou manual

#resposta_final['url'] = parsed_html.find(itemprop='url').get('href', str)
resposta_final['url'] = url

# Json
json_resposta_final = json.dumps(resposta_final, ensure_ascii=False) ## Arrumar a acentuação
with open('produto.json', 'w') as arquivo_json:
    arquivo_json.write(json_resposta_final)
