#asvz bot


#################################################################
#
# make into fully fledged excecutable
# install python, pip, selenium etc.
# run program
# set up
# ask user if sign up opening is correct, allow for manual input if not
#
#################################################################


import time
import re
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass

DEBUG = False

CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
WINDOW_SIZE = "1920,1080"
chrome_options = Options()

chrome_options.add_argument("--headless")

chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
driver.implicitly_wait(10) # seconds


lesson_num = input("ASVZ lesson number: ")

print("Setting up...")

link = "https://schalter.asvz.ch/tn/lessons/<number>"
link = link.replace("<number>",lesson_num)

driver.get(link)

# Current location: LESSON SITE

now = time.mktime(time.localtime())
while time.mktime(time.localtime()) < now+10:
    try:
        assert driver.title.split(' ')[0] != "Online-Schalter"
        break
    except:
        pass

print(driver.title)
lesson = driver.title

#wait = WebDriverWait(driver, 10)
#element = wait.until(EC.element_to_be_clickable((By.XPATH, 'someXPATH')))

try:
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'button')))
except:
    pass
buttons = driver.find_elements_by_tag_name('button')
buttons[1].click()

# Current location: LOGIN - ONLINE-SCHALTER | SELECT LOGIN METHOD

try:
    WebDriverWait(driver, 10).until(
        EC.title_is('Login - Online-Schalter')
    )
except:
    pass
finally:
    assert driver.title == 'Login - Online-Schalter'


print(driver.title)



try:
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'button')))
except:
    pass
buttons = driver.find_elements_by_tag_name('button')
buttons[3].click()


# Current location: Switch AAI Organisation selection (OR directly ETH login)
if DEBUG:
    input("break 1 (here starts the headless trouble): ")

print(driver.title)


wait = WebDriverWait(driver, 10)
time.sleep(3)
uni_input_field = wait.until(EC.presence_of_element_located((By.ID,'userIdPSelection_iddtext')))
uni_input_field = driver.find_element_by_id('userIdPSelection_iddtext')
print(uni_input_field.text)
time.sleep(1)
uni_input_field.clear()
time.sleep(1)
uni_input_field.send_keys('ETH Zurich')
time.sleep(2)
driver.find_element_by_name('Select').click()
time.sleep(1)

print(driver.title)
#!!!!!!!!! login doesnt work with headless !!!!!!!!!!!



wait = WebDriverWait(driver, 10)
field_username = wait.until(EC.presence_of_element_located((By.ID,'username')))
#field_username = driver.find_element_by_id('username')
username = input('ETH username: ')
field_username.send_keys(username)
field_password = driver.find_element_by_id('password')
password = getpass.getpass("password: ")
field_password.send_keys(password)
time.sleep(2)
driver.find_element_by_tag_name('button').click()




#if first login: have to accept that stuff...
#button_accept = driver.find_element_by_name('_eventId_proceed')
if DEBUG:
    input("break 2: ")
print(driver.title)

if driver.title == "Information Release":
    box = driver.find_element_by_class_name('ce-text')
    cd = box.find_elements_by_class_name('consentDuration')[2]
    input_field = cd.find_elements_by_tag_name('input')[1]
    time.sleep(1)
    input_field.click()


input("break 3: ")

time.sleep(1)

findr = re.compile('[MDFS][oira], [0-9][0-9].[0-9][0-9].20[0-9][0-9] [0-9][0-9]:[0-9][0-9]')
time.sleep(1)
results = findr.findall(driver.page_source)
print(results)
time.sleep(1)
signup_open = results[1]



if DEBUG:
    print(results[1])

print("Lesson: ",lesson," | Signup opening at: ", signup_open)
confirm = input("Correct? [y/n] ")
if confirm == 'n':
    print("Please restart the program or consult with a developer.")
    exit()

s = results[1][4:]

if DEBUG:
    print(s)


day = s.split('.')[0]
month = s.split('.')[1]
year = (s.split('.')[2]).split(' ')[0]
t = s.split(' ')[1]
t = t + ':00'

dt_string = year + '-' + month + '-' + day + ' ' + t

if DEBUG:
    print(dt_string)
    dt_string = '2020-11-08 14:38:30'


button_register = driver.find_element_by_id('btnRegister')

def action():
    button_register.click()

def dummy_action():
    print('job executing')


# TODO: what if signup date already past?

sched = BackgroundScheduler()

sched.add_job(dummy_action, 'date', run_date=dt_string)
print("Job scheduled!")
sched.start()
# TODO: when to close the driver? make sure request has completed!
# sleep until done
try:
    input("Wait until signup is complete, then enter 'done': ")
finally:
    driver.close()
