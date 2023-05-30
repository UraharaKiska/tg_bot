import asyncio
from fake_useragent import UserAgent
import aiohttp
import requests
from bs4 import BeautifulSoup
import time, random
import json
from selenium import webdriver
import re
import os
from  config import *

anime_name_list = []


def get_data(page):
    ua = UserAgent()
    url = f"https://jut.su/anime/page-{page}"
    headers = {'User-Agent': ua.random,
               'Accept': '*/*'}
    try:
        response = requests.get(url=url, headers=headers)
        with open(f"test/page-{page}.html", 'w') as file:
            file.write(response.text)
        print(f"{page} --- ready")
        time.sleep(random.randrange(2, 4))
    except Exception as ex:
        print(ex)


def scrapy() -> list:
    # url = "https://jut.su/anime/ongoing/"
    anime_name_list = []
    path = "./test"
    for f in os.listdir(path):
        if os.path.isfile:
            file = os.path.join(path, f)
            with open(file, 'r') as file:
                site = file.read()
                soup = BeautifulSoup(site, "lxml")
                try:
                    # content = soup.find('div', class_="all_anime_tooltip")
                    anime_name_block = soup.find_all('div', class_="all_anime")
                    for part in anime_name_block:
                        name = part.find('div', class_="aaname").text
                        episod = part.find('div', class_="aailines").text
                        index = episod.find('сери')
                        i = 2
                        series = ''
                        while episod[index - i].isdigit():
                            series += episod[index - i]
                            i += 1
                        series = series[::-1]
                        title = name
                        name = re.sub(r"[:,.;!? ]", '', name).replace('-', '').replace('ё', 'е').lower()
                        anime_name_list.append({'name': name, 'title': title, 'episode_count': series})
                except Exception as ex:
                    print(ex)

    return anime_name_list
    # print(anime_name_list)

def finaly_parse():
    for page in range(1, 33):
        get_data(page)
    anime = scrapy()
    return anime

# async def main():
#     start_time = time.time()
#     # gather_data()
#     anime_list = list(scrapy())
#     new_list = check_new_episode_or_anime(anime_list)
#     if len(new_list) != 0:
#         with open("anime/anime_list.txt", "w") as file:
#             for el in new_list:
#                 file.write(el)
#         await ClientStatesGroup.send_update.set()
#     finish_time = time.time()
#     print(finish_time - start_time)
#
# if __name__ == "__main__":
#     asyncio.run(main())
#


#
# def connect_to_data_base():
#     conn = 0
#
#     try:
#         # пытаемся подключиться к базе данных
#         conn = psycopg2.connect(dbname=DB_NAME, user=LOGIN, password=PASS, host=HOST)
#         print("Connected with database")
#         # create_table(conn)
#         load_data(conn, anime_name_list)
#     except  Exception as ex:
#         # в случае сбоя подключения будет выведено сообщение в STDOUT
#         print(ex)

    # cursor = conn.cursor()


# def connect_the_site(url):
#     options = webdriver.FirefoxOptions()
#     options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0")
#     options.set_preference("dom.webdriver.enabled", False)
#     options.headless = True
#     driver = webdriver.Firefox(
#         executable_path="/home/gregorok/my_work/get_new_epizod/geckodriver",
#         options=options,
#     )
#
#     try:
#
#         driver.get(url=url)
#
#         for i in range(1, 5):
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(1)
#
#         time.sleep(15)
#
#         with open("data/ongoing.html", 'w') as file:
#             file.write(driver.page_source)
#     except Exception as ex:
#         print(ex)
#     finally:
#         driver.close()
#         driver.quit()


