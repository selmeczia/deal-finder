# print("initial commit")

from module import *


config_path = "config/"
product_group_input = config_path + "product_group_input.csv"
chromedriver = "C:\Program Files (x86)\chromedriver.exe"

DealFinder(product_group_input, chromedriver).task_scheduler()

#browser = webdriver.Chrome(chromedriver)
#browser.get("https://ipon.hu/shop/csoport/szamitogep-alkatresz/videokartya?price=23790-299790&sortOrder=olcso&page=1")
#print(browser.title)