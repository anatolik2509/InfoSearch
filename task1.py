from bs4 import BeautifulSoup
import requests as req

api_endpoint = 'https://ru.wikipedia.org/w/api.php'
wiki_url = 'https://ru.wikipedia.org'
Soviet_film_directors_url = wiki_url + '/wiki/Категория:Кинорежиссёры_СССР'

index = open('index.txt', 'w')

page = req.get(Soviet_film_directors_url)

soup = BeautifulSoup(page.content, 'html.parser')

table = soup.find(id='mw-pages')

count = 1


def get_page(title):
    resp = req.get(
        api_endpoint,
        params={
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts',
            'explaintext': True,
        }).json()
    return next(iter(resp['query']['pages'].values()))['extract']


print('Download started')


for a in table.find_all('a', href=True):
    page_title = a['title']
    page_url = wiki_url + a['href']
    page = get_page(page_title)
    with open('plain_pages/' + str(count) + '.txt', 'w', encoding="utf-8") as out:
        out.write(page)
        out.close()
        print(str(count))
        index.write(str(count) + '\t' + page_url + '\n')
    count += 1

index.close()
