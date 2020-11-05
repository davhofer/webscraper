#ApartScraper
"""
help us find an apartment pls :/
"""

"""
regex_pattern = r'<a href="/rent/real-estate/city-zurich/matching-list(.*?)Go to next page'
regex_reverse = r'egap txen ot oG(.*?)tsil-gnihctam/hciruz-ytic/etatse-laer/tner/"=ferh a<'


"""

# https://www.google.ch/maps/dir/ETH+Zürich,+Rämistrasse+101,+8092+Zürich/Schäracher+2,+Zürich/

# class = section-directions-trip-numbers


import requests
import re
import json
from selenium import webdriver
import time
import os
from selenium.webdriver.chrome.options import Options
from datetime import date



def getLinkToNextPage(r):
    regex_pattern = re.compile(r'<a href="/rent/real-estate/city-zurich/matching-list(.*?)Go to next page')
    matchZero = regex_pattern.search(r.text).group()
    #might be too large
    regex_pattern_reverse = re.compile(r'egap txen ot oG(.*?)tsil-gnihctam/hciruz-ytic/etatse-laer/tner/"=ferh a<')
    match = regex_pattern_reverse.search(matchZero[::-1]) #search reversed matchZero from behind
    link = ((match.group()[::-1]).split('"')[1]).replace('amp;','')
    return 'https://www.homegate.ch' + link

def addApartment(data,address,link,name,approxDistance,rooms,price,livingSpace,availableFrom,description,scanDate,check):
    data[address] = {
    'link': link,
    'address': address,
    'name':name,
    'approxDistance':approxDistance,
    'rooms': rooms,
    'price': price,
    'livingSpace': livingSpace,
    'availableFrom':availableFrom,
    'description':description,
    'scanDate':scanDate,
    'check': check
    }
    #print(data[address])
    print('ITEM ADDED')


def commitNewFindingsJSON(data,file):
    with open(file,'w+') as outfile:
        json.dump(data,outfile,indent=4)#,ensure_ascii=False)
    outfile.close()

def commitNewFindingsCSV(data,file):
    file = (file.split('.')[0]) + '.csv'
    categories = ['link','address','name','approxDistance','rooms','price','livingSpace','availableFrom','description','scanDate']
    with open(file,'w') as f:
        for c in categories:
            f.write(c + ",")
        f.write("\n")
        for apart_addr in data.keys():
            for key in data[apart_addr].keys():
                f.write(data[apart_addr][key] + ",")
            f.write("\n")
        f.close()


def readFileJSON(file):
    if os.path.getsize(file) != 0:
        with open(file,'r') as f:
            old_data = json.load(f)
            f.close()
    else:
        old_data = {}
    return old_data

def readFileCSV(file):
    file = (file.split('.')[0]) + '.csv'
    categories = ['link','address','name','approxDistance','rooms','price','livingSpace','availableFrom','description','scanDate']
    data = {}
    if os.path.getsize(file) != 0:
        with open(file,'r') as f:
            for line in f.readlines():
                l = line.split(',')
                if l[0] == 'link':
                    continue
                apart = {}
                for i in range(len(categories)):
                    apart[categories[i]] = l[i]
                data[l[1]] = apart
            f.close()
    return data



def replaceSwiss(s):
    s = s.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('é','e')

    return s

def errPrint(msg):
    print('-------------- ERROR ---------------')
    print(msg)
    print('------------------------------------')




query_homegate = 'https://www.homegate.ch/rent/real-estate/city-zurich/matching-list?ac=_minRooms_&ah=_maxPrice_'

# Navigating pages: search in sourcecode if contains 'Go to page i'

minRoomNumber = input('Rooms (min): ')
maxPrice = input('Price (max): ')

query_homegate = query_homegate.replace('_maxPrice_',str(maxPrice))
query_homegate = query_homegate.replace('_minRooms_',str(minRoomNumber))

#data_file = "homegate_" + date.today().strftime("%b-%d-%Y") + "_" + str(minRoomNumber) + "rooms_" + str(maxPrice) + "maxPrice" + ".txt"
data_file = "homegate_apartment_data.txt"
totalPages = 1

#old_data = readFileJSON(data_file)
old_data = readFileJSON(data_file)


###################################################

new_data = {}
chromeoptions = Options()
chromeoptions.headless = True
driver = webdriver.Chrome(options=chromeoptions)

newFindings = 0

tooFar = []


while True:
    r = requests.get(query_homegate)
    print('page ' + str(totalPages))

    for href in re.findall(r'a href="/rent/\d+" ',r.text):
        newFindings += 1
        link = 'https://www.homegate.ch' + href.replace('a href="','')
        link = link[:-2]

        page = requests.get(link)

        driver.get(link)

        try:
            address = driver.find_element_by_class_name("AddressDetails_street_22a5p").text[:-1]
        except:
            address = str(newFindings) + "_NoAddress"
        if address == str(newFindings) + "_NoAddress":
            time.sleep(1)
            try:
                address = driver.find_element_by_class_name("AddressDetails_street_22a5p").text[:-1]
            except:
                address = str(newFindings) + "_NoAddress"

        address = replaceSwiss(address)

        if address in old_data:
            newFindings -= 1
            continue

        price = ''
        if '"price":' in page.text:
            p = re.compile(r'"price":(\d+)?')
            if p.search(page.text) == None:
                newFindings -= 1
                continue # "Preis auf Anfrage"
            price = p.search(page.text).group().replace('"price":','')

        if price == '':
            newFindings -= 1
            continue

        rooms = ''
        if '"numberOfRooms":' in page.text:
            p = re.compile(r'"numberOfRooms":\d\.?\d?')
            rooms = p.search(page.text).group().replace('"numberOfRooms":','')

        livingSpace = ''
        if 'livingSpace":' in page.text:
            p = re.compile(r'livingSpace":\d+')
            livingSpace = p.search(page.text).group().replace('livingSpace":','')

        availableFrom = ''
        if 'availableFrom":' in page.text:
            p = re.compile(r'availableFrom":"\d+-\d+-\d+"')
            availableFrom = p.search(page.text).group().replace('availableFrom":"','')[:-1]


        description = ''
        name = ''
        try:
            descriptionPart = driver.find_element_by_class_name("Description_description_2w_d-")
            try:
                name = str(descriptionPart.find_element_by_tag_name("h1").text)
            except:
                errPrint('html: title not found')
            try:
                description = str(descriptionPart.find_element_by_class_name("Description_descriptionBody_2wGwE").text)
            except:
                errPrint("html: description body not found")
        except:
            errPrint("html: description div not found")

        description = replaceSwiss(description)
        name = replaceSwiss(name)

        # https://www.google.ch/maps/dir/ETH+Zürich,+Rämistrasse+101,+8092+Zürich/Schäracher+2,+Zürich/

        # class = section-directions-trip-distance section-directions-trip-secondary-text
        address_dissected = address.split(" ")
        if len(address_dissected) == 2:
            routelink = "https://www.google.ch/maps/dir/ETH+Zürich,+Rämistrasse+101,+8092+Zürich/%s+%s,+Zürich/" % (address.split(" ")[0],address.split(" ")[1])
        elif len(address_dissected) == 1:
            routelink = "https://www.google.ch/maps/dir/ETH+Zürich,+Rämistrasse+101,+8092+Zürich/%s,+Zürich/" % address.split(" ")[0]
        else:
            routelink = ''

        if routelink != '':
            driver.get(routelink)
            try:
                approxDistance = str(driver.find_element_by_class_name('section-directions-trip-numbers').text).split('\n')[1]
            except:
                time.sleep(2)
                try:
                    approxDistance = str(driver.find_element_by_class_name('section-directions-trip-numbers').text).split('\n')[1]
                except:
                    approxDistance = ''
                    errPrint('Could not assess approximate distance')

            if approxDistance != '':
                approxDistance = approxDistance.replace(',','.')
                if float(approxDistance.split(' ')[0]) > 5.0:
                    print(address + ": too far? " + link)
                    tooFar.append([address,link])
        else:
            approxDistance = ''
            errPrint('Could not assess approximate distance. Invalid address.')


        # if '"description":' in page.text:
        #     desc = re.findall('"description":".*?"',page.text)
        #     max = 0
        #     for d in desc:
        #         if len(d) > max:
        #             description = d
        #             max = len(d)
        #     description = description.replace('"description":"','')[:-1]
        #     #description = (description.encode('ascii', 'ignore')).decode("utf-8")
        #
        #
        # name = ''
        # if '"name":' in page.text:
        #     p = re.compile(r'name":".*?"')
        #     name = p.search(page.text).group().replace('name','')[3:-1]
        #     #name = name.encode('ascii','ignore')
        #     #name = (name.encode('ascii', 'ignore')).decode("utf-8")
        #
        # print(name)
        scanDate = date.today().strftime("%b-%d-%Y")

        addApartment(new_data,address,link,name,approxDistance,rooms,price,livingSpace,availableFrom,description,scanDate,False)

    if('Go to next page' not in r.text):
        print('LAST PAGE')
        break

    query_homegate = getLinkToNextPage(r)
    totalPages += 1

print()
print("+++++++ DONE +++++++")
print(str(newFindings) + " new apartments found!")
if len(tooFar) > 0:
    print("These appartments might be too far from ETH Zentrum:")
for e in tooFar:
    print(e[0] + ", " + e[1])



#commitNewFindingsJSON(new_data,data_file)
if len(new_data) > 0:
    new_data.update(old_data)
    commitNewFindingsJSON(new_data,data_file)
###################################################
driver = None
