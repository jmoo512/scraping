from flask import request
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime,timedelta
from urllib.parse import unquote
import requests,csv,re,jmespath,json

f = open('MRD.json', encoding="utf8")

json = json.load(f)

deckbox_url = input("Deckbox URL:")
deckbox_set_name = input("Deckbox Set Name:")
deckbox_set_id = input("Deckbox Set ID:")
cs_url = input("CS URL:")
cs_alt = input("CS ALTERNATE ART:")
cs_ext = input("CS EXTENDED ART:")
cs_promo = input("CS PROMO:")
cs_show = input("CS SHOWCASE:")
cs_bundle = input("CS BUNDLE:")


with open('mirrodin.csv', 'w', newline='') as csvfile:
    fieldnames=['Deckbox Card Name','Deckbox Card ID','Deckbox Set Name','Deckbox Set ID','Set Number','Is Foil','Cardsphere ID']
    card_writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
    card_writer.writeheader()

    deckbox_page=requests.get(deckbox_url)
    deckbox_soup=BeautifulSoup(deckbox_page.text,'html.parser')

    cs_page=requests.get(cs_url)
    cs_soup = BeautifulSoup(cs_page.text,'html.parser')

    cs_alt_page = requests.get(cs_alt)
    cs_alt_soup = BeautifulSoup(cs_alt_page.text, 'html.parser')

    cs_ext_page = requests.get(cs_ext)
    cs_ext_soup = BeautifulSoup(cs_ext_page.text, 'html.parser')

    cs_promo_page = requests.get(cs_promo)
    cs_promo_soup = BeautifulSoup(cs_promo_page.text, 'html.parser')

    cs_show_page = requests.get(cs_show)
    cs_show_soup = BeautifulSoup(cs_show_page.text, 'html.parser')

    cs_bundle_page = requests.get(cs_bundle)
    cs_bundle_soup = BeautifulSoup(cs_bundle_page.text, 'html.parser')

    row=deckbox_soup.find_all("tr")

    for i in row:
        try:
            num = i.find_all("td")[0].string.strip()
            number = num.partition("# ")[2]
            next = i.find_all("td")[1]
            a = next.find("a")
            href = a['href'].partition("=")[2]
            card_name = a['href'].partition("mtg/")[2]
            card_name = unquote(card_name.partition("?")[0])

            card_json = jmespath.search("data.cards[?number=='"+number+"']", json)

            if 'promopack' in card_json[0]['promoTypes']:
                cs_row=cs_promo_soup.find("a", class_="cardpeek", string=re.compile(card_name))
                cs_id = cs_row['href'].partition("cards/")[2]
                print(cs_id)
                print("Promo Pack")
            elif 'borderless' in card_json[0]['borderColor']:
                cs_row=cs_alt_soup.find("a", class_="cardpeek", string=re.compile(card_name))
                cs_id = cs_row['href'].partition("cards/")[2]
                print(cs_id)
                print("Borderless")
            elif 'extendedart' in card_json[0]['frameEffects']:
                cs_row=cs_ext_soup.find("a", class_="cardpeek", string=re.compile(card_name))
                cs_id = cs_row['href'].partition("cards/")[2]
                print(cs_id)
                print("Extended Art")
            elif 'showcase' in card_json[0]['frameEffects']:
                cs_row = cs_show_soup.find("a", class_="cardpeek", string=re.compile(card_name))
                cs_id = cs_row['href'].partition("cards/")[2]
                print(cs_id)
                print("Showcase")
            elif 'bundle' in card_json[0]['promoTypes']:
                cs_row = cs_bundle_soup.find("a", class_="cardpeek", string=re.compile(card_name))
                cs_id = cs_row['href'].partition("cards/")[2]
                print(cs_id)
                print("Bundle")
            else:
                cs_row=cs_soup.find("a", class_="cardpeek", string=re.compile(card_name))
                cs_id = cs_row['href'].partition("cards/")[2]

            card_writer.writerow({'Deckbox Card Name':card_name,'Deckbox Card ID':href,'Deckbox Set Name':deckbox_set_name,'Deckbox Set ID':deckbox_set_id,'Set Number':number,'Is Foil':False,'Cardsphere ID':cs_id})
            card_writer.writerow({'Deckbox Card Name':card_name,'Deckbox Card ID':href,'Deckbox Set Name':deckbox_set_name,'Deckbox Set ID':deckbox_set_id,'Set Number':number,'Is Foil':True,'Cardsphere ID':int(cs_id)-1})
        except:
            print("Didn't work, y no?")
