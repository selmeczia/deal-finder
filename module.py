from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
from datetime import datetime
import os


class DealFinder:

    def __init__(self, product_group_path, chromedriver_path, output_path, rules_path):
        self.product_group_df = pd.DataFrame()
        self.product_group_path = product_group_path
        self.chromedriver = chromedriver_path
        self.output_path = output_path
        self.rules_path = rules_path

    def task_scheduler(self):
        self.read_inputs()
        self.scrape_handler()

    def read_inputs(self):
        self.input_group_df = pd.read_csv(self.product_group_path, sep=";")

    def df_creation(self, product_dict, run_name):
        df_name = run_name + "_df"
        vars()[df_name] = pd.DataFrame.from_dict(product_dict, orient="index", columns=["Price", "Timestamp"]) \
            .reset_index().rename(columns={"index": "Title"})
        # self.current_df_name = vars()[df_name]
        print("Dataframe created")

        return vars()[df_name]

    def duplicate_removal(self, df):
        path = self.output_path + self.current_run_type + ".csv"
        df["Latest run"] = ""

        if os.path.isfile(path):
            df['Latest run'] = 1
            imported = pd.read_csv(path, sep=";")
            imported_without_latest = imported[imported['Latest run'] == 0]
            imported_only_latest = imported[imported['Latest run'] == 1].copy()
            imported_only_latest['Latest run'] = 0
            latest_and_current = imported_only_latest.append(df)
            removed_duplicates = latest_and_current.drop_duplicates(subset=['Title', 'Price'], keep='last')

            output = imported_without_latest.append(removed_duplicates)
            df = output
        else:
            df["Latest run"] = 0

        print("Duplicates removed")
        return df

    def rule_checker(self, df):
        rules_df = pd.read_csv(self.rules_path, sep=";")
        to_scan = df.loc[df["Latest run"].values == 1].copy()
        to_scan["Title no spaces"] = to_scan["Title"].str.replace(" ", "").str.lower()
        notification = []
        for index, row in rules_df.iterrows():
            if row["file"] == self.current_run_type:
                if row["rule"] == "avaliability":
                    if row["item"] in to_scan["Title"]: notification.append(row["item"] + " is avaliable")
                if "<" in row["rule"]:
                    price_rule = int(row["rule"][1:])
                    items_found = to_scan[to_scan["Title no spaces"].str.contains(str(row["item"]))]
                    try:
                        for item_index, item_row in items_found.iterrows():
                            if int(item_row["Price"]) < price_rule:
                                notification.append(item_row["Title"] + " is avaliable at price: " + str(item_row["Price"]))
                    except:
                        continue

        return notification

    def save_df(self, df):

        path = self.output_path + self.current_run_type + ".csv"
        df.to_csv(path, index=False, header=True, sep=";")
        print("Dataframe saved")

    def scrape_handler(self):
        for index, row in self.input_group_df.iterrows():
            current_store = row[0].split("_")[0]
            self.current_run_type = row[0]
            current_link = row[1]

            if current_store == "Ipon":
                current_scrape = self.scrape_Ipon_group(current_link)
                current_df_raw = self.df_creation(current_scrape, current_store)
                current_df_processed = self.duplicate_removal(current_df_raw)
                self.save_df(current_df_processed)
                self.rule_checker(current_df_processed)

    def scrape_Ipon_group(self, link):

        browser = webdriver.Chrome(self.chromedriver)
        browser.get(link)

        while True:
            time.sleep(2)
            next_page_btn = browser.find_elements_by_class_name("product-list__show-more-button")
            if len(next_page_btn) < 1:
                print("All pages loaded")
                break
            else:
                WebDriverWait(browser, 10) \
                    .until(EC.element_to_be_clickable((By.CLASS_NAME, "product-list__show-more-button"))).click()

        cards = browser.find_elements_by_class_name("shop-card__body")

        product_dict = {}
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

        for card in cards:
            title_element = card.find_elements_by_class_name("shop-card__title")[0].text
            price_element = card.find_elements_by_class_name("shop-card__price-block")[0].text

            if price_element.find("\n") != -1:
                price_element = price_element.split("\n")[1]
                price_int = int(price_element.split(' Ft')[0].replace(' ', ''))
                product_dict[title_element] = [price_int, timestamp]

            elif price_element == "csak b2b":
                continue
            elif price_element == "":
                continue
            else:
                price_int = int(price_element.split(' Ft')[0].replace(' ', ''))
                product_dict[title_element] = [price_int, timestamp]

        print("Scraping done")
        return product_dict

# TODO: add extra values if available (avaliability, free shipping, discounted)
# TODO: deal trigger
# TODO: notification for deal trigger
# TODO: automated run
