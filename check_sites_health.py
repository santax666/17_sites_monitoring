import requests
import whois
import datetime
import argparse
import os


def create_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s [аргументы]',
                                     description='Мониторинг сайтов'
                                                 ' с помощью %(prog)s')
    parser.add_argument('-f', '--filepath', help='Список с URL-адресами')
    return parser


def load_urls4check(path):
    global urls
    if not os.path.exists(path):
        return None
    urls = open(path, 'r')
    return urls


def close_file_with_urls():
    urls.close()


def send_get_request(url):
    response = requests.get(url, allow_redirects=False)
    return response.status_code


def is_server_respond_with_200(url):
    http_code_ok = 200
    return send_get_request(url) == http_code_ok


def get_domain_expiration_date(url):
    domain = whois.whois(url)
    return domain.expiration_date


def calculate_days_between_dates(expiration_date):
    days_in_month = 31
    now_date = datetime.datetime.today()
    days_count = expiration_date - now_date
    return days_count.days > days_in_month


def output_url_status(url):
    prefix = ('НЕ ', '',)
    out_text = ('сервер {0}отвечает на запрос статусом HTTP 200;',
                'доменное имя сайта {0}проплачено как минимум на '
                '1 месяц вперед.')
    for url in urls:
        url = url.rstrip('\n')
        print('{0}:'.format(url))
        status = is_server_respond_with_200(url)
        print(out_text[0].format(prefix[status]))
        expiration_date = get_domain_expiration_date(url)
        if type(expiration_date) == list:
            expiration_date = expiration_date[0]
        expire_stat = calculate_days_between_dates(expiration_date)
        print(out_text[1].format(prefix[expire_stat]))
        print()

if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    filepath = namespace.filepath

    if filepath is None:
        filepath = input("Введите путь до файла с URL-адресами: ")

    urls = load_urls4check(filepath)
    if urls is not None:
        output_url_status(urls)
        close_file_with_urls()
    else:
        print('Файл с URL-адресами не найден!')
