import vk_api
import sys
import configparser
from re import sub, findall
import csv

def captcha_handler(captcha):
    key = input("Enter Captcha {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)

def read_users():
    users_list = []
    #f=open('users.txt', 'r')
    f=open('users_test.txt', 'r')
    for line in f:
        users_list.append(line.strip())
    f.close
    return users_list

def write_info(data):
    with open('result.txt', 'w', encoding='utf8') as f:
        f.write(data)

def write_phones(data):
    with open('phones_format.txt', 'w', encoding='cp1251') as f:
        f.write(data)

def read_phones():
    phones_list = []
    #f=open('users.txt', 'r')
    f=open('phones.txt', 'r', encoding='windows-1251')
    for line in f:
        phones_list.append(line.strip())
    f.close
    return phones_list

def norm_mob(str):
    if len(str) != '':
        norm_mob = sub(r'(\D+)?', '', str)
        # проверяем строку на наличие в ней только необходимых символов
        right_mob = findall(r'[\d]', norm_mob)
        # если количество знаков в двух строках совпадает, значит это номер телефона
        if (len(right_mob) == len(norm_mob)) and (len(norm_mob) >= 10):
            rev_norm_mob = norm_mob[::-1]
            norm_mob = rev_norm_mob[0:10]
            return "+7"+norm_mob[::-1]
    else:
        return None

def get_phones(users_str, vk_session):
    users_str = users_str[:-1]
    vk = vk_session.get_api()
    response = vk.users.get(user_ids=users_str,fields='contacts')
    parsed = ''
    for user in response:
        if user.get('mobile_phone'):
            parsed = parsed + str(user.get('id')) + ';' \
                    + str(user.get('first_name')) + ';' \
                    + str(user.get('last_name')) + ';' \
                    + str(user.get('mobile_phone')) + ';' + '\n'
        if user.get('home_phone'):
            parsed = parsed + str(user.get('id')) + ';'\
                    + str(user.get('first_name')) + ';' \
                    + str(user.get('last_name')) + ';' \
                    + str(user.get('home_phone')) + ';' + '\n'
    return parsed

def main():
    #Валидатор номеров, пока обрывком,
    #ТОДО: сделать в отдельную функцию, завязать на csv
    if 1==1:
        data = ''
        phones_list = read_phones()
        for phone in phones_list:
            #print(phone)
            if norm_mob(phone):
                #print(norm_mob(phone))
                data = data + norm_mob(phone) + '\n'
            #else: print('-----------')
            write_phones(data)
            print('write_phones success')
        sys.exit()

    parsed = []
    users = []
    users_str = ''
    #Загружаем ИД юзеров
    users_list = read_users()
    # Загружаем конфиг
    conf = configparser.RawConfigParser()
    conf.read('config.cfg')
    login = conf.get('account', 'login')
    password = conf.get('account', 'password')
    print('Loggin into ' + login)
    vk_session = vk_api.VkApi(login, password, captcha_handler=captcha_handler)
    vk = vk_session.get_api()
    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return
    #Поочередно собираем все телефоны с каждого пользователя
    cnt = 0
    parsed = ''
    max_cnt = len(users_list)-1;
    for user in users_list:
        cnt += 1
        users_str = user + ',' + users_str
        if cnt%10000 == 0:
            parsed = parsed + get_phones(users_str, vk_session)
            users_str = ''
            print(cnt)
        if max_cnt == cnt:
            parsed = parsed + get_phones(users_str, vk_session)
            users_str = ''
            print(max_cnt)
    write_info(parsed)
    print('Done!')
    input('Press Enter...')

main()