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

    def test_variable_declaration_without_value(self):
        """Тест генерации объявления переменной без значения"""
        python_code = "x = None"
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("let x = null", js_code)

    def test_multiple_variables(self):
        """Тест генерации нескольких переменных"""
        python_code = """
x = 5
y = "hello"
z = True
"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("let x = 5", js_code)
        self.assertIn('let y = "hello"', js_code)
        self.assertIn("let z = true", js_code)

    def test_function_declaration(self):
        """Тест генерации объявления функции"""
        python_code = """def greet(name):
    return "Hello, " + name"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("function greet(name)", js_code)
        self.assertIn("return", js_code)
        self.assertIn('"Hello, " + name', js_code)

    def test_function_with_multiple_parameters(self):
        """Тест генерации функции с несколькими параметрами"""
        python_code = """def calculate(a, b, c):
    return a + b * c"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("function calculate(a, b, c)", js_code)
        self.assertIn("return a + b * c", js_code)

    def test_function_without_return(self):
        """Тест генерации функции без возвращаемого значения"""
        python_code = """def log_message(msg):
    print(msg)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("function log_message(msg)", js_code)
        self.assertIn("console.log(msg)", js_code)

    def test_if_statement(self):
        """Тест генерации условного оператора"""
        python_code = """if x > 5:
    result = "big"
else:
    result = "small" """
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("if (x > 5)", js_code)
        self.assertIn("else", js_code)
        self.assertIn('result = "big"', js_code)
        self.assertIn('result = "small"', js_code)

    def test_while_loop(self):
        """Тест генерации цикла while"""
        python_code = """while x < 10:
    x = x + 1"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("while (x < 10)", js_code)
        self.assertIn("x = x + 1", js_code)

    def test_while_with_break_continue(self):
        """Тест генерации while с break и continue"""
        python_code = """while True:
    if x > 10:
        break
    if x < 0:
        continue
    x = x + 1"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("while (true)", js_code)
        self.assertIn("break", js_code)
        self.assertIn("continue", js_code)

    def test_for_loop(self):
        """Тест генерации цикла for"""
        python_code = """for item in items:
    print(item)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("for (let item of items)", js_code)
        self.assertIn("console.log(item)", js_code)

    def test_nested_for_loops(self):
        """Тест генерации вложенных циклов for"""
        python_code = """for i in range(3):
    for j in range(2):
        print(i, j)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("for (let i of range(3))", js_code)
        self.assertIn("for (let j of range(2))", js_code)

    def test_binary_operations(self):
        """Тест генерации бинарных операций"""
        python_code = """result = a + b * c - d / e"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("a + b * c - d / e", js_code)

    def test_logical_operations(self):
        """Тест генерации логических операций"""
        python_code = """result = (a > b) and (c < d) or (e == f)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("(a > b) && (c < d) || (e == f)", js_code)

    def test_unary_operations(self):
        """Тест генерации унарных операций"""
        python_code = """result = not flag
negative = -number"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("!flag", js_code)
        self.assertIn("-number", js_code)

    def test_function_calls(self):
        """Тест генерации вызовов функций"""
        python_code = """result = calculate(a, b, c)
print("Hello", name)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("calculate(a, b, c)", js_code)
        self.assertIn('console.log("Hello", name)', js_code)

    def test_list_literals(self):
        """Тест генерации литералов списков"""
        python_code = """numbers = [1, 2, 3, 4, 5]
names = ["Alice", "Bob", "Charlie"]"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("[1, 2, 3, 4, 5]", js_code)
        self.assertIn('["Alice", "Bob", "Charlie"]', js_code)

    def test_nested_lists(self):
        """Тест генерации вложенных списков"""
        python_code = """matrix = [[1, 2], [3, 4], [5, 6]]"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("[[1, 2], [3, 4], [5, 6]]", js_code)

    def test_boolean_literals(self):
        """Тест генерации булевых литералов"""
        python_code = """flag_true = True
flag_false = False"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("flag_true = true", js_code)
        self.assertIn("flag_false = false", js_code)

    def test_none_literal(self):
        """Тест генерации None"""
        python_code = """value = None"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("value = null", js_code)

    def test_string_operations(self):
        """Тест генерации операций со строками"""
        python_code = '''greeting = "Hello, " + name + "!"
message = "Value: " + str(value)'''
        js_code = self.transpiler.transpile(python_code)

        self.assertIn('"Hello, " + name + "!"', js_code)
        self.assertIn('"Value: " + str(value)', js_code)

    def test_complex_expression(self):
        """Тест генерации сложного выражения"""
        python_code = """result = (a + b) * (c - d) / (e % f) ** 2"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("(a + b) * (c - d) / (e % f) ** 2", js_code)

    def test_multiple_statements(self):
        """Тест генерации нескольких операторов"""
        python_code = """x = 5
y = 10
z = x + y
print(z)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("let x = 5", js_code)
        self.assertIn("let y = 10", js_code)
        self.assertIn("let z = x + y", js_code)
        self.assertIn("console.log(z)", js_code)

    def test_empty_function(self):
        """Тест генерации пустой функции"""
        python_code = """def empty_function():
    pass"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("function empty_function()", js_code)

    def test_comments_handling(self):
        """Тест обработки комментариев"""
        python_code = """# This is a comment
x = 5  # inline comment"""
        js_code = self.transpiler.transpile(python_code)

        # Комментарии должны игнорироваться или преобразовываться
        self.assertIn("let x = 5", js_code)

    def test_operator_precedence(self):
        """Тест приоритета операторов"""
        python_code = """result = a + b * c ** d - e / f"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("a + b * c ** d - e / f", js_code)

    def test_comparison_operators(self):
        """Тест операторов сравнения"""
        python_code = """result = (a == b) and (c != d) or (e > f) and (g < h) or (i >= j) and (k <= l)"""
        js_code = self.transpiler.transpile(python_code)

        self.assertIn("(a == b) && (c != d) || (e > f) && (g < h) || (i >= j) && (k <= l)", js_code)


if __name__ == '__main__':
    unittest.main()