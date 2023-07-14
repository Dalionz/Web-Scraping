import requests
import bs4
import lxml
from fake_headers import Headers
import json
from time import sleep



def headers():
    headers = Headers(browser='firefox', os='win').generate()
    return headers

def pars_hh(URL):
    response = requests.get(URL, headers=headers()).text
    soup = bs4.BeautifulSoup(response, 'lxml')
    return soup

def get_count_page(soup):
    '''
    Функция для получения количества страниц по данному запросу
    '''
    count_page = soup.find('div', attrs={"class": "pager"}).find_all('span', recursive=False)[-1].find('a').find('span').text
    return int(count_page)

def get_all_link(URL,count_page):
    '''
    Функция создает список, элементами которого являются ссылки на все найденные вакансии
    '''
    link_list = []
    for i in range(count_page+1):
        response = requests.get(f"{URL}&page={i}", headers=headers()).text
        soup = bs4.BeautifulSoup(response, 'lxml')
        link_soup = soup.find_all('a', attrs={'class': 'serp-item__title'})
        for a in link_soup:
            link = a['href']
            link_list.append(link)
    return link_list

def get_json_dict(link_list):
    '''
    Фунция содает словарь для будущего преобразованияего в json-файл
    '''
    data_json = {}
    name_vac = ''
    salary = ''
    name_company = ''
    name_city = ''
    count = 0
    for link in link_list:
        count += 1
        sleep(1)
        response = requests.get(f"{link}", headers=headers()).text
        soup = bs4.BeautifulSoup(response, 'lxml')
        name_vac = soup.find('h1', attrs={'data-qa': 'vacancy-title'}).text
        salary = soup.find('div', attrs={'data-qa': 'vacancy-salary'})
        if salary == None:
            salary = 'Не указана'
        else:
            salary = salary.text
        name_company = soup.find('a', attrs={'data-qa': 'vacancy-company-name'}).text
        name_city = soup.find('p', attrs={'data-qa': 'vacancy-view-location'})
        if name_city == None:
            name_city = ''
            name_city_soup = soup.find('span', attrs={'data-qa': 'vacancy-view-raw-address'})
            for name in name_city_soup:
                name_city = name
                break
        name_city = name_city.text
        data_vac = {
            'vacancy': str(name_vac).replace('\xa0', ''),
            'link': str(link),
            'salary': str(salary).replace('\xa0', ''),
            'company': str(name_company).replace('\xa0', ''),
            'city': str(name_city).replace('\xa0', '')
        }
        data_json[str(count)] = data_vac

    return data_json

def get_json_file(json_dict):
    '''
    Функция создает json-файл из словаря
    '''
    with open("vacancy.json", "w", encoding="utf-8") as outfile:
        json.dump(json_dict, outfile, ensure_ascii=False)


if __name__ == "__main__":
    URL = f'https://spb.hh.ru/search/vacancy?text=Python%2C+Django%2C+Flask&salary=&area=1&area=2'
    soup = pars_hh(URL)
    count_page = get_count_page(soup)
    link_list = get_all_link(URL, count_page)
    json_dict = get_json_dict(link_list)
    get_json_file(json_dict)

