#!/usr/bin/env python3
import unittest
import sys
import os


def run_all_tests():
    """Запускает все тесты проекта"""

    # Добавляем путь к backend для импорта модулей
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

    # Находим все тестовые файлы
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('backend/tests', pattern='test_*.py')

    # Запускаем тесты
    print("Running Python to JS Transpiler Tests...")
    print("=" * 60)

    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Выводим итоговую статистику
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("All tests passed!")
        return True
    else:
        print("Some tests failed!")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False


def test_examples():
    """Тестирует примеры из папки examples"""
    print("\nTesting examples...")
    print("-" * 40)

    try:
        from backend.src.transpiler import Transpiler
        transpiler = Transpiler()

        examples_dir = 'examples'
        if not os.path.exists(examples_dir):
            print("Examples directory not found")
            return

        for root, dirs, files in os.walk(examples_dir):
            for file in files:
                if file.endswith('.py'):
                    py_file = os.path.join(root, file)
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            python_code = f.read()

                        js_code = transpiler.transpile(python_code)

                        # Сохраняем сгенерированный JS код
                        js_filename = file.replace('.py', '.js')
                        js_file = os.path.join(root, js_filename)

                        with open(js_file, 'w', encoding='utf-8') as f:
                            f.write(js_code)

                        print(f"Transpiled: {py_file} -> {js_file}")

                    except Exception as e:
                        print(f"Error transpiling {py_file}: {e}")

    except ImportError as e:
        print(f"Cannot import transpiler: {e}")


if __name__ == '__main__':
    # Запускаем unit-тесты
    tests_passed = run_all_tests()

    # Тестируем примеры (только если unit-тесты прошли)
    if tests_passed:
        test_examples()

    # Возвращаем код выхода для CI/CD
    sys.exit(0 if tests_passed else 1)