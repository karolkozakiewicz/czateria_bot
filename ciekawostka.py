import requests
import random
from bs4 import BeautifulSoup
import json

class Ciekawostka():

    def __init__(self):
        self.generuj_kategorie()
        self.aktualna_kategoria = "entertainment"
        self.API = f"https://trivia.psycatgames.com/get-question?category={self.aktualna_kategoria}&lang=pl"
        


    def generuj_kategorie(self):
        self.kategorie = {'zabawa': 'entertainment/', 
                     'sztuka': 'arts/',
                     'styl życia': 'lifestyle/',
                     'sporty': 'sports/',
                     'nauki ścisłe': 'science/',
                     'język': 'language/',
                     'historia': 'history/',
                     'gry wideo': 'video-games/',
                     'gospodarka': 'economy/',
                     'geografia': 'hgeography/',
                     'fikcja': 'fiction'}

    def update_api(self):
        self.API = f"https://trivia.psycatgames.com/get-question?category={self.aktualna_kategoria}&lang=pl"     

    def site(self, kategoria):
        self.aktualna_kategoria = kategoria
        self.update_api()
        try:
            question_json = requests.get(self.API).text
        except:
            random_kategoria = random.choice([i for i in self.kategorie.keys()])
            self.aktualna_kategoria = random_kategoria
            question_json = requests.get(self.API).text
        
        self.set_question(question_json)
            
    def set_question(self, pytanie):
        pytanie = json.loads(pytanie)
        self.kategoria = pytanie['category']
        self.pytanie = pytanie['question']
        self.odpowiedzi = self.sortuj_odpowiedzi(pytanie['answers'])
        self.poprawna_odpowiedz = pytanie['correctAnswer']

        print(self.kategoria)
        print(self.pytanie)
        print(self.odpowiedzi)
        print(self.poprawna_odpowiedz)
            
    def sortuj_odpowiedzi(self, odpowiedzi):
        output = ""
        for odpowiedz in odpowiedzi.keys():
            output += f"{odpowiedzi[odpowiedz]} | "
        return output[:-2]

ciekawostka = Ciekawostka()

ciekawostka.site('zabawa')