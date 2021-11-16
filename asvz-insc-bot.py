# setup raspberry pi again, add command for discord bot to schedule asvz signup

# install selenium
import subprocess
import sys


import time
import datetime
import re


import getpass


# make sure to download the right version of chromedriver for your version of Google Chrome, and specify the correct path to the file


def main(args):
    if "--help" in args:
        print("---- Help ----")
        print()
        print(
            "use: 'python3 asvz-insc-bot.py' to run the program, after that the user will be prompted to enter the lesson number and his credentials."
        )
        print()
        print("optional arguments:")
        print("--demo               use this argument to display the automated webbrowser while the programm is running.")
        print("--specify-path       use this argument to be able to input a specific path to the chromedriver executable. otherwise, it will be looked for in the system path.")
        print("--help               for help.")
        print()
        return

    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys


    # chromedriver path on my personal linux laptop
    CHROMEDRIVER_PATH_LINUX = "/usr/local/bin/chromedriver"

    chrome_options = Options()
    if '--demo' not in args:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")

    
    
    
    try:
        if '--specify-path' in args:
            CHROMEDRIVER_PATH = input("Please specify the file path to chromedriver:")
            print()
            driver = webdriver.Chrome(options=chrome_options, executable_path=CHROMEDRIVER_PATH)
        else:
            driver = webdriver.Chrome(options=chrome_options, executable_path="./chromedriver")
    except Exception as e:
        print("Please make sure that your chromedriver file is the right version for your browser, and is either in the same folder as the python file or you specified the correct path.")
        return
    print("")
    print("")
    print("Make sure to place the chromedriver file for your version of chrome in the same folder as this python file, or specify the path to it with --specify-path")
    print()
    lesson_num = input("ASVZ lesson number: ")
    username = input("NETHZ username: ")
    password = getpass.getpass("Password: ")
    print("")
    print("Setting up...")
    print()

    link = "https://schalter.asvz.ch/tn/lessons/<number>"
    link = link.replace("<number>", lesson_num)

    # goto main lesson page
    driver.get(link)
    time.sleep(2)

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
    elem = driver.find_element_by_xpath(
        "//button[@class='btn btn-default ng-star-inserted']"
    )
    elem.click()
    time.sleep(2)

    # SWITCH AAI
    elem = driver.find_element_by_xpath("//button[@name='provider']")

    elem.click()
    time.sleep(2)

    # select institution
    elem = driver.find_element_by_xpath("//input[@id='userIdPSelection_iddtext']")
    elem.click()
    elem.send_keys("ETH Zürich")
    elem.send_keys(Keys.ENTER)
    time.sleep(2)

    # enter accoutn data
    elem = driver.find_element_by_xpath("//input[@id='username']")
    elem.click()
    elem.send_keys(username)

    elem = driver.find_element_by_xpath("//input[@id='password']")
    elem.click()
    elem.send_keys(password)

    elem.send_keys(Keys.ENTER)
    time.sleep(2)

    # either will have to accept some agreement or not (get redirected back to lesson page directly)
    try:
        time.sleep(7)
        # accept button
        elem = driver.find_element_by_xpath("//button[@name='_eventId_proceed']")
        print("elementId_proceed element: ")
        print(elem)
        elem.click()
        time.sleep(7)

        # wait until enrollment opens
        if datetime.datetime.now() < t:
            print("Waiting for enrollment to open...")
        while datetime.datetime.now() < t:
            time.sleep(0.7)

        # register
        elem = driver.find_element_by_xpath("//button[@id='btnRegister']")
        elem.click()

        print("Completed successfully, but please check manually if you got a spot.")

    except:
        try:
            # wait until enrollment opens
            if datetime.datetime.now() < t:
                print("Waiting for enrollment to open...")
            while datetime.datetime.now() < t:
                time.sleep(0.7)

            # register
            elem = driver.find_element_by_xpath("//button[@id='btnRegister']")
            elem.click()
            print(
                "Completed successfully, but please check manually if you got a spot."
            )

            # print("Could not register!")
            # f = open("register-dump-" + str(lesson_num) + ".html", "w+")
            # f.write(driver.page_source)
            # f.close()
            # print("on", driver.title)
        except:
            print("ERROR")


main(sys.argv)

