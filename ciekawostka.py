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

    def get_question(self, kategoria=None):
        if kategoria == None:
            try:
                kategoria = random.choice([i for i in self.kategorie.keys()])
            except:
                kategoria = 'lifestyle'

        self.aktualna_kategoria = kategoria
        self.update_api()
        try:
            question_json = requests.get(self.API).text
        except:
            print('Blad przy kategoriach')
            random_kategoria = random.choice([i for i in self.kategorie.keys()])
            self.aktualna_kategoria = random_kategoria
            question_json = requests.get(self.API).text
        
        self.set_question(question_json)
            
    def set_question(self, pytanie):
        pytanie = json.loads(pytanie)
        self.kategoria = pytanie['category']
        self.pytanie = pytanie['question']
        self.poprawna_odpowiedz = pytanie['correctAnswer']
        self.literka_poprawnej_odpowiedzi = ""
        self.odpowiedzi = self.sortuj_odpowiedzi(pytanie['answers'])

    def sprawdz_odpowiedz(self, odpowiedz):
        if odpowiedz == self.literka_poprawnej_odpowiedzi:
            return True

    def sortuj_odpowiedzi(self, odpowiedzi):
        output = ""
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F']
        for i, odpowiedz in enumerate(odpowiedzi.keys()):
            
            if self.poprawna_odpowiedz in odpowiedzi[odpowiedz]:
                self.literka_poprawnej_odpowiedzi = odpowiedz
            output += f"{alphabet[i]}. {odpowiedzi[odpowiedz]} | "
        return output[:-2]

    def print_all(self):
        print(self.kategoria)
        print(self.pytanie)
        print(self.odpowiedzi)
        print(self.poprawna_odpowiedz)
        print(self.literka_poprawnej_odpowiedzi)

