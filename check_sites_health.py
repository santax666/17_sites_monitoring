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
    if not os.path.exists(path):
        return None
    with open(path, 'r') as urls_list:
        return urls_list.read().splitlines()


def check_http_code(url):
    TIME_WAIT_FOR_RESPONSE = 10
    HTTP_SERVER_ERROR = 503
    http_codes = [list(range(200, 227)), list(range(300, 308)), [401, 407],
                  [403], [404], list(range(400, 452)), [500], [503],
                  list(range(501, 512)), list(range(100, 103))]
    try:
        code = requests.get(url, allow_redirects=False,
                            timeout=TIME_WAIT_FOR_RESPONSE).status_code
    except requests.exceptions.Timeout:
        code = HTTP_SERVER_ERROR
    return next(i for i, x in enumerate(http_codes) if code in x)


def check_expiration_date(url):
    DAYS_IN_MONTH = 31
    now_date = datetime.datetime.today()
    expire_date = whois.whois(url).expiration_date
    if expire_date is None:
        return False
    if type(expire_date) == list:
        expire_date = expire_date[0]
    days_count = expire_date - now_date
    return not days_count.days > DAYS_IN_MONTH


def check_sites_status(urls_list):
    success_state = ('FAIL:', 'OK',)
    errors_msg = ('Окончание регистрации домена произойдет в течение месяца',
                  '(3xx): Запросы для сайта перенаправлены на другой URL',
                  'Для получения страницы требуются данные авторизации',
                  '(403): Страница не предназначена для публичного просмотра',
                  '(404): Запрошенная страница не найдена на сервере сайта',
                  '(4xx): По указанной странице сервер вернул ошибку запроса',
                  '(500): Внутренняя ошибка сервера, ожидайте исправления',
                  '(503): Сервер не может обрабатать запрос по тех. причинам',
                  '(5xx): Неудачное выполнение запроса по вине сервера',
                  '(1xx): Возвращен код, информирующий о процессе передачи')
    for url in urls_list:
        http_state = check_http_code(url)
        expire_state = check_expiration_date(url)
        if (http_state or expire_state):
            print('{0} - {1}'.format(url, success_state[False]))
            if expire_state:
                print(errors_msg[0])
            if http_state:
                print(errors_msg[http_state])
        else:
            print('{0} - {1}'.format(url, success_state[True]))


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    filepath = namespace.filepath
    if filepath is None:
        filepath = input('Введите путь до файла с URL-адресами: ')
    urls_list = load_urls4check(filepath)
    if urls_list is not None:
        check_sites_status(urls_list)
    else:
        print('URL-адреса в указанном файле не найдены!')
