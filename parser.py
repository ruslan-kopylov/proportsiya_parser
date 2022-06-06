import csv
from time import sleep

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests



URL_BASE = 'https://proportsiya.by/menu/'
HEADERS_FOR_FILE = [
    'РАЦИОН', 'ПРИЁМ', 'НАЗВАНИЕ', 'ВЕС', 'ККАЛ', 'БЕЛКИ', 'ЖИРЫ',
    'УГЛЕВОДЫ', 'СОСТАВ', 'СЕРВИРОВКА', 'URL']


def get_main_page(url):
    """Функция нужна, чтобы получить первую страницу и основные данные"""
    with open(file='data.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                HEADERS_FOR_FILE
            )
        )
    ua = UserAgent()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User-Agent': ua.random
    }
    s = requests.Session()
    response = s.get(url=url, headers=headers)

    with open('index.html', 'w') as file:
        file.write(response.text)


def parsing_main_page():
    """Вытащили с первой страницы ссылки на все меню"""
    with open('index.html') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    all_menu = soup.find('section', class_='pt-50 pb-50 bg-l-gray').find_all('a')
    menu_urls = []
    for menu in all_menu:
        url = menu.get('href')
        menu_urls.append(url)
    return menu_urls


def get_pages(urls):
    """Скачиваем все страницы и загоняем каждую в парсер"""
    for index, url in enumerate(urls):
        temp = url.split('/')[::-1][1]
        urls[index] = f'{URL_BASE}{temp}/'
    for index, url in enumerate(urls):
        for day in range(1, 22):
            new_url = url+str(day)
            sleep(4)
            parsing(new_url)
            print(f'Обработано {day} дней')
        print(f'Меню номер {index} обработано')
            #response = s.get(url=new_url, headers=headers)


def parsing(url=''):
    """Собираем данные по меню с конкретной страницы"""
    ua = UserAgent()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User-Agent': ua.random,
    }
    s = requests.Session()
    response = s.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    name_menu = soup.find('section', class_='pt-80 pb-50').find(
        'h2', class_='section-title').text.split()[2]
    intakes = soup.find_all('div', class_='intake')
    for intake in intakes:
        course_time = intake.find('h4').text.split()[1]
        course_id = intake.find('a', class_='btn-show-course-card').get('course-id')
        heads = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        response = s.post('https://proportsiya.by/ajax/get_course_card', headers=heads, data=f"course_id={course_id}")
        course_name = response.json()['course']['name']
        weight = response.json()['course']['weight']
        composition = response.json()['course']['composition']
        calorie = response.json()['course']['calorie']
        protein = response.json()['course']['protein']
        carbohyd = response.json()['course']['carbohyd']
        fat = response.json()['course']['fat']
        course_serve = response.json()['course']['serve']['name']
        with open (file='data.csv', mode='a') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    name_menu, course_time, course_name, weight, calorie,
                    protein, fat, carbohyd, composition, course_serve, url
                )
            )


def main():
    get_main_page(URL_BASE)
    urls = parsing_main_page()
    get_pages(urls)


if __name__ == '__main__':
    main()

