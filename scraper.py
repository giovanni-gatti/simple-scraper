from bs4 import BeautifulSoup, SoupStrainer
from requests import get
import urllib.request
from time import sleep
import json 
from datetime import datetime 
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
countries = {"Italy": "I"}

page = get("https://www.autoscout24.it")
soup1 = BeautifulSoup(page.text,"lxml")
options = soup1.find("select",{"name":"make"}).findAll("option")

brands = []

for i in options:
    brands.append(i.text)

brands.pop(0)
print(brands)

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
                # print(URL)
                try:
                    car_counter+=1
                    car_dict = {}
                    car_dict["country"] = country
                    car_dict["date"] = str(datetime.now())                    
                    car = BeautifulSoup(urllib.request.urlopen('https://www.autoscout24.it'+URL).read(),'lxml')

                    test_car = BeautifulSoup(urllib.request.urlopen('https://www.autoscout24.it'+URL), 'html.parser')
                    images = test_car.find_all('img')
                    images = [image['src'] for image in images]
                    images = [image for image in images if image[0:5] == 'https'and image[-3:] == 'jpg']
                    images = [image.rsplit('/', 1) for image in images]
                    images = [image[0] for image in images]
                    n_images = len(images)

                    car_dict["image_list"] = images
                    car_dict["n_images"] = n_images                    
                    car_dict["locat"] = car.find("a",attrs={"class":"scr-link LocationWithPin_locationItem__pHhCa"}).text
                    
                    for key, value in zip(car.find_all("dt"),car.find_all("dd")):
                        if key.text == "Consumo di carburante":
                            valore = value.text.replace(")", "), ")
                            consumi = valore.split(", ", 2)
                            print(consumi[:len(consumi)])
                            car_dict[key.text.replace("\n","")] = valore
                        else:
                            car_dict[key.text.replace("\n","")] = re.sub(r"(\w)([A-Z])", r"\1 \2", value.text.replace("\n",""))


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
        df.to_csv("data/autos/"+re.sub("[.,:,-, ]","_",str(datetime.now()))+".csv",sep=",",index_label="url")
        print(df)
        print(df.shape)
        print(df.size)
    else:
        print("No Data\n\n")
    with open("data/visited/visited_urls.json", "w") as file:
        json.dump(visited_urls, file)