import os
import json
from sys import stderr, exit
import tls_client
import inquirer
import xlsxwriter
from art import text2art
from loguru import logger
from termcolor import colored
from inquirer.themes import load_theme_from_dict as loadth


######### ILES SETTINGS
cwd = os.getcwd()
file_data1 = f'{cwd}/files/database1.json'
file_data2 = f'{cwd}/files/database2.json'
file_data3 = f'{cwd}/files/database3.json'
file_query1 = f'{cwd}/files/query1.json'
file_query2 = f'{cwd}/files/query2.json'
file_query3 = f'{cwd}/files/query3.json'
file_query4 = f'{cwd}/files/query4.json'
file_wallets = f'{cwd}/files/wallets.txt'
file_excel_table = f'{cwd}/_PH Stats.xlsx'

######### LOGGING SETTING
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")

WALLETS = []
QUERY1 = 2623081
QUERY2 = 2623051
QUERY3 = 2623025


def is_exists(path: str) -> bool:
    return os.path.isfile(path)

######### Редагувиння даних
def filter_wallets1(wallet: dict) -> bool:
    if (wallet['wallet'].lower() in WALLETS):
        return True
    return False

def filter_wallets2(wallet: dict) -> bool:
    try:
        if (wallet['wallet'].lower() in WALLETS):
            return True
    except:
        return False
    return False

def filter_wallets3(wallet: dict) -> bool:
    try:
        if (wallet['wallet'].lower() in WALLETS):
            return True
    except:
        return False
    return False

#########
def load_wallets() -> None:
    global WALLETS
    with open(file_wallets, 'r') as file:
        WALLETS = [row.strip().lower() for row in file]

#########
def edit_dates1(wallets: list) -> None:
    for wallet in wallets:
        for i in wallet:
            if (i in (['ibt'])):
                wallet[i] = wallet[i][:19]
            if (i == 'txs_msg' and wallet[i] != None):
                wallet[i] = round(wallet[i],2)
                
def edit_dates2(wallets: list) -> None:
    for wallet in wallets:
        for i in wallet:
            if (i == 'txs_nft' and wallet[i] != None):
                wallet[i] = round(wallet[i],2)
                
def edit_dates3(wallets: list) -> None:
    for wallet in wallets:
        for i in wallet:
            if (i in (['ibt'])):
                wallet[i] = wallet[i][:19]
            if (i == 'txs_msg' and wallet[i] != None):
                wallet[i] = round(wallet[i],2)                

#########
def get_filtered_wallets(data_file: str) -> list:
    with open(data_file, 'r') as file:
        data = json.load(file)

    all_wallet_info = data['data']['get_execution']['execution_succeeded']['data']
    
    if data_file == file_data1:
        filtered_wallets = list(filter(filter_wallets1, all_wallet_info))
        edit_dates1(filtered_wallets)
    elif data_file == file_data2:
        filtered_wallets = list(filter(filter_wallets2, all_wallet_info))
        edit_dates2(filtered_wallets)
    else:
        filtered_wallets = list(filter(filter_wallets3, all_wallet_info))
        edit_dates3(filtered_wallets)
    return filtered_wallets

######### Створення таблиці
def save_to_excel(wallets1: list, wallets2: list, wallets3: list) -> None:
    pretty_columns = [
        "Rank ID",
        "Wallet",
        "Contracts",
        "Total TXS",
        "NFT",
        "Message",
        
    ]

    columns = list(wallets1[0].keys())
    columns.insert(5,"txs_nft")
    columns.insert(6,"txs_msg")

    for wallet in wallets1:
        for i, wallet2 in enumerate(wallets2):
            if wallet["wallet"] == wallet2["wallet"]:
                break
        else:
            wallet["txs_nft"] = 0
            wallet["txs_msg"] = 0
            continue
        wallet["txs_nft"] = wallets2[i]["txs_nft"]
    
    for wallet in wallets1:
        for i, wallet3 in enumerate(wallets3):
            if wallet["wallet"] == wallet3["wallet"]:
                break
        else:
            wallet["txs_nft"] = 0
            wallet["txs_msg"] = 0
            continue
        wallet["txs_msg"] = wallets3[i]["txs_msg"]
    
    workbook = xlsxwriter.Workbook(file_excel_table)
    worksheet = workbook.add_worksheet("Stats")

    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'border': 1
    })
    for col_num, column in enumerate(pretty_columns):
        worksheet.write(0, col_num, column, header_format)

    for row_num, wallet in enumerate(wallets1, 1):
        for col_num, col in enumerate(columns):
            worksheet.write(row_num, col_num, wallet[col])

    # Закріплення першого рядка
    worksheet.freeze_panes(1, 0)  # Перший рядок, починаючи з другого стовпця
    
    row_format = workbook.add_format({'align': 'center'})
    sizes = [9, 45, 12, 12, 12, 12]
    for col_num, size in enumerate(sizes):
        worksheet.set_column(col_num, col_num, size, row_format)

    first_row_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'vcenter',
        'align': 'center',
        'border': 1
    })
    worksheet.set_row(0, 18, first_row_format) #висота стовпця

    workbook.close()

######### Помилка оновлення
def get_execution_id(session: tls_client.Session, query_id: int) -> int:
    with open(file_query1, 'r') as file:
        payload = json.load(file)

    payload['variables']['query_id'] = query_id

    while True:
        try:
            response = session.post('https://core-hsr.dune.com/v1/graphql', json=payload)
            if (response.status_code == 200):
                break
            else:
                logger.error(f'Ошибка обновления базы данных: {response.text} | Cтатус запроса: {response.status_code}')
        except Exception as error:
            logger.error(f'Ошибка обновления базы данных: {error}')

    execution_id = response.json()['data']['get_result_v3']['result_id']
    return execution_id

#########  Веб клієнт
def setup_session() -> tls_client.Session:
    session = tls_client.Session(
        client_identifier="chrome112",
        random_tls_extension_order=True
    )

    headers = {
        'origin': 'https://dune.com',
        'referer': 'https://dune.com/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    session.headers = headers
    session.timeout_seconds = 1000
    return session

######### Завантаження даних
def update_database() -> None:
    session = setup_session()

    
    logger.info('Начинаю скачивание двух баз данных. Процесс может занять несколько минут...')


############ Скачиваю 1 базу данных
    with open(file_query2, 'r') as file:
        payload = json.load(file)

    execution_id = get_execution_id(session, QUERY1)
    logger.info(f'ID #1 базы данных №{QUERY1}: {execution_id}')
    payload['variables']['execution_id'] = execution_id

    while True:
        try:
            response = session.post('https://app-api.dune.com/v1/graphql', json=payload)
            if (response.status_code == 200):
                logger.success(f'База данных №{QUERY1} успешно скачана!')
                break
            else:
                logger.error(f'Ошибка обновления базы данных: {response.text} | Cтатус запроса: {response.status_code}')
        except Exception as error:
            logger.error(f'Ошибка обновления базы данных: {error}')
    
    with open(file_data1, 'w') as file:
        json.dump(response.json(), file)

############ Скачиваю 2 базу данных

    with open(file_query3, 'r') as file:
        payload = json.load(file)

    execution_id = get_execution_id(session, QUERY2)
    logger.info(f'ID #2 базы данных №{QUERY2}: {execution_id}')
    payload['variables']['execution_id'] = execution_id

    while True:
        try:
            response = session.post('https://app-api.dune.com/v1/graphql', json=payload)
            if (response.status_code == 200):
                logger.success(f'База данных №{QUERY2} успешно скачана!')
                break
            else:
                logger.error(f'Ошибка обновления базы данных: {response.text} | Cтатус запроса: {response.status_code}')
        except Exception as error:
            logger.error(f'Ошибка обновления базы данных: {error}')
    
    with open(file_data2, 'w') as file:
        json.dump(response.json(), file)

############ Скачиваю 3 базу данных
    with open(file_query4, 'r') as file:
        payload = json.load(file)

    execution_id = get_execution_id(session, QUERY3)
    logger.info(f'ID #3 базы данных №{QUERY3}: {execution_id}')
    payload['variables']['execution_id'] = execution_id

    while True:
        try:
            response = session.post('https://app-api.dune.com/v1/graphql', json=payload)
            if (response.status_code == 200):
                logger.success(f'База данных №{QUERY3} успешно скачана!')
                break
            else:
                logger.error(f'Ошибка обновления базы данных: {response.text} | Cтатус запроса: {response.status_code}')
        except Exception as error:
            logger.error(f'Ошибка обновления базы данных: {error}')
    
    with open(file_data3, 'w') as file:
        json.dump(response.json(), file)


    logger.success(f'Готово!\n')

######### Створення таблиці
def make_table() -> None:
    exists1 = is_exists(file_data1)
    exists2 = is_exists(file_data2)
    exists3 = is_exists(file_data3)
    #exists4 = is_exists(file_data4)
    if (not exists1 or not exists2 or not exists3): #add 'or not exists3 or not exists4'
        logger.info('Файлы баз данных отстутствуют!')
        update_database()

    load_wallets()
    logger.info(f'Загружено {len(WALLETS)} кошельков')
    filtered_wallets1 = get_filtered_wallets(file_data1)
    filtered_wallets2 = get_filtered_wallets(file_data2)
    filtered_wallets3 = get_filtered_wallets(file_data3)
    
    if (len(filtered_wallets1) == 0):
        logger.error('Не найден ни один кошелек в базе!')
        return
    save_to_excel(filtered_wallets1, filtered_wallets2, filtered_wallets3)
    logger.success('Готово!\n')
    WALLETS.clear()

######### Головне меню вибір
def get_action() -> str:
    theme = {
        "Question": {
            "brackets_color": "bright_yellow"
        },
        "List": {
            "selection_color": "bright_blue"
        }
    }

    question = [
        inquirer.List(
            "action",
            message=colored("Выберите действие", 'light_yellow'),
            choices=["Обновить базу данных", "Составить Excel таблицу", "Выход"],
        )
    ]
    action = inquirer.prompt(question, theme=loadth(theme))['action']
    return action

######### Головне меню
def main() -> None:

    text = "ZkBridge Stats"
    text_parts = text.split(" ")

    line1 = " ".join(text_parts[:1])
    line2 = " ".join(text_parts[1:])

    art = text2art(text=f"{line1}\n{line2}", font="standard")
    print(colored(art,'light_blue'))

    while True:
        action = get_action()

        match action:
            case 'Обновить базу данных':
                update_database()
            case 'Составить Excel таблицу':
                make_table()
            case 'Выход':
                exit()
            case _:
                pass


if (__name__ == '__main__'):
    main()
