import zmq

class BotConnect:

    def __init__(self):
        """
        Połączenie ze skryptem bota który działa na VPSie
        """
        context = zmq.Context()
        self.IP = 'ssh.vego.link'
        self.PORT = '19283'
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{self.IP}:{self.PORT}")
        print('Connected to bot.')

    def send(self, message: str):
        """
        Wysyła wiadomość w formacie bytes literal do bota
        :param message: str: wiadomość do wysłania
        """
        self.socket.send(message.encode())

    def receive(self) -> str:
        """
        Odbiera odpowiedź bota na wysłaną wcześniej wiadomość
        :return: str: wiadomość dekodowana do string
        """
        return self.socket.recv().decode()
