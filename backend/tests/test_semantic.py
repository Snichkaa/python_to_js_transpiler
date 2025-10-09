import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.lexer.lexer import Lexer
from backend.src.parser.parser import Parser
from backend.src.semantic.analyzer import SemanticAnalyzer


class TestSemanticAnalyzer(unittest.TestCase):

    def test_undefined_variable(self):
        """Тест обнаружения необъявленной переменной"""
        code = "x = y + 5"  # y не объявлена
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)

        self.assertFalse(result)
        self.assertGreater(len(analyzer.errors), 0)

    def test_valid_program(self):
        """Тест корректной программы"""
        code = """def test():
    x = 5
    return x"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)

        self.assertTrue(result)
        self.assertEqual(len(analyzer.errors), 0)

    def test_type_compatibility(self):
        """Тест проверки совместимости типов"""
        code = """x = 5
y = "hello"
z = x + y"""  # Сложение числа и строки
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)

        # В Python это допустимо, но у нас строгая проверка
        self.assertFalse(result)
        self.assertGreater(len(analyzer.errors), 0)


if __name__ == '__main__':
    unittest.main()