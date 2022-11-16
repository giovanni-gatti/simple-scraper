from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
from time import sleep
import json 
from datetime import datetime 
from requests import get
import re 
import os 
import pandas as pd

folders = ["/data/autos","/data/visited"]
for folder in folders:
    print(os.path.isdir(os.getcwd() + folder))
    if not os.path.isdir(os.getcwd() + folder):
        os.mkdir(folder)
    else:
        print(folder,"already exists")

path_to_visited_urls = "data/visited/visited_urls.json"

if not os.path.isfile(path_to_visited_urls):
    with open(path_to_visited_urls,"w") as file:
        json.dump([],file)
countries = {"Italy": "I",
             "Germany": "D",
             "Austria": "A",
             "Belgium" : "B",
             "Spain": "E",
             "France": "F",
             "Luxemburg": "L",
             "Netherlands": "NL"}


page = get("https://www.autoscout24.it")
soup1 = BeautifulSoup(page.text,"lxml")
options = soup1.find("select",{"name":"make"}).findAll("option")

brands = []

for i in options:
    brands.append(i.text)

brands.pop(0)

car_counter=1
cycle_counter=0
while True:
    with open(path_to_visited_urls) as file:
        visited_urls = json.load(file)
    
    if len(visited_urls) > 100000:
        visited_urls = []
    
    multiple_cars_dict = {}
    
    cycle_counter+=1
    for country in countries:
        
        car_URLs = []
        
        for page in range(1,21):
            try:
                url = 'https://www.autoscout24.it/lst?sort=age&desc=1&cy='+countries[country]+'&atype=C&ustate=N%2CU&powertype=kw&page='+str(page)
                only_a_tags = SoupStrainer("a")
                soup = BeautifulSoup(urllib.request.urlopen(url).read(),'lxml', parse_only=only_a_tags)
            except Exception as e:
                print("\n\n Overview: " + str(e) +" "*50, end="\r")
                pass

            for link in soup.find_all("a"):
                if r"/annunci/" in str(link.get("href")):
                    car_URLs.append(link.get("href"))
            car_URLs_unique = [car for car in list(set(car_URLs)) if car not in visited_urls]
            
            print(f'Run {cycle_counter} | {country} | Page {page} | {len(car_URLs_unique)} new URLs', end="\r")
        print("")
        if len(car_URLs_unique)>0:
            for URL in car_URLs_unique:
                print(f'Run {cycle_counter} | {country} | Auto {car_counter}'+' '*50, end="\r")
                try:
                    car_counter+=1
                    car_dict = {}
                    car_dict["country"] = country
                    car_dict["date"] = str(datetime.now())                    
                    car = BeautifulSoup(urllib.request.urlopen('https://www.autoscout24.it'+URL).read(),'lxml')
                    
                    for key, value in zip(car.find_all("dt"),car.find_all("dd")):
                        car_dict[key.text.replace("\n","")] = value.text.replace("\n","")
                    #car_dict["dealer"] = car.find("div",attrs={"class":"cldt-vendor-contact-box",
                    #                                             "data-vendor-type":"dealer"}) != None
                    #car_dict["private"] = car.find("div",attrs={"class":"cldt-vendor-contact-box",
                    #                                           "data-vendor-type":"privateseller"}) != None
                    #car_dict["place"] = car.find("div",attrs={"class":"sc-grid-col-12",
                    #                                       "data-item-name":"vendor-contact-city"}).text
                    
                    #price has the updated html tag which should be working
                    car_dict["price"] =  "".join(re.findall(r'[0-9]+',car.find("div",attrs={"class":"PriceInfo_styledPriceRow__2fvRD"}).text))
                    
                    # equipment = []
                    # for i in car.find_all("div",attrs={"class":"cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"}):
                    #     for span in i.find_all("span"):
                    #         equipment.append(i.text)
                    # equipment2 = []
                    # for element in list(set(equipment)):
                    #     equipment_list = element.split("\n")
                    #     equipment2.extend(equipment_list)
                    # car_dict["equipment_list"] = sorted(list(set(equipment2)))
                    multiple_cars_dict[URL] = car_dict
                    visited_urls.append(URL)
                except Exception as e:
                    print("\n\n Detail Page: " + str(e) + " "*50)
                    pass
            print("")
            
        else:
            print("\U0001F634")
            sleep(60)
    
    if len(multiple_cars_dict)>0:
        df = pd.DataFrame(multiple_cars_dict).T
        df.to_csv("data/autos/"+re.sub("[.,:,-, ]","_",str(datetime.now()))+".csv",sep=";",index_label="url")
    else:
        print("No Data\n\n")
    with open("data/visited/visited_urls.json", "w") as file:
        json.dump(visited_urls, file)