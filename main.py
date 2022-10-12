import bs4
import requests
from user_agent import generate_navigator
from db.db_func import FuncDB
import dateparser as dp

func_db = FuncDB()
HEADERS = generate_navigator()


def get_news(url: str, headers=None) -> dict:
    """
    Функция парсит ссылку переданную пользователем, забирает все ссылки с указанного ресурса имеющие в названии
    больше трех дифисов. Возвращает cловарь с информацией о ресурсе.

    :params url: str - ссылка на ресурс
    :params headers: dict - псевдо-данные о браузере (по-умолчанию None)

    :return news_inform: dict  {
        'res_url': url, - ссылка на ресурс
        'res_id': res_id, - идентификаионный номер ресурса в БД
        'res_title': res_title, - название ресурса
        'news': news_list - список из статей на этом ресурсе
    }

    """
    response = requests.get(url, headers=headers).text

    soup = bs4.BeautifulSoup(response, features='html.parser')
    res_title = soup.find('title').text

    if not func_db.resource_in_db(url):
        func_db.add_new_resource(url, res_title)

    res_id = func_db.get_id_resource(res_title)

    news = soup.find_all('a')
    news_list = []
    for new in news:
        link = new.get('href')
        if link[:4] != 'http':
            link = url + link
        if link.count('-') > 3:
            news_list.append(link)

    news_inform = {
        'res_url': url,
        'res_id': res_id,
        'res_title': res_title,
        'news': news_list
    }

    return news_inform


def get_info_news(news_inform: dict, headers=None) -> str:
    """
    Функция принимает словарь с данными о ресурсе и ссылками на все статьи этого ресурса. Парсит каждую ссылку,
    обрабатывает информацию о каждой статье и заносит данные в БД, если данных еще нет в БД.

    :params news_inform: dict - словарь с данными о ресурсе. Ожидает:
    {
        'res_url': url, - ссылка на ресурс
        'res_id': res_id, - идентификаионный номер ресурса в БД
        'res_title': res_title, - название ресурса
        'news': news_list - список из статей на этом ресурсе
    }

    :params headers: dict - псевдо-данные о браузере (по-умолчанию None)

    :return: str - f'successful'
    """

    resource_id = news_inform['res_id']

    for news in news_inform['news']:

        if not func_db.news_in_db(resource_id, news):

            response = requests.get(news, headers=headers).text

            soup = bs4.BeautifulSoup(response, features='html.parser')

            title = soup.find('h1').contents[0]
            paragraphs = soup.find_all('p')
            content = []
            news_date = soup.find_all('time')
            for date in news_date:
                if date.attrs.get('datetime'):
                    not_date = str(dp.parse(date.attrs['datetime']).date())
                    nd_date = int(dp.parse(date.attrs['datetime']).timestamp())
                    break
                elif date.text and len(date.text) > 0:
                    not_date = str(dp.parse(date.text).date())
                    nd_date = int(dp.parse(date.text).timestamp())
                    break

            for paragraph in paragraphs:
                content.append(paragraph.text)

            func_db.add_new_news(
                resource_id=resource_id,
                link=news,
                title=title,
                content='\n'.join(content),
                nd_date=nd_date,
                not_date=not_date
            )

    return f'successful'


if __name__ == "__main__":
    news_info = get_news("https://tengrinews.kz", HEADERS)
    get_info_news(news_info, HEADERS)
    func_db.close()
