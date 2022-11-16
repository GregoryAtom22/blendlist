import requests #HTTP library for Python
from bs4 import BeautifulSoup #Python library for pulling data out of HTML and XML files
import re #This module provides regular expression matching operations similar to those found
from lxml import html #The lxml XML toolkit is a Pythonic binding for the C libraries libxml2 and libxslt
# establishing session
s = requests.Session()
s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    })

def load_user_data(user_id, page, session): #загрузка данных странницы
    url = 'http://www.kinopoisk.ru/user/%d/votes/list/ord/date/page/%d/#list' % (user_id, page)
    request = session.get(url)
    return request.text

def contain_movies_data(text):
    soup = BeautifulSoup(text, features="lxml")
    film_list = soup.find_all('div', class_='profileFilmsList') #в этом теге лежит весь список, проверяем его наличие
    return film_list is not None

# loading files
page = 1 #список фильмов в нескольких страницах
user_id = 44342982 #контретны пользователь
#пролистываем все страницы списка
while page<3: #<3 ограничение количества страниц для теста,
    data = load_user_data(user_id, page, s)
    if contain_movies_data(data):
        with open('./pages/page_%d.html' % (page), 'w', encoding="iso-8859-1") as output_file: #читаем
            output_file.write(data) #записываем эту странницу в свой файл
            page += 1
    else:
            break

def read_file(filename):
    with open(filename) as input_file:
        text = input_file.read()
    return text

def parse_user_datafile_bs(filename):
    results = []
    text = read_file(filename)

    soup = BeautifulSoup(text)
    film_list = film_list = soup.find('div', class_='profileFilmsList')
    items = film_list.find_all('div', class_=['item', 'item even']) #не уверена надо проверять
    for item in items:
        # getting movie_id
        movie_link = item.find('div', class_='nameRus').find('a').get('href')
        movie_desc = item.find('div', class_='nameRus').find('a').text
        movie_id = re.findall('\d+', movie_link)[0]

        # getting english name
        name_eng = item.find('div', class_='nameEng').text

        #getting watch time
        watch_datetime = item.find('div', class_='date').text
        date_watched, time_watched = re.match('(\d{2}\.\d{2}\.\d{4}), (\d{2}:\d{2})', watch_datetime).groups()

        # getting user rating
        user_rating = item.find('div', class_='vote').text
        if user_rating:
            user_rating = int(user_rating)

        results.append({
                'movie_id': movie_id,
                'name_eng': name_eng,
                'date_watched': date_watched,
                'time_watched': time_watched,
                'user_rating': user_rating,
                'movie_desc': movie_desc
            })
    return results

def parse_user_datafile_lxml(filename):
    results = []
    text = read_file(filename)

    tree = html.fromstring(text)

    film_list_lxml = tree.xpath('//div[@class = "profileFilmsList"]')[0]
    items_lxml = film_list_lxml.xpath('//div[@class = "item even" or @class = "item"]')
    for item_lxml in items_lxml:
        # getting movie id
        movie_link = item_lxml.xpath('.//div[@class = "nameRus"]/a/@href')[0]
        movie_desc = item_lxml.xpath('.//div[@class = "nameRus"]/a/text()')[0]
        movie_id = re.findall('\d+', movie_link)[0]

        # getting english name
        name_eng = item_lxml.xpath('.//div[@class = "nameEng"]/text()')[0]

        # getting watch time
        watch_datetime = item_lxml.xpath('.//div[@class = "date"]/text()')[0]
        date_watched, time_watched = re.match('(\d{2}\.\d{2}\.\d{4}), (\d{2}:\d{2})', watch_datetime).groups()

        # getting user rating
        user_rating = item_lxml.xpath('.//div[@class = "vote"]/text()')
        if user_rating:
            user_rating = int(user_rating[0])

        results.append({
                'movie_id': movie_id,
                'name_eng': name_eng,
                'date_watched': date_watched,
                'time_watched': time_watched,
                'user_rating': user_rating,
                'movie_desc': movie_desc
            })
    return results