from datetime import datetime

import requests
from bs4 import BeautifulSoup

import schedule


url = 'https://micom.kz/'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 RuxitSynthetic/1.0 v3975717906 t6703941201591042144 athfa3c3975 altpub cvcv=2 smf=0"
}


def get_data():
    req = requests.get(url=url, headers=headers)
    req.encoding = 'UTF8'
    src = req.text
    soup = BeautifulSoup(src, 'lxml')

    # Сбор всех ссылок на каталоги
    categories_li_1 = soup.find('ul', class_='menu').find_all('li')
    test_dict_catalog = []
    for li_1 in categories_li_1:
        test_dict_catalog.append(li_1.find('a').get('href'))

    dict_catalog = []
    for a in test_dict_catalog:
        try:
            int(a[-7:])
            dict_catalog.append(a)

        except Exception as ex:
            print(ex)

    dict_catalog.append(test_dict_catalog[-3])
    dict_catalog.append(test_dict_catalog[-2])
    dict_catalog.append(test_dict_catalog[-1])

    # Сбор всех карточек в каталоге
    list_cards = []
    list_url = []
    for url_catalog in dict_catalog:
        page = 1
        while True:
            print(f'{url_catalog}&limit=25&page={page}')
            req1 = requests.get(url=f'{url_catalog}&limit=50&page={page}', headers=headers)
            req1.encoding = 'UTF8'
            src1 = req1.text
            soup1 = BeautifulSoup(src1, 'lxml')

            if len(soup1.find_all('a', class_='btn')) == 1:
                print('!')
                break

            else:
                all_cards = soup1.find_all('div', class_='product-layout product-list col-xs-12')
                count_page = 0
                for card in all_cards:
                    count_page += 1
                    name_product = card.find('div', class_='name name-product').text.strip()
                    url_product = card.find('div', class_='name name-product').find('a').get('href')

                    if len(card.find('div', class_='price price-product').find_all('span')) == 1:
                        price = card.find('div', class_='price price-product').text.split('тг.')[0].strip()
                    else:
                        price = card.find('span', class_='price-new').text.split('тг.')[0].strip()

                    # print(f'{name_product} - {price}')
                    article_num = card.find('div', class_='caption').find_all('p')[1].find('span').text

                    list_atr = [name_product, article_num, price]

                    # print(list_atr)
                    # print(list_cards)

                    if list_atr not in list_cards:
                        list_cards.append(list_atr)
                        list_url.append(url_product)

            page += 1

    finish_list = [["Название", "Артикул", "Цена", "Ссылка"]]
    n = 0
    for card_3 in list_cards:
        card_3.append(list_url[n])
        finish_list.append(card_3)
        n += 1

    # print(len(finish_list))
    # for x in finish_list:
    #     print(x)
    google_table(dict_cards=finish_list)


def google_table(dict_cards):
    import os.path

    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # mail bot 'parsers@parsers-372008.iam.gserviceaccount.com'
    SAMPLE_SPREADSHEET_ID = '107SdHe8_dV6npe_dKE-7xA2QJgxz6ZOywOy-GZyrZX0'
    SAMPLE_RANGE_NAME = 'micom.kz'

    try:
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        # Чистим(удаляет) весь лист
        array_clear = {}
        clear_table = service.clear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,
                                    body=array_clear).execute()

        # добавляет информации
        array = {'values': dict_cards}
        response = service.append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                  range=SAMPLE_RANGE_NAME,
                                  valueInputOption='USER_ENTERED',
                                  insertDataOption='OVERWRITE',
                                  body=array).execute()

    except HttpError as err:
        print(err)


def main():
    start_time = datetime.now()

    schedule.every(57).minutes.do(get_data)
    while True:
        schedule.run_pending()

    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)


if __name__ == '__main__':
    main()
