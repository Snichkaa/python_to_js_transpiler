import unittest
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.lexer.lexer import Lexer
from backend.src.lexer.token_types import TokenType


class TestLexer(unittest.TestCase):

    def test_basic_tokens(self):
        """Тест базовых токенов"""
        code = "x = 5 + 3"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.VARIABLE,
            TokenType.ASSIGN,
            TokenType.INTEGER,
            TokenType.PLUS,
            TokenType.INTEGER,
            TokenType.EOF
        ]

        self.assertEqual(token_types, expected_types)

    def test_keywords(self):
        """Тест ключевых слов"""
        code = "if while for def"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        token_types = [token.type for token in tokens]
        expected_types = [
            TokenType.IF,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.DEF,
            TokenType.EOF
        ]

        self.assertEqual(token_types, expected_types)

    def test_numbers(self):
        """Тест числовых литералов"""
        code = "123 45.67 0.5"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        values = [token.value for token in tokens if token.type != TokenType.EOF]
        expected_values = ["123", "45.67", "0.5"]

        self.assertEqual(values, expected_values)

    def test_strings(self):
        """Тест строковых литералов"""
        code = '"hello" \'world\''
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        values = [token.value for token in tokens if token.type in [TokenType.STRING, TokenType.CHAR]]
        expected_values = ["hello", "world"]

        self.assertEqual(values, expected_values)

    def test_operators(self):
        """Тест операторов"""
        code = "+= -= == !="
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        values = [token.value for token in tokens if token.type != TokenType.EOF]
        expected_values = ["+=", "-=", "==", "!="]

        self.assertEqual(values, expected_values)

    def test_indentation(self):
        """Тест отступов"""
        code = """if True:
    x = 5
    y = 10"""
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        token_types = [token.type for token in tokens]
        # Должны быть INDENT и DEDENT токены
        self.assertIn(TokenType.INDENT, token_types)
        self.assertIn(TokenType.DEDENT, token_types)


if __name__ == '__main__':
    unittest.main()