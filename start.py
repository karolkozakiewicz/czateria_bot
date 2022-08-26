from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from threading import Thread
import time
import logging
import json
#from BotConnect import BotConnect
import random
import datetime
#import pika
import threading
import wx
from ciekawostka import Ciekawostka

logging.basicConfig(level=logging.INFO, filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(levelname)s : %(asctime)s : %(message)s',
                    filename='Czateria.log')



class Czateria:
    # threading.Thread(target=Program_Gui, daemon=True).start()
    # print('Threading GUI started')
    def __init__(self, login, password, link):

        self.driver = self.chrome_options()
        self.driver.get(link)
        self.login = login
        self.MY_NICK = login
        self.password = password
        self.LAST_MESSAGE = ""
        self.load_files()
        # self.known_nicknames
        #self.bot = BotConnect()
        self.GREETING = False
        self.last_greeting_time = datetime.datetime.now()
        self.last_mention_time = datetime.datetime.now()
        self.currently_online_list = []
        self.chat_frame = None
        self.check_rodo()
        self.login_to_czateria_guest()
        self.threads = []
        self.all_messages = []
        self.read_messages_thread = ""
        self.guimessages = []
        self._get_frame_count_crash = 0
        self._main_loop_count_crash = 0
        self.ciekawostka = Ciekawostka()

    @staticmethod
    def chrome_options():
        """
        Options for Chrome driver
        Add options in arguments list
        :return:
        """
        chrome_options = Options()

        arguments = ['--test-type']

        for argument in arguments:
            chrome_options.add_argument(argument)

        driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
        return driver

    def nickname_add(self, nickname):
        nicknames = self.known_nicknames['people']['nicknames']
        if nickname not in nicknames:
            if self.MY_NICK not in nickname:
                nicknames.append(nickname)
                self.known_nicknames['people']['nicknames'] = nicknames
                with open('nicknames.json', 'w') as f:
                    json.dump(self.known_nicknames, f, indent=4)

    def load_files(self):
        """
        Creating nicknames.json if not exist.
        :return:
        """
        try:
            with open('nicknames.json', 'r') as f:
                self.known_nicknames = json.load(f)
        except:
            with open('nicknames.json', 'w') as f:
                f.write(json.dumps({"people": {"nicknames": ['value']}}, indent=4))

    def check_rodo(self):
        try:
            rodo_box = self.driver.find_element(By.XPATH, "//div[@class='rodo-popup']")
            button = rodo_box.find_element(By.XPATH, "//button[@class='rodo-popup-agree']").click()
        except Exception as e:
            print(f"Cannot find rodo button. {e}")

    def login_to_czateria_guest(self, guest=False):
        """
        TEGO TU NIE RUSZAĆ POD ŻADNYM POZOREM
        :param guest:
        :return:
        """
        try:
            time.sleep(2)
            if not guest:

                login_box = self.driver.find_element(By.XPATH , "//div[@id='login-box']")
                print(f"FOUND FOUND FOUND ==================== {login_box}")

                registered_nickname = login_box.find_element(By.XPATH, "//label[@class='login-entire-label']"
                                                                      "[@data-type='guest']")
                registered_nickname.click()

                login_forms = login_box.find_element(By.XPATH, "//div[@class='login-forms'][@id='login-forms']")
                login_input = login_forms.find_element(By.XPATH, "//input[@name='nick'][@id='nick-login']")
                password_input = login_forms.find_element(By.XPATH, "//input[@name='password'][@id='password-login']")
                enter_button = login_box.find_element(By.XPATH, "//input[@class='enter'][@id='enter-login']")

                login_input.send_keys(self.login)
                password_input.send_keys(self.password)

                enter_button.click()

                print('Successfully connected to chat.')
        except Exception as e:
            print(e)
            self.check_rodo()   
            self.login_to_czateria_guest()

    def load_people_list(self):
        """
        Refreshing page and creating list with online nicknames
        :return: list containing all online nicknames except admins and your own nicknames
        """
        try:

            people_online = self.driver.find_element(By.XPATH, "//div[@id='m-tab-main-container-1']"
                                                              "//div[@class='m-tabs-main-container']['m-osoby']"
                                                              "['m-user-list-primary']")

            each_person = people_online.find_elements(By.XPATH, "//div[@class='m-usersList-sublist']")

            self.currently_online_list = [person.get_attribute('textContent') for
                                          person in each_person[-1].find_elements(By.CLASS_NAME, 'm-list-user-item')]

            for person in self.currently_online_list:
                if person not in self.known_nicknames['people']['nicknames']:
                    if self.MY_NICK not in person:
                        self.nickname_add(person)
                        print(f"Added {person} to the nicknames.json")

        except Exception as e:
            print(f'{e} | Couldnt load nicknames.')
            exit(1)
            # self.load_people_list()

    def welcome_message(self, timeout=1):
        """
        Greeting messages
        ;param timeout (default float 0.5 second)
        """
        greting_start = ['No siemka', 'Eloszka', 'Cześć wam :)', 'Hejoooo', 'Bry', 'Hejcia naklejcia']
        greeting_end = ['Wrocilem', 'Jestem z powrotem', 'Tęskniłem :roll:', 'Powróciwszy :v']
        gif_list = ['<u-hjehje>', '<u-awes10>', '<u-hihih>', '<u-awes1>', '<u-meow>']
        time.sleep(timeout)
        self.chat_send_message(f'{random.choice(greting_start)}. {random.choice(greeting_end)} {random.choice(gif_list)}')
        self.GREETING = 1

    def greeting(self, statement=False):
        """
        Greeting message on first join
        :param statement:
        :return:
        """
        if statement:
            if not self.GREETING:
                # time.sleep(1)
                self.GREETING = True  # testy
                self.welcome_message()

    def chat_send_message(self, message, timeout=0.7):
        """
        :param message: string message
        ;param timeout (default float 0.5 second)
        """
        input_area = self.driver.find_element(By.XPATH, "//div[@id='m-tab-main-container-1']"
                                                       "//div[@class='m-tabs-main-container']"
                                                       "//form[@id='m-sendMessage']"
                                                       "//input[@placeholder='Wpisz wiadomość']")

        send_button = self.driver.find_element(By.XPATH, "//div[@id='m-tab-main-container-1']"
                                                        "//div[@class='m-tabs-main-container']"
                                                        "//form[@id='m-sendMessage']"
                                                        "//input[@value='Wyślij']")

        for letter in message:
            time.sleep(random.uniform(0.025, 0.053))
            input_area.send_keys(letter)
        time.sleep(timeout*2)
        send_button.click()

    def get_string_messages(self, messages):
        """
        Function removes trash from divs and returns list with string messages
        """
        div_messages_important_list = ['m-msg-item', 'm-msg-item accosted', 'm-msg-item m-msg-item--me']
        div_messages_ignore_list = ['m-msg-item-user-message', 'm-msg-item-user-login', 'm-msg-item-system']
        string_messages_list = []
        for div in messages:
            message_string = ""
            for letter in div.text:
                message_string += letter
            if div.get_attribute('class') in div_messages_important_list:
                if div.get_attribute('class') not in div_messages_ignore_list:
                    if 'Aktualny temat:' not in message_string:
                        if '~Witaj na CZATerii.' not in message_string:
                            string_messages_list.append(message_string)
        return string_messages_list

    def format_message(self, received_message):
        """
        Function removes all nicknames from the message.
        """
        received_message = received_message.split()
        nicknames_lower = [nick.lower() for nick in self.known_nicknames['people']['nicknames']]
        for nick in nicknames_lower:
            for word in received_message:
                if nick == word.lower() or self.MY_NICK == word.lower():
                    received_message.remove(word)
        message = ' '.join(received_message)
        return message

    def get_chat_frame(self):
        """
        This functions finds chat frame div in site HTML
        :return:
        """
        try:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//div[@id='m-tab-main-container-1']"
                                                          "//div[@class='m-tabs-main-container']"
                                                          "//div[@class='m-tab']")))

            chatting_frame = self.driver.find_element(By.XPATH, "//div[@id='m-tab-main-container-1']"
                                                               "//div[@class='m-tabs-main-container']"
                                                               "//div[@class='m-tab']")
            return chatting_frame

        except Exception as e:
            if count_crash <= 10:
                print(f"Cannot get the chat_frame. Function: get_chat_Frame. Retrying... {self._get_frame_count_crash}/10")
                time.sleep(1)
                self._get_frame_count_crash += 1
                self.get_chat_frame()  
            else:
                return 666
            

    def get_messages_continuously(self, chat_frame):
        """
        Function refreshes chat frame and returns all divs with messages
        """
        chat_messages = chat_frame.find_element(By.XPATH, "//div[@class='m-container']"
                                                                  "//div[@class='m-textArea']"
                                                                  "//div[@class='m-messagesTextArea']")
        # messages_old = chat_messages.find_elements_by_xpath("//div[@class='m-msg-item']")
        messages_div = chat_messages.find_elements(By.TAG_NAME, 'div')

        return messages_div

    def get_nick_message(self, message):
        """
        Function returns list with nick and message
        """
        nick = message[0][0:-1]
        message = ' '.join(message[1:])

        return [nick, message]

    def if_chat_silent(self, time):
        """
        Function sends random message on chat if noone is talking there
        """
        messages_list = ['Co taka cisza <u-oczi>', 'Halo? <u-oczi>',
                         'Cześć wam :3', ':roll:', 'jest ktoś?', 'wszyscy śpią :(']
        time_now = datetime.datetime.now()
        difference = time_now - self.last_greeting_time
        if difference.seconds > time:
            try:
                self.last_greeting_time = time_now
                self.chat_send_message(random.choice(messages_list).encode("utf-8"))
            except Exception:
                print("Cannot send message. Function: if_chat_silent")

    def last_mention(self, time):
        """
        Function sends reminder on chat if noone marked bot for {time} seconds
        """
        mention_list = ['HALO GURŁA','Nikt do mnie nie pisze :c', 'Co tam? :3', 'czemu ze mną nie piszecie :(']
        if (datetime.datetime.now()-self.last_mention_time).seconds > time:
            try:
                self.chat_send_message(random.choice(mention_list))
                self.last_mention_time = datetime.datetime.now()
            except Exception:
                print("Cannot send message. Function: last_mention")

    def enter_left_check(self, message):
        """
        Checks if message contains keywords.
        """
        keywords = ['+', '-']
        if message[0] in keywords:
            return True
        else:
            return False

    def destroy_inactive_thread(self):
        try:
            for thread in self.threads:
                if thread.is_alive() == False:
                    self.threads.remove(thread)
                    thread.join()


        except:
            pass

    def threaded_sending_message(self, nick, message):
        # print(f'started thread [ args ] : {nick} | {message}')
        self.bot.send(message)
        received_message = self.bot.receive()
        received_message = self.format_message(received_message)
        self.chat_send_message(f"{nick} {received_message}", timeout=1)

    def threaded_sending_message_without_output(self, nick, message):
        # print(f'started thread w/o [ args ] : {nick} | {message}')
        self.bot.send(message)
        received_message = self.bot.receive()

    def start_chat(self):
        """
        Function sets up chat frame and do things after joining to chat
        """
        
        try:
            
            self.chat_frame = self.get_chat_frame()
            self.greeting(False)
            self.load_people_list()
            self.main()
        except Exception as e:
            if self.chat_frame == 666:
                return 999

    def read_messages(self):
        messages = self.get_string_messages(self.get_messages_continuously(self.chat_frame))

    # def thread_read_messages(self):
    #     self.read_messages_thread = threading.Thread(target=self.read_messages, daemon=True, name=nick, args=(nick, message))

    def pick_insult(self):
        poczatek_zdania = ['ty', '', ' ', '', ' ']
        przymiotnik = ["głupi", "obszczany", "tępy", "brzydki", "bezmózgi"]
        rzeczownik = ["agencie", "alfonsie", "andersowcu", "bandyto", "becwale", "bekarcie", "Benderze", "bzdecie", "blizniaku jednojajowy", "bolszewiku", "buraku", "burku", "chamie", "chuliganie", "chuju zlamany", "cieciu", "ciemniaku", "cioto", "cipo", "ciulu", "cymbale", "cwelu", "debilu", "dupku sfalczaly", "dupo blada", "durniu", "dziuro w dupie", "dziwko", "elemencie", "elyto", "endeku", "eunuchu", "faszysto", "fizyku", "fiucie", "flecie", "frajerze", "fujaro", "Giertychu", "glabie", "glupolu", "gnido", "gnoju pod pieczarki", "goju", "gowniarzu", "gwalcicielu", "glizdo", "Heiderze", "Hitlerze", "huju", "idioto", "impotencie", "imbecylu", "intelektualisto", "Jaskiernio", "jebancu", "jezuito", "judaszu", "kacapie", "kalmuku", "kanalio", "kmiocie", "kretynie", "kutasie", "komuchu", "koniowale", "kurwo jebana", "kwachu", "lazego", "Leperze", "magistrze", "malpo", "matole", "mecie spoleczny", "medrku", "menelu", "mendo medialna", "Michniku", "mlocie", "morderco", "mosku", "mule", "narodowcu", "nurku smietnikowy", "obszczajmurze", "oszolomie", "palancie", "padalcu", "padlino", "parchu", "parobku", "pedale", "pedofilu", "pierdolcu", "pizdo", "poldupku", "pojebie", "probszczu", "prostaku", "prostytutko", "przekupniu", "przybledo", "przyglupie", "pseudomedrku", "psie", "robolu", "rolniku", "ruro krzywa", "rusku", "Rydzyku", "rynsztoku", "scierwo", "sklerozo", "skunksie", "skurwysynu", "smieciu", "smierdzielu", "swinio niemyta", "streczycielu", "szczylu", "szmato", "szujo", "szwabie", "tchorzu", "tepaku", "trabo", "trepie", "tumanie", "turku", "ubeku", "Urbanie", "walachu", "warchole", "wiesniaku", "wloczego", "wypierdku mamuta", "zapluty karle", "zasrancu", "zdrajco", "zgredzie", "zgnilizno", "zlobie", "zlodzieju", "zydozerco", "zydzie wszawy", "zygowino"]
        koncowka = ["tfu ci na ryj", "wyjdź stąd", "won z czatu", "j*eb się"]

        zdanie = random.choice(poczatek_zdania) + ' ' +random.choice(przymiotnik) + ' ' + random.choice(rzeczownik) + '. ' + random.choice(koncowka)
        return zdanie

    def check_if_bot_command(self, nick, text):
        message = text.split(' ')[1:]
        try:
            if 'quiz' in message[0].lower():
                if len(message) > 1:
                    if 'losuj' in message[1].lower():
                        self.ciekawostka.get_question()
                        zdanie = f"{self.ciekawostka.odpowiedzi}"
                        self.chat_send_message(f"{self.ciekawostka.kategoria}. {self.ciekawostka.pytanie}")
                        self.chat_send_message(zdanie)

                    if 'odpowiedz' in message[1].lower():
                        if len(message) > 2:
                            if message[2].lower() in ['A', 'B', 'C', 'D', 'a', 'b', 'c', 'd']:
                                if self.ciekawostka.sprawdz_odpowiedz(message[2].lower()):
                                    self.chat_send_message('Poprawna odpowiedź :)')

                                else:
                                    self.chat_send_message('Zła odpowiedź :(')



        except Exception as e:
            print(e)


    def main(self):
        crash = False
        crash_count = 0
        while True:
            """
            This loop refreshes chat and do all the work
            """
            self.if_chat_silent(180)
            self.last_mention(500)

            try:
                data1 = datetime.datetime.now()
                messages = self.get_string_messages(self.get_messages_continuously(self.chat_frame))
                self.guimessages = messages
                if not messages:
                    # If there are no messeges on chat, retry start_chat function.
                    self.start_chat()
                if messages[-1] not in self.LAST_MESSAGE:
                    self.destroy_inactive_thread()
                    self.LAST_MESSAGE = messages[-1]
                    self.last_greeting_time = datetime.datetime.now()
                    nick, message = self.get_nick_message(messages[-1].split(' '))
                    self.nickname_add(nick)
                    someone_enter_or_left_chat_message = self.enter_left_check(messages[-1].split(' '))
                    message = self.format_message(message)
                    
                    # Statement checks if phrase 'enter' or 'left' is in message.
                    if someone_enter_or_left_chat_message is False:
                        if len(self.format_message(self.get_nick_message(messages[-1].split(' '))[1])) > 0:
                            # If message isn't empty.
                            if self.MY_NICK.lower() not in nick.lower():
                                # If i'm not author of the message.
                                if self.MY_NICK.lower() in message.lower():
                                    self.check_if_bot_command(nick, message)
                                    # If someone mentioned me.
                                    try:
                                        print(f'{nick} : {message}')
                                        # self.chat_send_message(self.pick_insult())
                                    except Exception as e:
                                        print(e)
                                        print("Couldn't send message to bot[0]")
                                else:
                                    # If noone mentioned me, just send message to the bot without replying on chat.
                                    try:
                                        print(f'{nick} : {message}')

                                    except Exception as e:
                                        print(e)
                                        print("Couldn't send message to bot [1]")
                            
                                

                # print(f"\n{(datetime.datetime.now()-data1)} Zakonczona pętla. Usuwanie zakończonych wątków")
                self.destroy_inactive_thread()
            except Exception as e:
                if self._main_loop_count_crash > 15:
                    return 777
                print(f"Something went wrong in main function. Retrying... {self._main_loop_count_crash}/15")
                time.sleep(0.2)
                self._main_loop_count_crash += 1 
                self.start_chat()
                
        
                


czateria = Czateria('Pam_Bot', 'misiek08', 'https://czateria.interia.pl/emb-chat,room,247,Psychologia')
# czateria = Czateria('Pam_Bot', 'misiek08', 'https://czateria.interia.pl/emb-chat,room,311,M%C4%99%C5%BCowie%20i%20%C5%BCony')
# czateria = Czateria('Pam_Bot', 'misiek08', 'https://czateria.interia.pl/emb-chat,room,468,Ostr%C3%B3da')
# czateria = Czateria('Pam_Bot', 'misiek08', 'https://czateria.interia.pl/emb-chat,room,74,%C5%81%C3%B3d%C5%BA')
czateria.start_chat()


class Main(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        self.app = wx.App()

        f = wx.Frame(None)
        f.Show()
        self.app.MainLoop()
    
    def stop(self):
        Thread._stop(self)
        sys.exit()
        print('Pomyślnie zamknięto proces')
    

class Przegladarka(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        try:
            czateria = Czateria('Pam_Bot', 'misiek08', 'https://czateria.interia.pl/emb-chat,room,468,Ostr%C3%B3da')
            czateria.start_chat()
        except:
            self.stop()
    
    def stop(self):
        Thread._stop(self)
        sys.exit()
        print('Pomyślnie zamknięto proces')
    





# panel = wx.Panel(self)
# self.text_ctrl = wx.TextCtrl(panel, pos=(5, 5), size=(150, 150))
# my_btn = wx.Button(panel, label='Press me', pos=(160, 5))
        

# if __name__ == '__main__':
    
#     try:
#         p = Przegladarka()
#         p.start()
#         # t = Main()
#         # t.start()
#     except Exception as e:
#         p.stop()
        
#         # t.stop()
#         sys.exit()



    
    
    
    

