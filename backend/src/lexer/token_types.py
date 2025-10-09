from enum import Enum

class TokenType(Enum):
    # Ключевые слова
    BREAK = "K1"
    CONTINUE = "K2"
    DEF = "K3"
    ELIF = "K4"
    ELSE = "K5"
    FOR = "K6"
    IF = "K7"
    IMPORT = "K8"
    WHILE = "K9"
    RETURN = "K10"

    # Зарезервированные слова
    FALSE = "R1"
    NONE = "R2"
    TRUE = "R3"
    INT = "R8"
    FLOAT = "R9"
    STR = "R10"
    LIST = "R11"
    PRINT = "R12"

    #Логические операторы
    AND = "R4"
    OR = "R7"
    NOT = "R6"
    IN = "R5"

    #Идентификаторы
    IDENTIFIER = "I1"
    VARIABLE = "I3"

    #Числовые литералы
    INTEGER = "N1"
    FLOAT_NUMBER = "N2"

    #Строковые литералы
    CHAR = "S1"
    STRING = "S2"

    #Операторы
    PLUS = "O1"
    MINUS = "O2"
    MULTIPLY = "O3"  # *
    DIVIDE = "O4"  # /
    MODULO = "O5"  # %
    POWER = "O6"  # **
    ASSIGN = "O7"  # =
    PLUS_ASSIGN = "O8"  # +=
    MINUS_ASSIGN = "O9"  # -=
    MULTIPLY_ASSIGN = "O10"  # *=
    DIVIDE_ASSIGN = "O11"  # /=
    MODULO_ASSIGN = "O12"  # %=
    EQUALS = "O13"  # ==
    NOT_EQUALS = "O14"  # !=
    GREATER = "O15"  # >
    LESS = "O16"  # <
    GREATER_EQUAL = "O17"  # >=
    LESS_EQUAL = "O18"  # <=
    BITWISE_OR = "O23"  # |
    BITWISE_XOR = "O24"  # ^

    #Разделители
    LBRACE = "D1"  # {
    RBRACE = "D2"  # }
    LBRACKET = "D3"  # [
    RBRACKET = "D4"  # ]
    LPAREN = "D5"  # (
    RPAREN = "D6"  # )
    COLON = "D7"  # :
    COMMA = "D8"  # ,
    DOT = "D9"

    #Строковые разделители
    SINGLE_QUOTE = "Q1"  # '
    DOUBLE_QUOTE = "Q2"  # "

    #Специальные токены
    NEWLINE = "NEWLINE"  #новая строка
    EOF = "EOF"  #конец файла
    INDENT = "INDENT"  #отступ
    DEDENT = "DEDENT"  #уменьшение отступа


#Словари
KEYWORDS = {
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'def': TokenType.DEF,
    'elif': TokenType.ELIF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'if': TokenType.IF,
    'import': TokenType.IMPORT,
    'while': TokenType.WHILE,
    'return': TokenType.RETURN,
}

RESERVED_WORDS = {
    'False': TokenType.FALSE,
    'None': TokenType.NONE,
    'True': TokenType.TRUE,
    'and': TokenType.AND,
    'in': TokenType.IN,
    'not': TokenType.NOT,
    'or': TokenType.OR,
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'str': TokenType.STR,
    'list': TokenType.LIST,
    'print': TokenType.PRINT,
}

OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '**': TokenType.POWER,
    '=': TokenType.ASSIGN,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.MULTIPLY_ASSIGN,
    '/=': TokenType.DIVIDE_ASSIGN,
    '%=': TokenType.MODULO_ASSIGN,
    '==': TokenType.EQUALS,
    '!=': TokenType.NOT_EQUALS,
    '>': TokenType.GREATER,
    '<': TokenType.LESS,
    '>=': TokenType.GREATER_EQUAL,
    '<=': TokenType.LESS_EQUAL,
    '|': TokenType.BITWISE_OR,
    '^': TokenType.BITWISE_XOR,
}

DELIMITERS = {
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    ':': TokenType.COLON,
    ',': TokenType.COMMA,
    '.': TokenType.DOT,
}