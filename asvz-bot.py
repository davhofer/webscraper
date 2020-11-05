#asvz bot

# link = https://schalter.asvz.ch/tn/lessons/<number>, <number> ist die nummer der jeweiligen lektion
# auf diesen link gehen, auf button mit id:
# id="btnRegister"
# clicken
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import datetime



"""
CHANGE: user must supply direct link to online-schalter einschreibung
"""

lesson_num = input("asvz lesson number: ")


link = "https://schalter.asvz.ch/tn/lessons/<number>"
#chromeoptions.headless = True
driver = webdriver.Firefox()
link.replace("<number>",lesson_num)

driver.get(link)

btn = driver.find_element_by_id('btnRegister')


#when it's time
#btn.click()
