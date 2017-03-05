#coding:utf-8
import requests
from bs4 import BeautifulSoup
import re
import unicodecsv as csv

def link(x):
    return "http://r.pl"+re.sub("\?.*$","", x.find("a")['href'])

def departure_date(x):
     m = re.search("\d\d\.\d\d.\d\d\d\d",x.find(class_="icon-terminwyjazdu").text)
     return m.group() if m else ""

def name(x):
    return x.find(class_="oferta-nazwa").find("h5").text

def country(x):
    return x.find(class_="oferta-nazwa").find("h6").find("a").text

def region(x):
    y = x.find(class_="oferta-nazwa").find("h6").find_all("a")
    return y[1].text if len(y)>1 else ""

def trip_type(x):
    return x.find(class_="icon-typwycieczki").text

def price_and_duration_list(x):
    result = []
    for y in x.find_all(class_="cena-opcja"):
        price = "".join(re.findall("\d+", y.find(class_="cena-wartosc").text))
        days = sum(map(lambda s: int(s), re.findall("\d+", y.find(class_="cena-opis").text)))
        duration_text = y.find(class_="cena-opis").text
        result.append((price, days, duration_text))
    return result

record_headers = "country,region,name,link,departure_date,days,duration_text,trip_type,price".split(",")

def records_from_node(x):
    result = []
    for (price,days,duration_text) in price_and_duration_list(x):
        record = {}
        record['price'] = price
        record['days'] = days
        record['duration_text'] = duration_text
        record['link'] = link(x)
        record['departure_date'] = departure_date(x)
        record['name'] = name(x)
        record['country'] = country(x)
        record['region'] = region(x)
        record['trip_type'] = trip_type(x)
        result.append(record)
    return result

def url(page=1):
    return "http://r.pl/oferty/szukaj?strona=%s"%(page)

def get_page_count():
    return int(BeautifulSoup(requests.get(url(1)).text, 'html.parser').find(class_="pagination").find(class_="last").text)

def get_offers_soup(i):
    return BeautifulSoup(requests.get(url(i)).text, 'html.parser').find_all("div", class_="oferta")

def all_records_in_page(i):
    return (record for offer in get_offers_soup(i) for record in records_from_node(offer))

def all_records():
    return (record for i in range(1, get_page_count()+1) for record in all_records_in_page(i) )

def dump_out(outfile="out.csv"):
    with open(outfile, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=record_headers)
        writer.writeheader()
        for record in all_records():
            writer.writerow(record)

if __name__ == "__main__":
    dump_out()
