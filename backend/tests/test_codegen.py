import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.transpiler import Transpiler


class TestCodeGenerator(unittest.TestCase):

    def setUp(self):
        self.transpiler = Transpiler()

    def test_variable_assignment(self):
        """Тест генерации присваивания переменной"""
        python_code = "x = 5"
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("let x = 5", js_code)
        self.assertIn("use strict", js_code)

    def test_function_declaration(self):
        """Тест генерации объявления функции"""
        python_code = """def greet(name):
    return "Hello, " + name"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("function greet(name)", js_code)
        self.assertIn("return", js_code)

    def test_if_statement(self):
        """Тест генерации условного оператора"""
        python_code = """if x > 5:
    result = "big"
else:
    result = "small" """
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("if (x > 5)", js_code)
        self.assertIn("else", js_code)

    def test_while_loop(self):
        """Тест генерации цикла while"""
        python_code = """while x < 10:
    x = x + 1"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("while (x < 10)", js_code)

    def test_for_loop(self):
        """Тест генерации цикла for"""
        python_code = """for item in items:
    print(item)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("for (let item of items)", js_code)
        self.assertIn("console.log(item)", js_code)


if __name__ == '__main__':
    unittest.main()