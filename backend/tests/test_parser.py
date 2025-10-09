import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.lexer.lexer import Lexer
from backend.src.parser.parser import Parser
from backend.src.parser.ast_nodes import *


class TestParser(unittest.TestCase):

    def test_variable_assignment(self):
        """Тест парсинга присваивания переменной"""
        code = "x = 5"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], Assignment)

    def test_function_declaration(self):
        """Тест парсинга объявления функции"""
        code = """def hello(name):
                    return name"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], FunctionDeclaration)

        func_decl = ast.statements[0]
        self.assertEqual(func_decl.name, "hello")
        self.assertEqual(len(func_decl.parameters), 1)

    def test_if_statement(self):
        """Тест парсинга условного оператора"""
        code = "if x > 5:\n    y = 10\nelse:\n    y = 0"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], IfStatement)

    def test_while_loop(self):
        """Тест парсинга цикла while"""
        code = """while x < 10:
                    x = x + 1"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], WhileLoop)

    def test_binary_operations(self):
        """Тест парсинга бинарных операций"""
        code = "result = a + b * c"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.assertIsInstance(ast, Program)
        assignment = ast.statements[0]
        self.assertIsInstance(assignment, Assignment)
        self.assertIsInstance(assignment.value, BinaryOperation)


if __name__ == '__main__':
    unittest.main()