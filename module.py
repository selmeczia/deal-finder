from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np

# TODO: load inputs


class DealFinder:

    def __init__(self, product_group_path, chromedriver):
        self.product_group_df = pd.DataFrame()
        self.product_group_path = product_group_path
        self.chromedriver = chromedriver

    def task_scheduler(self):
        self.read_inputs()
        self.iterate_over_lines()

    def read_inputs(self):
        self.product_group_df = pd.read_csv(self.product_group_path, sep = ";")
        return self.product_group_df

    def iterate_over_lines(self):
        for index, row in self.product_group_df.iterrows():
            name = row.tolist()[0] + ".csv"
            link = row.tolist()[1]

            path = "./output/ " + name


            browser = webdriver.Chrome(self.chromedriver)
            browser.get(link)

            while True:
                next_page_btn = browser.find_elements_by_class_name("product-list__show-more-button")
                time.sleep(1)
                if len(next_page_btn) < 1:
                    print("All pages loaded")
                    break
                else:
                    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "product-list__show-more-button"))).click()

            cards = browser.find_elements_by_class_name("shop-card__body")

            title_list = []
            price_list = []

            for card in cards:
                title_element = card.find_elements_by_class_name("shop-card__title")[0].text
                price_element = card.find_elements_by_class_name("shop-card__price-block")[0].text

                if (price_element.find("\n") != -1):
                    price_element = price_element.split("\n")[1]
                    price_int =  int(price_element.split(' Ft')[0].replace(' ', ''))
                elif (price_element == "csak b2b"):
                    price_int = np.nan
                else:
                    price_int = int(price_element.split(' Ft')[0].replace(' ', ''))

                title_list.append(title_element)
                price_list.append(price_int)

            df = pd.DataFrame(list(zip(title_list, price_list)), columns=['Title', "Price"])

            print(df)



            # print(source)

            # print(soup.find_all('div', class_='shop-card__body'))

            # for item in soup.find_all('div', class_='shop-card__price'):
            #
            #     item_price_raw = item.find('div', class_='row-price').text
            #     item_price = item_price_raw.split(' Ft')[0].replace(' ', '')
            #
            #     store_name = item.find('div', class_='shopname').text
            #
            #     link = item.find('a', class_='jumplink-overlay initial')
            #     item_link = link['href']
            #
            #     price_list.append(int(item_price))
            #     store_list.append(store_name)
            #     link_list.append(item_link)
            #
            # if not (price_list):
            #     pass
            # else:
            #     min_price = min(price_list)
            #     df = pd.DataFrame(list(zip(price_list, store_list, link_list)), columns=['Price', "Store", "Link"])
            #     df["Min price"] = min_price
            #     df["Date"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            #     df = df[["Date", "Price", "Min price", "Store", "Link"]]
            #
            #     df['Latest_run'] = ""
            #
            #     # if not first run:
            #     if os.path.isfile(path):
            #         df['Latest_run'] = 1
            #         imported = pd.read_csv(path)
            #         imported_without_latest = imported[imported['Latest_run'] == 0]
            #         imported_only_latest = imported[imported['Latest_run'] == 1].copy()
            #         # https://www.dataquest.io/blog/settingwithcopywarning/
            #         imported_only_latest['Latest_run'] = 0
            #         latest_and_current = imported_only_latest.append(df)
            #         removed_duplicates = latest_and_current.drop_duplicates(subset=['Store', 'Price'], keep='last')
            #
            #         output = imported_without_latest.append(removed_duplicates)
            #         df = output
            #
            #     else:
            #         df['Latest_run'] = 0

# TODO: find prices of products
# TODO: add extra values if available (avaliability, free shipping, discounted)
# TODO: create database for the scraped data
# TODO: remove unnecessary data (look for old project)
# TODO: deal trigger
# TODO: notification for deal trigger
# TODO: automated run
