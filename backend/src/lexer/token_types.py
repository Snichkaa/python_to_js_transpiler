from enum import Enum

class TokenType(Enum):
    # Ключевые слова
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    DEF = "DEF"
    ELIF = "ELIF"
    ELSE = "ELSE"
    FOR = "FOR"
    IF = "IF"
    IMPORT = "IMPORT"
    WHILE = "WHILE"
    RETURN = "RETURN"

    # Зарезервированные слова
    FALSE = "FALSE"
    NONE = "NONE"
    TRUE = "TRUE"
    INT = "INT"
    FLOAT = "FLOAT"
    STR = "STR"
    LIST = "LIST"
    PRINT = "PRINT"

    # Логические операторы
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IN = "IN"

    # Идентификаторы
    IDENTIFIER = "IDENTIFIER"
    VARIABLE = "VARIABLE"

    # Числовые литералы
    INTEGER = "INTEGER"
    FLOAT_NUMBER = "FLOAT"

    # Строковые литералы
    CHAR = "CHAR"
    STRING = "STRING"

    # Операторы
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    POW = "POW"
    ASSIGN = "ASSIGN"
    PLUS_ASSIGN = "PLUS_ASSIGN"
    MINUS_ASSIGN = "MINUS_ASSIGN"
    MUL_ASSIGN = "MUL_ASSIGN"
    DIV_ASSIGN = "DIV_ASSIGN"
    MOD_ASSIGN = "MOD_ASSIGN"
    EQ = "EQ"
    NE = "NE"
    GT = "GT"
    LT = "LT"
    GTE = "GTE"
    LTE = "LTE"
    BITWISE_OR = "BITWISE_OR"
    BITWISE_XOR = "BITWISE_XOR"

    # Разделители
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COLON = "COLON"
    COMMA = "COMMA"
    DOT = "DOT"

    # Строковые разделители
    SINGLE_QUOTE = "SINGLE_QUOTE"
    DOUBLE_QUOTE = "DOUBLE_QUOTE"

    # Специальные токены
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    INDENT = "INDENT"
    DEDENT = "DEDENT"


# Словари
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
    '*': TokenType.MUL,
    '/': TokenType.DIV,
    '%': TokenType.MOD,
    '**': TokenType.POW,
    '=': TokenType.ASSIGN,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.MUL_ASSIGN,
    '/=': TokenType.DIV_ASSIGN,
    '%=': TokenType.MOD_ASSIGN,
    '==': TokenType.EQ,
    '!=': TokenType.NE,
    '>': TokenType.GT,
    '<': TokenType.LT,
    '>=': TokenType.GTE,
    '<=': TokenType.LTE,
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