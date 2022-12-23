import requests #HTTP library for Python
from bs4 import BeautifulSoup #Python library for pulling data out of HTML and XML files
import re #This module provides regular expression matching operations similar to those found
from lxml import html #The lxml XML toolkit is a Pythonic binding for the C libraries libxml2 and libxslt
import os
import json
# establishing session
s = requests.Session()
s.headers.update({
        'cookie': 'desktop_session_key=46ab9bc4fcc7775af3fa59308ca02b93aca618916c6b58f01f65ebb86b4f6ed9b11dd800af2c5efb6e128c7161997461276b1963aaa6f640ef48091d8012bae9e17830373bb99c8fa03013ab1a1185381bd1012bf30c04f4d890bbef6c9e4ad1; desktop_session_key.sig=liNbo55k91nhTwAXFxWJ3Jw9jjs; yandexuid=3102365891664885173; location=1; _csrf=WhNix-QDN5uMs7tRx9vBN1bO; PHPSESSID=299f5c8cd329629e0ae099995e9d99ba; yandex_gid=66; uid=107997733; _csrf_csrf_token=Fm8FMWt-K8AK6UWqM3rmnVljPrvjxkiWguL8anAXRP0; my_perpages=%5B%5D; mustsee_sort_v5=01.10.200.21.31.41.121.131.51.61.71.81.91.101.111; mda_exp_enabled=1; user-geo-region-id=66; user-geo-country-id=2; mykp_button=movies; hideBlocks=393216; i=XCp1cYBaEM6lkeHxSTXj4L1UK+DUyNP7zkdLkS1k39ZzKtK8YurwNAyQzo785f5ib+be/rykBw/B28l1tduPt0WJubM=; _ym_uid=1663047690533907655; last_visit_friend_lenta=2022-11-09+22%3A14%3A00; yandex_login=valyanazarova2002; crookie=2vbk3SKLukQ5eYel3VwhAeT5yMg+VXG3BcDrDD1l2jzSRbosK8NE/iTBTKGyRAJSWlonRVySZvMiIMVGGMRJs+fkwk4=; cmtchd=MTY2ODgwMDQ1NTY0NQ==; mobile=no; _yasc=1s0NbUa24TE1U3tpqr9w42EAsP8qFG2DDeltine2zR6qHl7W3WhbfTBBxZRD; tc=462; user_country=ru; ya_sess_id=3:1669313998.5.0.1668181057834:fAPWsA:25.1.2:1|1598970492.0.2|30:10211868.473587.8cAPv4ZS0duYTmKVj_1PfiW6Jns; ys=c_chck.1972328011#udn.cDp2YWx5YW5hemFyb3ZhMjAwMg%3D%3D; mda2_beacon=1669313998801; sso_status=sso.passport.yandex.ru:synchronized; yandex_plus_metrika_cookie=true; _ym_d=1669318378',
        'Referer': 'https://www.kinopoisk.ru/user/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    })
def create_dir(path):
    if os.path.exists(path):
        return
    else:
        os.mkdir(path)

create_dir("./user_data")
create_dir("./pages")

def load_user_data(user_id, page, session): #загрузка данных странницы
    url = 'http://www.kinopoisk.ru/user/%d/votes/list/ord/date/page/%d/#list' % (user_id, page)
    request = session.get(url, timeout=(3.05, 27))
    return request.text

def contain_movies_data(text):
    soup = BeautifulSoup(text, features="lxml")
    film_list = soup.find_all('div', class_='profileFilmsList') #в этом теге лежит весь список, проверяем его наличие
    return film_list is not None

# loading files
page = 1 #список фильмов в нескольких страницах
user_id = 44342982 #контретный пользователь
#пролистываем все страницы списка
while page<3: #<3 ограничение количества страниц для теста,
    data = load_user_data(user_id, page, s)
    if contain_movies_data(data):
        with open('./pages/page_%d.html' % (page), 'w', encoding="utf-8") as output_file: #читаем
            output_file.write(data) #записываем эту странницу в свой файл
            page += 1
    else:
            break

def read_file(filename):
    with open(filename, 'r', encoding="utf-8") as input_file:
        text = input_file.read()
    return text

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


results = []
for filename in os.listdir('./pages/'):
    results.extend(parse_user_datafile_lxml('./pages/' + filename))
with open('./user_data/user%d_data.json' % (user_id), 'w') as user_json_data:
    user_json_data.write(json.dumps(results))