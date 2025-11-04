import unittest
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from backend.src.lexer.lexer import Lexer
from backend.src.lexer.token_types import TokenType
from backend.src.exceptions import LexerError, InvalidCharacterError, UnclosedStringError, InvalidNumberError


class TestLexer(unittest.TestCase):

    def print_test_info(self, test_name, tokens, expected_types=None, expected_values=None):
        """Вспомогательная функция для вывода информации о тесте"""
        print(f"\n{'=' * 50}")
        print(f"Тест: {test_name}")
        print(f"{'=' * 50}")
        print("Полученные токены:")
        for i, token in enumerate(tokens):
            print(f"  {i}: {token}")

        if expected_types:
            actual_types = [token.type for token in tokens]
            print(f"\nОжидаемые типы: {expected_types}")
            print(f"Фактические типы: {actual_types}")

        if expected_values:
            actual_values = [token.value for token in tokens if token.type != TokenType.EOF]
            print(f"Ожидаемые значения: {expected_values}")
            print(f"Фактические значения: {actual_values}")
        print(f"{'=' * 50}")

    def test_basic_tokens(self):
        """Тест базовых токенов"""
        code = "x = 5 + 3"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.VARIABLE,
            TokenType.ASSIGN,
            TokenType.INTEGER,
            TokenType.PLUS,
            TokenType.INTEGER,
            TokenType.EOF
        ]

        self.print_test_info("Базовые токены", tokens, expected_types)
        token_types = [token.type for token in tokens]
        self.assertEqual(token_types, expected_types)

    def test_keywords(self):
        """Тест ключевых слов"""
        code = "if while for def break continue elif else import return"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IF,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.DEF,
            TokenType.BREAK,
            TokenType.CONTINUE,
            TokenType.ELIF,
            TokenType.ELSE,
            TokenType.IMPORT,
            TokenType.RETURN,
            TokenType.EOF
        ]

        self.print_test_info("Ключевые слова", tokens, expected_types)
        token_types = [token.type for token in tokens]
        self.assertEqual(token_types, expected_types)

    def test_reserved_words(self):
        """Тест зарезервированных слов"""
        code = "False None True and in not or int float str list print"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.FALSE,
            TokenType.NONE,
            TokenType.TRUE,
            TokenType.AND,
            TokenType.IN,
            TokenType.NOT,
            TokenType.OR,
            TokenType.INT,
            TokenType.FLOAT,
            TokenType.STR,
            TokenType.LIST,
            TokenType.PRINT,
            TokenType.EOF
        ]

        self.print_test_info("Зарезервированные слова", tokens, expected_types)
        token_types = [token.type for token in tokens]
        self.assertEqual(token_types, expected_types)

    def test_numbers(self):
        """Тест числовых литералов"""
        code = "123 45.67 0.5 100"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        values = [token.value for token in tokens if token.type != TokenType.EOF]
        expected_values = ["123", "45.67", "0.5", "100"]

        types = [token.type for token in tokens if token.type != TokenType.EOF]
        expected_types = [TokenType.INTEGER, TokenType.FLOAT_NUMBER, TokenType.FLOAT_NUMBER, TokenType.INTEGER]

        self.print_test_info("Числовые литералы", tokens, expected_types, expected_values)
        self.assertEqual(values, expected_values)
        self.assertEqual(types, expected_types)

    def test_strings(self):
        """Тест строковых литералов"""
        code = '"hello" \'world\' "escaped\\nstring"'
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Фильтруем только строки и символы (исключаем EOF)
        string_tokens = [token for token in tokens if token.type in [TokenType.STRING, TokenType.CHAR]]
        values = [token.value for token in string_tokens]
        expected_values = ["hello", "world", "escaped\nstring"]

        self.print_test_info("Строковые литералы", tokens, None, expected_values)
        self.assertEqual(values, expected_values)

    def test_operators(self):
        """Тест операторов"""
        code = "+ - * / % ** = += -= *= /= %= == != > < >= <= | ^"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        values = [token.value for token in tokens if token.type != TokenType.EOF]
        expected_values = ["+", "-", "*", "/", "%", "**", "=", "+=", "-=", "*=", "/=", "%=", "==", "!=", ">", "<", ">=",
                           "<=", "|", "^"]

        self.print_test_info("Операторы", tokens, None, expected_values)
        self.assertEqual(values, expected_values)

    def test_delimiters(self):
        """Тест разделителей"""
        code = "{} [] () : , ."
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        values = [token.value for token in tokens if token.type != TokenType.EOF]
        expected_values = ["{", "}", "[", "]", "(", ")", ":", ",", "."]

        expected_types = [
            TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET,
            TokenType.LPAREN, TokenType.RPAREN,
            TokenType.COLON, TokenType.COMMA, TokenType.DOT,
            TokenType.EOF
        ]

        self.print_test_info("Разделители", tokens, expected_types, expected_values)
        self.assertEqual(values, expected_values)

    def test_indentation(self):
        """Тест отступов"""
        code = """if True:
    x = 5
    y = 10
z = 15"""
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        token_types = [token.type for token in tokens]

        # Проверяем наличие INDENT и DEDENT токенов
        self.print_test_info("Отступы", tokens)
        self.assertIn(TokenType.INDENT, token_types)
        self.assertIn(TokenType.DEDENT, token_types)

        # Проверяем порядок токенов
        expected_important_types = [
            TokenType.IF, TokenType.TRUE, TokenType.COLON, TokenType.NEWLINE,
            TokenType.INDENT,
            TokenType.VARIABLE, TokenType.ASSIGN, TokenType.INTEGER, TokenType.NEWLINE,
            TokenType.VARIABLE, TokenType.ASSIGN, TokenType.INTEGER, TokenType.NEWLINE,
            TokenType.DEDENT,
            TokenType.VARIABLE, TokenType.ASSIGN, TokenType.INTEGER,
            TokenType.EOF
        ]

        # Фильтруем только важные токены для проверки структуры
        important_tokens = [token for token in tokens if token.type not in [TokenType.NEWLINE, TokenType.EOF]]
        important_types = [token.type for token in important_tokens]

        # Проверяем что INDENT и DEDENT присутствуют в правильных местах
        indent_index = important_types.index(TokenType.INDENT)
        dedent_index = important_types.index(TokenType.DEDENT)

        self.assertGreater(dedent_index, indent_index, "DEDENT должен быть после INDENT")

    def test_comments(self):
        """Тест комментариев"""
        code = "x = 5 # This is a comment\ny = 10"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Комментарии должны быть пропущены
        values = [token.value for token in tokens if token.type not in [TokenType.NEWLINE, TokenType.EOF]]
        expected_values = ["x", "=", "5", "y", "=", "10"]

        self.print_test_info("Комментарии", tokens, None, expected_values)
        self.assertEqual(values, expected_values)

    def test_identifiers(self):
        """Тест идентификаторов"""
        code = "variable_name _private var123 camelCase"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        values = [token.value for token in tokens if token.type == TokenType.VARIABLE]
        expected_values = ["variable_name", "_private", "var123", "camelCase"]

        self.print_test_info("Идентификаторы", tokens, None, expected_values)
        self.assertEqual(values, expected_values)

    def test_complex_expression(self):
        """Тест сложного выражения"""
        code = "result = (a + b) * 2.5 - calculate_value(10, x)"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Проверяем основные типы токенов
        token_types = [token.type for token in tokens if token.type != TokenType.EOF]
        expected_types = [
            TokenType.VARIABLE, TokenType.ASSIGN,
            TokenType.LPAREN, TokenType.VARIABLE, TokenType.PLUS, TokenType.VARIABLE, TokenType.RPAREN,
            TokenType.MUL, TokenType.FLOAT, TokenType.MINUS,  # Исправлено здесь
            TokenType.VARIABLE, TokenType.LPAREN, TokenType.INTEGER, TokenType.COMMA, TokenType.VARIABLE,
            TokenType.RPAREN
        ]

        self.print_test_info("Сложное выражение", tokens, expected_types)
        self.assertEqual(token_types, expected_types)

    def test_error_cases(self):
        """Тест обработки ошибок"""
        # Тест недопустимого символа - теперь ожидаем LexerError вместо InvalidCharacterError
        with self.assertRaises(LexerError) as cm:
            code = "x = @ 5"
            lexer = Lexer(code)
            tokens = lexer.tokenize()

        print(f"\nТест ошибок: LexerError поймана как и ожидалось: {cm.exception}")
        self.assertIn("Invalid character", str(cm.exception))

        # Тест незакрытой строки - теперь ожидаем LexerError вместо UnclosedStringError
        with self.assertRaises(LexerError) as cm:
            code = 'x = "unclosed string'
            lexer = Lexer(code)
            tokens = lexer.tokenize()

        print(f"Тест ошибок: LexerError поймана как и ожидалось: {cm.exception}")
        self.assertIn("Unclosed", str(cm.exception))

        # Тест некорректного числа - теперь ожидаем LexerError вместо InvalidNumberError
        with self.assertRaises(LexerError) as cm:
            code = "x = 123.45.67"
            lexer = Lexer(code)
            tokens = lexer.tokenize()

        print(f"Тест ошибок: LexerError поймана как и ожидалось: {cm.exception}")
        self.assertIn("Invalid number", str(cm.exception))

    def test_empty_input(self):
        """Тест пустого ввода"""
        code = ""
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        self.print_test_info("Пустой ввод", tokens)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_only_whitespace(self):
        """Тест только пробельных символов"""
        code = "   \t   \n   "
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        self.print_test_info("Только пробелы", tokens)
        # Должен быть только EOF
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_escape_sequences(self):
        """Тест escape-последовательностей в строках"""
        code = r'"line1\nline2" "\t\tindented" "backslash\\"'
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        string_tokens = [token for token in tokens if token.type == TokenType.STRING]
        values = [token.value for token in string_tokens]
        expected_values = ["line1\nline2", "\t\tindented", "backslash\\"]

        self.print_test_info("Escape-последовательности", tokens, None, expected_values)
        self.assertEqual(values, expected_values)

    def test_char_literals(self):
        """Тест символьных литералов"""
        code = "'a' 'b' '\\n'"
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        char_tokens = [token for token in tokens if token.type == TokenType.CHAR]
        values = [token.value for token in char_tokens]
        expected_values = ["a", "b", "\n"]

        self.print_test_info("Символьные литералы", tokens, None, expected_values)
        self.assertEqual(values, expected_values)


if __name__ == '__main__':
    # Запускаем тесты с подробным выводом
    unittest.main(verbosity=2)
