import pyautogui
from time import sleep

COLON = 'COLON'
KEY = 'KEY'
KEYS = 'KEYS'
COMMAND = 'COMMAND'
TIME = 'TIME'
LOOP = 'LOOP'
END = 'END'
PLUS = 'PLUS'
NUMBER = 'NUMBER'
QUOTE = 'QUOTE'
COMMA = 'COMMA'
EOF = 'EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self.__str__()

RESERVERD_KEYWORDS = {
    ':k': Token('KEY', ':k'),
    ':c': Token('COMMAND', ':c'),
    ':t': Token('TIME', ':t'),
    ':l': Token('LOOP', ':l'),
    ':e': Token('END', ':e')
}


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid Character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char  = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def keys(self):
        result = ''
        while self.current_char is not None and self.current_char != '\'':
            result += self.current_char
            self.advance()

        return Token(KEYS, result)

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        token = Token(NUMBER, int(result))

        return token

    def statement(self):
        self.advance()

        token = RESERVERD_KEYWORDS[':'+self.current_char]
        self.advance()

        return token

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                return self.keys()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == ':':
                return self.statement()

            if self.current_char == '\'':
                self.advance()
                return Token(QUOTE, '\'')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            self.error()

        return Token(EOF, None)

class Parser:
    def  __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid Syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        self.statement_list()

    def statement_list(self):
        self.statement()

        while self.current_token.type in [KEY, COMMAND, TIME, LOOP, END]:
            self.statement()

    def statement(self):
        if self.current_token.type == KEY:
            self.eat(KEY)
            self.key()
        elif self.current_token.type == COMMAND:
            self.eat(COMMAND)
            self.commands()
        elif self.current_token.type == TIME:
            self.eat(TIME)
            self.time()
        elif self.current_token.type == LOOP:
            self.eat(LOOP)
            self.loop()
        elif self.current_token.type == END:
            self.eat(END)

    def key(self):
        self.eat(QUOTE)
        pyautogui.typewrite(self.current_token.value, interval=0)
        self.eat(KEYS)
        self.eat(QUOTE)

    def commands(self):
        self.command()

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            self.command()

    def command(self):
        commands = []

        self.eat(QUOTE)
        commands.append(self.current_token.value)
        self.eat(KEYS)
        self.eat(QUOTE)

        while self.current_token.type == PLUS:
            self.eat(PLUS)
            self.eat(QUOTE)
            commands.append(self.current_token.value)
            self.eat(KEYS)
            self.eat(QUOTE)

        pyautogui.hotkey(*commands)

    def time(self):
        number = self.current_token.value
        self.eat(NUMBER)

        sleep(number)

    def loop(self):
        number = self.current_token.value
        self.eat(NUMBER)

        start_token = self.current_token
        start_pos = self.lexer.pos
        end_token = None
        end_pos = None

        for x in range(0, number):
            self.statement_list()
            end_pos = self.lexer.pos
            end_token = self.current_token
            self.lexer.pos = start_pos
            self.current_token = start_token
            self.lexer.current_char = self.lexer.text[start_pos]


        self.lexer.pos = end_pos
        self.current_token = end_token


def run(text):
    Parser(Lexer(text)).program()
