import bs4
import requests
from user_agent import generate_navigator
from db.db_func import FuncDB
import dateparser as dp
import regex as re

func_db = FuncDB()
HEADERS = generate_navigator()


def get_news(url: str, headers=None):
    """
    Функция парсит ссылку переданную пользователем. В ручную необходимо передать уникальные классы для конкретного
    ресурса. Забирает тэги и уникальные классы в таблицу resource.

    :params url: str - ссылка на ресурс
    :params headers: dict - псевдо-данные о браузере (по-умолчанию None)
    """
    if not func_db.resource_in_db(url):
        response = requests.get(url, headers=headers).text

        soup = bs4.BeautifulSoup(response, features='lxml')
        title = soup.title.text

        # Структура для взятия ссылок на новости
        top_tag = soup.find('a', class_='js-article-link')

        link = top_tag.attrs['href']
        if link[:4] != 'http':
            link = url + top_tag.attrs['href']

        news_text = requests.get(url=link).text
        soup_news = bs4.BeautifulSoup(news_text, 'lxml')

        # структуру для взятия заголовка новости
        title_cut = soup_news.find('h1', class_='js-main-headline')

        # структуру для взятия  даты и времени новости
        date_cut = soup_news.find('time', class_='datetime--publication')

        # Структура для взятия текстового контента на новости
        bottom_tag_soup = soup_news.find('div', class_='io-article-body')

        bottom_tag = f"<{bottom_tag_soup.name} class={''.join(bottom_tag_soup.attrs['class'])}>"
        top_tag = f"<{top_tag.name} class={''.join(top_tag.attrs['class'])}>"
        date_cut = f"<{date_cut.name} class={''.join(date_cut.attrs['class'])}>"
        title_cut = f"<{title_cut.name} class={''.join(title_cut.attrs['class'])}>"

        func_db.add_new_resource(url, title=title,
                                 top_tag=str(top_tag),
                                 bottom_tag=str(bottom_tag),
                                 title_cut=str(title_cut),
                                 date_cut=str(date_cut))


def add_news(resource_id, headers):
    """
    Функция парсит все ссылки на странице ресурса из таблицы resoucrse с помощью тэгов и уникальных классов
    в таблице recourse.

    :params resource_id: int - Идентификатор ресурса в таблице resourse
    :params headers: dict - псевдо-данные о браузере (по-умолчанию None)
    """
    resource_info = func_db.get_resource(resource_id)
    pattern_tag = r"(?<=\<)(\w{0,200}\d{0,10}(?=[\s>]))"
    pattern_class = r"(?<=class=).{0,200}(?=>)"

    response = requests.get(resource_info['url'], headers=headers).text
    soup = bs4.BeautifulSoup(response, features='lxml')

    links = soup.find_all(re.search(pattern_tag, resource_info['top_tag']).group(0),
                          class_=re.search(pattern_class, resource_info['top_tag']).group(0))

    for tag in links:
        link = tag.attrs['href']
        if link[:4] != 'http':
            link = resource_info['url'] + link

        if not func_db.news_in_db(resource_id, link):

            resp = requests.get(link, headers=HEADERS).text
            soup_news = bs4.BeautifulSoup(resp, features='lxml')

            title = soup_news.find(re.search(pattern_tag, resource_info['title_cut']).group(0),
                                   class_=re.search(pattern_class, resource_info['title_cut']).group(0))

            if not title:
                continue

            date = soup_news.find(re.search(pattern_tag, resource_info['date_cut']).group(0),
                                  class_=re.search(pattern_class, resource_info['date_cut']).group(0))

            if date.attrs.get('datetime'):
                not_date = str(dp.parse(date.attrs['datetime']).date())
                nd_date = int(dp.parse(date.attrs['datetime']).timestamp())
            elif date.text and len(date.text) > 0:
                not_date = str(dp.parse(date.text).date())
                nd_date = int(dp.parse(date.text).timestamp())

            content = soup_news.find(re.search(pattern_tag, resource_info['bottom_tag']).group(0),
                                     class_=re.search(pattern_class, resource_info['bottom_tag']).group(0))

            func_db.add_new_news(
                resource_id=resource_id,
                link=link,
                title=title.text.strip(),
                content=content.text.strip(),
                nd_date=nd_date,
                not_date=not_date
            )


if __name__ == "__main__":
    # news_info = get_news("https://www.nur.kz", HEADERS)
    add_news(7, headers=HEADERS)
    func_db.close()
