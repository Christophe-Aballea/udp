import requests
import time
import xlsxwriter
from bs4 import BeautifulSoup

url = 'https://www.luniversdupneu.com'
url_departement = []
balises = {'Marque': ['span', 'product_manufacturer'],
           'Pneu': ['span', 'product_name'],
           'Référence': ['span', 'product_referance'],
           'Catégorie': ['div', 'product-category'],
           'Consommation': ['span', 'picto-carburant'],
           'Adhérence': ['span', 'picto-adherence'],
           'Bruit': ['span', 'picto-bruit'],
           'Disponibilité': ['span', 'd-block product-message'],
           'Prix': ['span', 'price']}


HEADERS = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
           'accept-language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'}

response = requests.get(url, headers=HEADERS)

print("Recherche départements : ", end='')
if response:
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        departement = soup.findAll('div', {'class': 'flip_link'})

        for dept in departement:
            url_dept = dept.a['href']
            if url_dept not in url_departement:
                url_departement.append(url_dept)
        print("Ok")
    except:
        print(f"{url} en maintenance, indisponible ou IP bannie.")
else:
    print("Problème inconnu.")
    exit()

for url in url_departement:
    dept = url[-3:-1]
    print()
    print(f"Département : {url}")
    print("Recherche catégories : ", end='')
    response = requests.get(url, headers=HEADERS)
    if response:
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            url_category = []
            urls = soup.findAll('li', {'class': 'category'})
            for url in urls:
                url_category.append(url.find('a', {'class': 'dropdown-item'})['href'])
            print("Ok")
            try:
                pneu = [['Marque',
                         'Pneu',
                         'Référence',
                         'Catégorie',
                         'Consommation',
                         'Adhérence',
                         'Bruit',
                         'Disponibilité',
                         'Prix']]
                for url in url_category:
                    i = 0
                    category = url.split('/')[-1]
                    print(f"Catégorie : {category}")
                    url_base = url
                    while True:
                        if i > 0:
                            url = url_base + "?page=" + str(i + 1)
                        page = requests.get(url, headers=HEADERS)

                        if page:
                            if i == 0 and "Veuillez nous excuser pour le désagrément." in page.text:
                                print("Rien à scraper ici.")
                                break
                            elif "Veuillez nous excuser pour le désagrément." not in page.text:
                                print(f"Page {i + 1} : ", end='')
                                articles = BeautifulSoup(page.text, 'lxml')
                                items = articles.find('div', {"class": "products clear display_list"}).findAll(
                                    'article')
                                field = pneu[0]
                                for x in items:
                                    p = []
                                    for f in field:
                                        bal, cl = balises[f][0], balises[f][1]
                                        try:
                                            value = x.find(bal, {'class': cl}).text.strip()
                                            if f == 'Prix':
                                                value = float(value[:-2].replace(',', '.'))
                                            p.append(value)
                                        except:
                                            p.append("")
                                    pneu.append(p)
                                i += 1
                                print(f"{len(items)} articles scrapés.")
                            else:
                                break
                        else:
                            break
            except:
                print(f"Impossible de scraper {category}")
        except:
            print(f"{url} en maintenance, indisponible ou IP bannie.")

        filename = 'udp_' + time.strftime('%y.%d.%m-%H.%M.%S') + '_' + dept.upper() + '.xlsx'
        print(f"Enregistrement {filename} : ", end='')
        try:
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet("Catalogue internet UDP " + dept.upper())
            row = 0
            col = 0
            for i, row in enumerate(pneu):
                for j, data in enumerate(row):
                    worksheet.write(i, j, data)
            workbook.close()
            print("Ok")
        except:
            print(f"Impossible.")
    else:
        print("Problème inconnu")

