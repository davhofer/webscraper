import subprocess
import sys


import time
import datetime
import re


import getpass

from multiprocessing import Process



# make sure to download the right version of chromedriver for your version of Google Chrome, and place it in the same location as the script



def main(args,lesson_num,username,password):
    if "--help" in args:
        print("---- Help ----")
        print()
        print(
            "use: 'python3 asvz-insc-bot.py' to run the program, after that the user will be prompted to enter the lesson number and his credentials."
        )
        print()
        print("optional arguments:")
        print("--demo               use this argument to display the automated webbrowser while the programm is running.")
        print("--raspbian           to run in production environment on raspberry pi.")
        print("--help               for help.")
        print()
        return

    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC 

    print()
    print()


    
    chrome_options = Options()
    if '--demo' not in args:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")

    
    
    
    try:
        if '--raspbian' in args:
            subprocess.check_call(['sudo','apt-get','install','chromium-chromedriver'])
            driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options, executable_path="./chromedriver")
    except Exception as e:
        print("Please make sure that your chromedriver file is the right version for your browser, and is either in the same folder as the python script or specified in PATH.")
        return

    def explicitWait(xpath,condition="clickable",timeout=30):
        # case: condition == "clickable"
        func = EC.element_to_be_clickable
        if condition == "present":
            func = EC.presence_of_element_located
            
        return WebDriverWait(driver, timeout).until(func((By.XPATH, xpath)))

    print("Setting up...")
    print()

    link = "https://schalter.asvz.ch/tn/lessons/<number>"
    link = link.replace("<number>", lesson_num)

    # goto main lesson page
    driver.get(link)
    
    # instead of:
    #time.sleep(2)
    # use:
    try:
        # elem = driver.find_element_by_xpath(
        # "//button[@class='btn btn-default ng-star-inserted']"
    #)
        elem = explicitWait("//button[@class='btn btn-default ng-star-inserted']")
    except:
        print("Timeout exception when waiting for lesson page")
        return
    # get time when enrollment opens
    html = driver.page_source
    r = "Datum/Zeit.*\n.*"

    ans = re.search(r, html)[0].split(", ")[1].split(" -")[0]
    d = int(ans.split(".")[0]) - 1
    mo = int(ans.split(".")[1])
    y = int(ans.split(".")[2].split(" ")[0])
    h = int(ans.split(".")[2].split(" ")[1].split(":")[0])
    mi = int(ans.split(".")[2].split(" ")[1].split(":")[1])

    t = datetime.datetime(
        year=y, month=mo, day=d, hour=h, minute=mi, microsecond=200000
    )

    # login
    
    elem.click()
    #time.sleep(2)

    # SWITCH AAI
    try:
        #elem = driver.find_element_by_xpath("//button[@name='provider']")
        elem = explicitWait("//button[@name='provider']")
    except:
        print("Timeout exception when waiting for SWITCH AAI")
        return

    elem.click()
    #time.sleep(2)

    # select institution
    try:
        elem = explicitWait("//input[@id='userIdPSelection_iddtext']")
    except:
        print("Timeout exception waiting for institution")
        return
    #elem = driver.find_element_by_xpath("//input[@id='userIdPSelection_iddtext']")
    elem.click()
    elem.send_keys("ETH Zürich")
    elem.send_keys(Keys.ENTER)
    #time.sleep(2)

    # enter accoutn data
    try:
        elem = explicitWait("//input[@id='username']")
    except:
        print("Timeout exception waiting for username input field")
        return
    #elem = driver.find_element_by_xpath("//input[@id='username']")
    elem.click()
    elem.send_keys(username)

    try:
        elem = explicitWait("//input[@id='password']")
    except:
        print("Timeout exception waiting for password input field")
        return
    #elem = driver.find_element_by_xpath("//input[@id='password']")
    elem.click()
    elem.send_keys(password)

    elem.send_keys(Keys.ENTER)
    #time.sleep(2)




    def f1():
        try:
            explicitWait("//button[@id='btnRegister']",condition="present",timeout=30)
        except:
            print("Timeout exception: waiting for register button")

    def f2():
        try:
            explicitWait("//button[@name='_eventId_proceed']",condition="present",timeout=30)
        except:
            print("Timeout exception: waiting for accept button")

    p1 = Process(target=f1)
    p2 = Process(target=f2)

    p1.start()
    p2.start()


    for i in range(20):

        # check if either process has finished, react accordingly
        if not p1.is_alive():
            p1.join()
            p2.terminate()
            p2.join()

            if datetime.datetime.now() < t:
                print("Waiting for enrollment to open...")
            while datetime.datetime.now() < t:
                time.sleep(0.5)

            elem = explicitWait("//button[@id='btnRegister']")
            elem.click()
            print("Completed successfully, but please check manually if you got a spot.")

            return

        if not p2.is_alive():
            p2.join()
            p1.terminate()
            p1.join()

            elem = explicitWait("//button[@name='_eventId_proceed']")
            elem.click()

            if datetime.datetime.now() < t:
                print("Waiting for enrollment to open...")
            while datetime.datetime.now() < t:
                time.sleep(0.7)

            elem = explicitWait("//button[@id='btnRegister']")
            elem.click()

            print("Completed successfully, but please check manually if you got a spot.")

            return 

        time.sleep(1)
    
    print("Error: Did not reach signup page!")

            



if __name__ == '__main__':
    # driver code
    lesson_num = input("ASVZ lesson number: ")
    username = input("NETHZ username: ")
    password = getpass.getpass("Password: ")

    main(sys.argv,lesson_num,username,password)

