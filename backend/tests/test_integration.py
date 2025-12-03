import unittest
import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.transpiler import Transpiler


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.transpiler = Transpiler()

    def test_hello_world(self):
        """Интеграционный тест: Hello World"""
        python_code = '''def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()'''

        js_code = self.transpiler.transpile(python_code)

        # Проверяем ключевые элементы
        self.assertIn('function main()', js_code)
        self.assertIn('console.log("Hello, World!")', js_code)
        self.assertIn('"use strict"', js_code)

    def test_fibonacci(self):
        """Интеграционный тест: числа Фибоначчи"""
        python_code = """def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)"""

        js_code = self.transpiler.transpile(python_code)

        self.assertIn('function fibonacci(n)', js_code)
        self.assertIn('if (n <= 1)', js_code)
        self.assertIn('return fibonacci(n - 1) + fibonacci(n - 2)', js_code)

    def test_calculator(self):
        """Интеграционный тест: простой калькулятор"""
        python_code = """def calculate(a, b, operation):
        if operation == "add":
            return a + b
        else:
            if operation == "subtract":
                return a - b
            else:
                if operation == "multiply":
                    return a * b
                else:
                    return a / b"""

        js_code = self.transpiler.transpile(python_code)

        self.assertIn('function calculate(a, b, operation)', js_code)
        # Исправляем здесь: меняем === на ==
        self.assertIn('if (operation == "add")', js_code)
        self.assertIn('operation == "subtract"', js_code)
        self.assertIn('operation == "multiply"', js_code)


if __name__ == '__main__':
    unittest.main()