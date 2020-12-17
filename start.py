from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
import time
import logging
import json
from BotConnect import BotConnect
import random
import datetime
import pika
import threading


logging.basicConfig(level=logging.INFO, filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(levelname)s : %(asctime)s : %(message)s',
                    filename='Czateria.log')


class Rabbit:

    @staticmethod
    def send(message):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('vego.link',
                                      credentials=pika.PlainCredentials('spirit', 'misiek08')))
        channel = connection.channel()
        channel.exchange_declare(exchange='exchange', durable=True)

        channel.basic_publish(exchange='exchange',
                              routing_key='key',
                              body=message)
        print('Message sent to rabbit.')
        connection.close()


class Czateria:
    # threading.Thread(target=Program_Gui, daemon=True).start()
    # print('Threading GUI started')
    def __init__(self, login, password, link):

        self.driver = self.chrome_options()
        self.site = self.driver.get(link)
        self.login = login
        self.MY_NICK = login
        self.password = password
        self.LAST_MESSAGE = ""
        self.load_files()
        # self.known_nicknames
        self.bot = BotConnect()
        self.GREETING = False
        self.last_greeting_time = datetime.datetime.now()
        self.last_mention_time = datetime.datetime.now()
        self.currently_online_list = []
        self.chat_frame = None
        self.login_to_czateria_guest()
        self.threads = []



    @staticmethod
    def chrome_options():
        """
        Options for Chrome driver
        Add options in arguments list
        :return:
        """
        chrome_options = Options()

        arguments = ['--test-type', '--headless']

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

    def login_to_czateria_guest(self, guest=False):

        """
        TEGO TU NIE RUSZAĆ POD ŻADNYM POZOREM
        :param guest:
        :return:
        """
        try:
            time.sleep(2)
            if not guest:
                try:
                    popup = WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "rodo-popup")))
                    popup_exit = popup.find_element_by_class_name("close-x")
                    popup_exit.click()
                except Exception as e:
                    logging.error(f'Exception occured while {e}')
                    print("Could not find RODO-POPUP div.")

                login_box = self.driver.find_element_by_id("login-box")

                registered_nickname = login_box.find_element_by_xpath("//label[@class='login-entire-label']"
                                                                      "[@data-type='guest']")
                registered_nickname.click()

                login_forms = login_box.find_element_by_xpath("//div[@class='login-forms'][@id='login-forms']")
                login_input = login_forms.find_element_by_xpath("//input[@name='nick'][@id='nick-login']")
                password_input = login_forms.find_element_by_xpath("//input[@name='password'][@id='password-login']")
                enter_button = login_box.find_element_by_xpath("//input[@class='enter'][@id='enter-login']")

                login_input.send_keys(self.login)
                password_input.send_keys(self.password)

                enter_button.click()
        except Exception as e:
            print(e)
            self.login_to_czateria_guest()

    def load_people_list(self):
        """
        Refreshing page and creating list with online nicknames
        :return: list containing all online nicknames except admins and your own nicknames
        """
        try:

            people_online = self.driver.find_element_by_xpath("//div[@id='m-tab-main-container-1']"
                                                              "//div[@class='m-tabs-main-container']['m-osoby']"
                                                              "['m-user-list-primary']")

            each_person = people_online.find_elements_by_xpath("//div[@class='m-usersList-sublist']")

            self.currently_online_list = [person.get_attribute('textContent') for
                                          person in each_person[-1].find_elements_by_class_name('m-list-user-item')]

            for person in self.currently_online_list:
                if person not in self.known_nicknames['people']['nicknames']:
                    if self.MY_NICK not in person:
                        self.nickname_add(person)
                        print(f"Added {person} to the nicknames.json")

        except Exception as e:
            print(f'{e} | Couldnt load nicknames.')
            exit(1)
            # self.load_people_list()

    def welcome_message(self, timeout=0.5):
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

    def chat_send_message(self, message, timeout=1):
        """
        :param message: string message
        ;param timeout (default float 0.5 second)
        """
        input_area = self.driver.find_element_by_xpath("//div[@id='m-tab-main-container-1']"
                                                       "//div[@class='m-tabs-main-container']"
                                                       "//form[@id='m-sendMessage']"
                                                       "//input[@placeholder='Wpisz wiadomość']")

        send_button = self.driver.find_element_by_xpath("//div[@id='m-tab-main-container-1']"
                                                        "//div[@class='m-tabs-main-container']"
                                                        "//form[@id='m-sendMessage']"
                                                        "//input[@value='Wyślij']")

        input_area.send_keys(message)
        time.sleep(timeout)
        send_button.click()
        time.sleep(0.2)
        send_button.click()
        time.sleep(0.2)
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

            chatting_frame = self.driver.find_element_by_xpath("//div[@id='m-tab-main-container-1']"
                                                               "//div[@class='m-tabs-main-container']"
                                                               "//div[@class='m-tab']")
            return chatting_frame

        except Exception as e:
            print("Cannot get the chat_frame. Function: get_chat_Frame. Retrying...")
            time.sleep(1)
            self.get_chat_frame()

    def get_messages_continuously(self, chat_frame):
        """
        Function refreshes chat frame and returns all divs with messages
        """
        chat_messages = chat_frame.find_element_by_xpath("//div[@class='m-container']"
                                                                  "//div[@class='m-textArea']"
                                                                  "//div[@class='m-messagesTextArea']")
        # messages_old = chat_messages.find_elements_by_xpath("//div[@class='m-msg-item']")
        messages_div = chat_messages.find_elements_by_tag_name('div')

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
                self.chat_send_message(random.choice(messages_list))
            except Exception:
                print("Cannot send message. Function: if_chat_silent")

    def last_mention(self, time):
        """
        Function sends reminder on chat if noone marked bot for {time} seconds
        """
        mention_list = ['Nikt do mnie nie pisze :c', 'Co tam? :3', 'czemu ze mną nie piszecie :(']
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
                if not thread.is_active():
                    self.threads.remove(thread)
        except:
            pass

    def create_thread(self, nick, message, func_name):
        # print(f'created thread [ args ] : {nick} | {message} | {func_name}')
        self.threads.append(threading.Thread(target=func_name, daemon=True, args=(nick, message)).start())


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

    def read_chat(self):
        """
        Function sets up chat frame and do things after joining to chat
        """
        self.chat_frame = self.get_chat_frame()
        self.greeting(False)
        self.load_people_list()
        self.main()

    def main(self):
        while True:
            """
            This loop refreshes chat and do all the work
            """
            self.if_chat_silent(180)
            self.last_mention(600)

            try:
                messages = self.get_string_messages(self.get_messages_continuously(self.chat_frame))
                if not messages:
                    # If there are no messeges on chat, retry read_chat function.
                    self.read_chat()
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

                                    # If someone mentioned me.
                                    try:
                                        print(f'{nick} : {message}')
                                        self.create_thread(nick, message, self.threaded_sending_message)
                                        time.sleep(0.4)
                                    except Exception as e:
                                        print(e)
                                        print("Couldn't send message to bot[0]")
                                else:
                                    # If noone mentioned me, just send message to the bot without replying on chat.
                                    try:
                                        print(f'{nick} : {message}')
                                        self.create_thread(nick, message, self.threaded_sending_message_without_output)
                                        time.sleep(0.4)
                                    except Exception as e:
                                        print(e)
                                        print("Couldn't send message to bot [1]")
            except Exception as e:
                print("Something went wrong in main function. Retrying...")
                print(e)
                time.sleep(0.5)
                self.read_chat()


czateria = Czateria('Pam_Bot', 'misiek08', 'https://czateria.interia.pl/emb-chat,room,247,Psychologia')
#czateria = Czateria('Pam_Bot', 'misiek08', 'https://czateria.interia.pl/emb-chat,room,341,Kanada')
czateria.read_chat()
