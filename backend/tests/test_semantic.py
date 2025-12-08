import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.lexer.lexer import Lexer
from backend.src.parser.parser import Parser
from backend.src.semantic.analyzer import SemanticAnalyzer
from backend.src.semantic.symbol_table import SymbolType, DataType
from backend.src.exceptions import UndefinedVariableError, RedeclarationError, TypeMismatchError


class TestSemanticAnalyzer(unittest.TestCase):

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.analyzer = SemanticAnalyzer()

    def _analyze_code(self, code):
        """Вспомогательный метод для анализа кода"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        return self.analyzer.analyze(ast), self.analyzer.errors

    def test_undefined_variable(self):
        """Тест обнаружения необъявленной переменной"""
        print("=== Тест: необъявленная переменная ===")
        code = "x = y + 5"  # y не объявлена
        result, errors = self._analyze_code(code)

        self.assertFalse(result)
        self.assertGreater(len(errors), 0)
        self.assertIsInstance(errors[0], UndefinedVariableError)
        print(f"✓ Ошибка обнаружена: {errors[0]}")
        print()

    def test_valid_program(self):
        """Тест корректной программы"""
        print("=== Тест: корректная программа ===")
        codes = [
            "x = 5",
            "def test(): return 5",
            "x = 5\ny = x + 1"
        ]

        all_passed = True
        for code in codes:
            self.analyzer = SemanticAnalyzer()
            result, errors = self._analyze_code(code)
            if not result:
                print(f"✗ Ошибка в: {code}")
                for error in errors:
                    print(f"  - {error}")
                all_passed = False

        self.assertTrue(all_passed)
        print("✓ Программы прошли семантический анализ без ошибок")
        print()

    def test_type_compatibility(self):
        """Тест проверки совместимости типов"""
        print("=== Тест: совместимость типов ===")
        code = "x = 5 + 'hello'"  # Сложение числа и строки
        result, errors = self._analyze_code(code)

        self.assertFalse(result)
        self.assertGreater(len(errors), 0)
        type_errors = [e for e in errors if isinstance(e, TypeMismatchError)]
        self.assertGreater(len(type_errors), 0)
        print(f"✓ Ошибка типов обнаружена: {type_errors[0]}")
        print()

    def test_variable_redeclaration(self):
        """Тест повторного объявления переменной"""
        print("=== Тест: повторное объявление переменной ===")
        code = "x = 5\nx = 'hello'"  # Переопределение в одной области видимости
        result, errors = self._analyze_code(code)

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Переприсваивание переменной обработано корректно")
        print()

    def test_function_declaration(self):
        """Тест объявления функции"""
        print("=== Тест: объявление функции ===")
        code = "def add(a, b): return a + b"
        result, errors = self._analyze_code(code)

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Объявление функции обработано корректно")
        print()

    def test_function_redeclaration(self):
        """Тест повторного объявления функции"""
        print("=== Тест: повторное объявления функции ===")
        code = "def test(): return 1\ndef test(): return 2"
        result, errors = self._analyze_code(code)

        self.assertFalse(result)
        self.assertGreater(len(errors), 0)
        self.assertIsInstance(errors[0], RedeclarationError)
        print(f"✓ Ошибка повторного объявления обнаружена: {errors[0]}")
        print()

    def test_parameter_scope(self):
        """Тест области видимости параметров функции"""
        print("=== Тест: область видимости параметров ===")
        code = "def process_data(data): return data * 2"
        result, errors = self._analyze_code(code)

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Область видимости параметров обработана корректно")
        print()

    def test_if_statement_semantic(self):
        """Тест семантики условного оператора"""
        print("=== Тест: семантика условного оператора ===")
        code = "x = 10\nif x > 5: result = 'greater'"
        result, errors = self._analyze_code(code)

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Условный оператор проанализирован корректно")
        print()

    def test_while_loop_semantic(self):
        """Тест семантики цикла while"""
        print("=== Тест: семантика цикла while ===")
        code = "counter = 0\nwhile counter < 5: counter = counter + 1"
        result, errors = self._analyze_code(code)

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Цикл while проанализирован корректно")
        print()

    def test_for_loop_semantic(self):
        """Тест семантики цикла for"""
        print("=== Тест: семантика цикла for ===")
        # Упрощенный тест с предварительным объявлением переменной
        code = """
items = [1, 2, 3]
i = 0
for i in items: 
    print(i)
"""
        result, errors = self._analyze_code(code)

        if result:
            print("✓ Цикл for проанализирован корректно")
        else:
            print(f"✗ Ошибки в цикле for: {errors}")

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print()

    def test_builtin_functions(self):
        """Тест встроенных функций"""
        print("=== Тест: встроенные функции ===")

        test_cases = [
            "print('Hello')",
        ]

        all_passed = True
        for code in test_cases:
            self.analyzer = SemanticAnalyzer()
            result, errors = self._analyze_code(code)
            if not result:
                print(f"✗ Ошибка в: {code}")
                for error in errors:
                    print(f"  - {error}")
                all_passed = False
            else:
                print(f"✓ Встроенная функция обработана: {code}")

        self.assertTrue(all_passed)
        print("✓ Все встроенные функции обработаны корректно")
        print()

    def test_return_statement(self):
        """Тест оператора return"""
        print("=== Тест: оператор return ===")
        code = "def get_value(): return 42"
        result, errors = self._analyze_code(code)

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Оператор return проанализирован корректно")
        print()

    def test_nested_scopes(self):
        """Тест вложенных областей видимости"""
        print("=== Тест: вложенные области видимости ===")

        # Тест с настоящей вложенной функцией
        code = """
    def outer():
        x = 10

        def inner():
            return x + 5

        return inner()
    """
        print("Код для анализа:")
        print(code)

        result, errors = self._analyze_code(code)

        if not result:
            print("Ошибки анализа:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✓ Вложенные функции проанализированы без ошибок")

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Вложенные области видимости обработаны корректно")
        print()

    def test_binary_operations_type_checking(self):
        """Тест проверки типов в бинарных операциях"""
        print("=== Тест: проверка типов в бинарных операциях ===")

        valid_codes = [
            "a = 5 + 3",
            "b = 2 * 4",
            "c = True and False",
            "d = 'hello' + 'world'"
        ]

        all_valid_passed = True
        for code in valid_codes:
            self.analyzer = SemanticAnalyzer()
            result, errors = self._analyze_code(code)
            if not result:
                print(f"✗ Ошибка в корректной операции: {code}")
                for error in errors:
                    print(f"  - {error}")
                all_valid_passed = False
            else:
                print(f"✓ Корректная операция: {code}")

        self.assertTrue(all_valid_passed)
        print("✓ Корректные бинарные операции приняты")

        invalid_codes = [
            "x = 5 + 'text'",
            "y = True - False",
            "z = 'hello' * 'world'"
        ]

        invalid_errors_count = 0
        for code in invalid_codes:
            self.analyzer = SemanticAnalyzer()
            result, errors = self._analyze_code(code)
            invalid_errors_count += len(errors)
            if not result:
                print(f"✓ Некорректная операция отклонена: {code}")

        self.assertGreater(invalid_errors_count, 0)
        print(f"✓ Некорректные операции отклонены: {invalid_errors_count} ошибок")
        print()

    def test_complex_expression_analysis(self):
        """Тест анализа сложных выражений"""
        print("=== Тест: анализ сложных выражений ===")
        code = "def calculate(a, b, c): return (a + b) * c - (a / b)"
        result, errors = self._analyze_code(code)

        self.assertTrue(result)
        self.assertEqual(len(errors), 0)
        print("✓ Сложные выражения проанализированы корректно")
        print()

    def test_error_recovery(self):
        """Тест восстановления после ошибок"""
        print("=== Тест: восстановление после ошибок ===")
        codes_with_errors = [
            "x = undefined_var",
            "y = 5 + 'text'",
            "z = 10"
        ]

        total_errors = 0
        for code in codes_with_errors:
            self.analyzer = SemanticAnalyzer()
            result, errors = self._analyze_code(code)
            total_errors += len(errors)
            print(f"Код: {code} -> Ошибок: {len(errors)}")

        self.assertGreaterEqual(total_errors, 2)
        print(f"✓ Обнаружено {total_errors} ошибок, анализ продолжен")
        print()

    def test_symbol_table_integrity(self):
        """Тест целостности таблицы символов"""
        print("=== Тест: целостность таблицы символов ===")
        codes = [
            "global_var = 1",
            "def func1(param1): return param1 + 1",
            "def func2(): return global_var * 2"
        ]

        all_passed = True
        for code in codes:
            result, errors = self._analyze_code(code)
            if not result:
                print(f"✗ Ошибка в: {code}")
                for error in errors:
                    print(f"  - {error}")
                all_passed = False

        self.assertTrue(all_passed)
        print("✓ Таблица символов сохраняет целостность")
        print()


if __name__ == '__main__':
    print("Запуск семантических тестов...")
    print("=" * 50)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSemanticAnalyzer)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 50)
    print(f"ИТОГИ:")
    print(f"Тестов запущено: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")

    if not result.wasSuccessful():
        print("\nДетали ошибок:")
        for test, traceback in result.failures + result.errors:
            print(f"\n{test}:")
            print(traceback)