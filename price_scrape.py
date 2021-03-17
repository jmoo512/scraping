from flask import request
from pauper import db
from pauper.models import Cards, DeckList, SideBoard, DeckContent
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime,timedelta
import requests,csv

q=Cards.query.order_by(Cards.card_name).all()
with open('prices.csv', 'w', newline='') as csvfile:
    fieldnames=['Card','Old Price','New Price','Change']
    pricewriter=csv.DictWriter(csvfile,fieldnames=fieldnames)
    pricewriter.writeheader()
    for i in q:
        url='https://www.cardsphere.com/cards/'+str(i.cs_id)
        page=requests.get(url)
        soup=BeautifulSoup(page.text,'html.parser')
        price=soup.find_all("div", class_=["cs-col-xs-4", "cs-col-sm-4"])[0].get_text()
        price=price.replace('$','')
        price=float(price)
        change=i.price-price
        print(datetime.now().time(),i.card_name,i.price,price,change)
        pricewriter.writerow({'Card':i.card_name,'Old Price':price,'New Price':i.price,'Change':change})
        if price != i.price:
            i.price=price

        sleep(1)
db.session.commit()

decks=DeckContent.query.order_by(DeckContent.name).all()
for d in decks:

    card=DeckList.query.join(Cards,DeckList.card_name==Cards.card_name).add_columns(Cards.card_name,Cards.price,DeckList.card_qty).filter(DeckList.deck_name==d.name).all()
    sb=SideBoard.query.join(Cards,SideBoard.card_name==Cards.card_name).add_columns(Cards.card_name,Cards.price,SideBoard.card_qty).filter(SideBoard.deck_name==d.name).all()

    deck_price=0
    for i in card:
        deck_price=(i.card_qty*i.price)+deck_price

    sb_price=0
    for i in sb:
        sb_price=(i.card_qty*i.price)+sb_price

    total_price=deck_price+sb_price

    d.price=float(total_price)
    print (d.name, d.price)
    db.session.commit()
