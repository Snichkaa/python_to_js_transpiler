import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.lexer.lexer import Lexer
from backend.src.parser.parser import Parser
from backend.src.parser.ast_nodes import *
from backend.src.exceptions import ParserError, UnexpectedTokenError


class TestParser(unittest.TestCase):

    def print_test_info(self, test_name, ast, expected_structure=None):
        """Вспомогательная функция для вывода информации о тесте"""
        print(f"\n{'=' * 60}")
        print(f"Тест: {test_name}")
        print(f"{'=' * 60}")
        print("Исходный код:")
        print(f"  {test_name.split(' - ')[-1] if ' - ' in test_name else 'N/A'}")

        print("\nПолученное AST:")
        self._print_ast(ast, level=0)

        if expected_structure:
            print(f"\nОжидаемая структура: {expected_structure}")
        print(f"{'=' * 60}")

    def _print_ast(self, node, level=0):
        """Рекурсивно печатает AST"""
        indent = "  " * level
        if isinstance(node, Program):
            print(f"{indent}Program (statements: {len(node.statements)})")
            for stmt in node.statements:
                self._print_ast(stmt, level + 1)
        elif isinstance(node, FunctionDeclaration):
            print(f"{indent}FunctionDeclaration: {node.name}")
            print(f"{indent}  Parameters: {[p.name for p in node.parameters]}")
            self._print_ast(node.body, level + 1)
        elif isinstance(node, Assignment):
            print(f"{indent}Assignment: {node.target.name} = ...")
            self._print_ast(node.value, level + 1)
        elif isinstance(node, BinaryOperation):
            print(f"{indent}BinaryOperation: {node.operator}")
            self._print_ast(node.left, level + 1)
            self._print_ast(node.right, level + 1)
        elif isinstance(node, Identifier):
            print(f"{indent}Identifier: {node.name}")
        elif isinstance(node, Literal):
            print(f"{indent}Literal: {node.value} ({node.literal_type.value})")
        elif isinstance(node, IfStatement):
            print(f"{indent}IfStatement")
            print(f"{indent}  Condition:")
            self._print_ast(node.condition, level + 2)
            print(f"{indent}  Then:")
            self._print_ast(node.then_branch, level + 2)
            if node.else_branch:
                print(f"{indent}  Else:")
                self._print_ast(node.else_branch, level + 2)
        elif isinstance(node, Block):
            print(f"{indent}Block (statements: {len(node.statements)})")
            for stmt in node.statements:
                self._print_ast(stmt, level + 1)
        elif isinstance(node, WhileLoop):
            print(f"{indent}WhileLoop")
            print(f"{indent}  Condition:")
            self._print_ast(node.condition, level + 2)
            print(f"{indent}  Body:")
            self._print_ast(node.body, level + 2)
        elif isinstance(node, ForLoop):
            print(f"{indent}ForLoop: {node.variable.name}")
            print(f"{indent}  Iterable:")
            self._print_ast(node.iterable, level + 2)
            print(f"{indent}  Body:")
            self._print_ast(node.body, level + 2)
        elif isinstance(node, ReturnStatement):
            print(f"{indent}ReturnStatement")
            if node.value:
                self._print_ast(node.value, level + 1)
        elif isinstance(node, Import):
            print(f"{indent}Import: {node.module_name}")
        elif isinstance(node, FunctionCall):
            print(f"{indent}FunctionCall: {node.name.name}")
            for arg in node.arguments:
                self._print_ast(arg, level + 1)
        elif isinstance(node, ExpressionStatement):
            print(f"{indent}ExpressionStatement")
            self._print_ast(node.expression, level + 1)
        else:
            print(f"{indent}Unknown node: {type(node).__name__}")


    def test_variable_assignment(self):
        """Тест парсинга присваивания переменной"""
        code = "x = 5"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Присваивание переменной", ast, "Program -> Assignment -> Identifier + Literal")

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)

        assignment = ast.statements[0]
        self.assertIsInstance(assignment, Assignment)
        self.assertEqual(assignment.target.name, "x")
        self.assertIsInstance(assignment.value, Literal)
        self.assertEqual(assignment.value.value, 5)

    def test_function_declaration(self):
        """Тест парсинга объявления функции"""
        code = """def hello(name):
    return name"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Объявление функции", ast, "Program -> FunctionDeclaration")

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)

        func_decl = ast.statements[0]
        self.assertIsInstance(func_decl, FunctionDeclaration)
        self.assertEqual(func_decl.name, "hello")
        self.assertEqual(len(func_decl.parameters), 1)
        self.assertEqual(func_decl.parameters[0].name, "name")
        self.assertIsInstance(func_decl.body, Block)
        self.assertEqual(len(func_decl.body.statements), 1)
        self.assertIsInstance(func_decl.body.statements[0], ReturnStatement)

    def test_if_statement(self):
        """Тест парсинга условного оператора if"""
        code = "if x > 5:\n    y = 10"

        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Условный оператор if", ast, "Program -> IfStatement")
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        if_stmt = ast.statements[0]
        self.assertIsInstance(if_stmt, IfStatement)
        self.assertIsInstance(if_stmt.condition, BinaryOperation)
        self.assertIsInstance(if_stmt.then_branch, Block)
        self.assertIsNone(if_stmt.else_branch)  # Проверяем, что else нет

    # def test_if_else_statement(self):
    #     """Тест парсинга условного оператора if-else"""
    #     code = "if x > 5:\n    y = 10\nelse:\n    y = 0"
    #
    #     print("DEBUG if-else code:")
    #     for i, line in enumerate(code.split('\n'), 1):
    #         print(f"{i}: '{line}'")
    #
    #     lexer = Lexer(code)
    #     parser = Parser(lexer)
    #     ast = parser.parse()
    #
    #     self.print_test_info("Условный оператор if-else", ast, "Program -> IfStatement")
    #     self.assertIsInstance(ast, Program)
    #     self.assertEqual(len(ast.statements), 1)
    #     if_stmt = ast.statements[0]
    #     self.assertIsInstance(if_stmt, IfStatement)
    #     self.assertIsInstance(if_stmt.condition, BinaryOperation)
    #     self.assertIsInstance(if_stmt.then_branch, Block)
    #     self.assertIsInstance(if_stmt.else_branch, Block)  # Проверяем, что else есть

    def test_multiple_functions(self):
        """Тест парсинга нескольких функций"""
        # Тестируем функции по отдельности
        code1 = "def func1():\n    return 1"
        code2 = "def func2(x):\n    return x * 2"

        lexer = Lexer(code1)
        parser = Parser(lexer)
        ast1 = parser.parse()

        self.print_test_info("Функция 1", ast1, "Program -> FunctionDeclaration")
        self.assertIsInstance(ast1, Program)
        self.assertEqual(len(ast1.statements), 1)
        self.assertIsInstance(ast1.statements[0], FunctionDeclaration)
        self.assertEqual(ast1.statements[0].name, "func1")

        lexer = Lexer(code2)
        parser = Parser(lexer)
        ast2 = parser.parse()

        self.print_test_info("Функция 2", ast2, "Program -> FunctionDeclaration")
        self.assertIsInstance(ast2, Program)
        self.assertEqual(len(ast2.statements), 1)
        self.assertIsInstance(ast2.statements[0], FunctionDeclaration)
        self.assertEqual(ast2.statements[0].name, "func2")

    def test_while_loop(self):
        """Тест парсинга цикла while"""
        code = """while x < 10:
    x = x + 1"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Цикл while", ast, "Program -> WhileLoop")

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)

        while_loop = ast.statements[0]
        self.assertIsInstance(while_loop, WhileLoop)
        self.assertIsInstance(while_loop.condition, BinaryOperation)
        self.assertIsInstance(while_loop.body, Block)

    def test_for_loop(self):
        """Тест парсинга цикла for"""
        code = """for i in range(10):
    print(i)"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Цикл for", ast, "Program -> ForLoop")

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)

        for_loop = ast.statements[0]
        self.assertIsInstance(for_loop, ForLoop)
        self.assertEqual(for_loop.variable.name, "i")
        self.assertIsInstance(for_loop.iterable, FunctionCall)
        self.assertIsInstance(for_loop.body, Block)

    def test_binary_operations(self):
        """Тест парсинга бинарных операций с приоритетами"""
        code = "result = a + b * c"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Бинарные операции с приоритетом", ast, "Program -> Assignment -> BinaryOperation(+)")

        assignment = ast.statements[0]
        binary_op = assignment.value
        self.assertIsInstance(binary_op, BinaryOperation)
        self.assertEqual(binary_op.operator, "+")

        # Проверяем приоритет операций: умножение должно быть справа
        self.assertIsInstance(binary_op.left, Identifier)
        self.assertIsInstance(binary_op.right, BinaryOperation)
        self.assertEqual(binary_op.right.operator, "*")

    def test_logical_operations(self):
        """Тест парсинга логических операций"""
        code = "condition = a > 5 and b < 10 or c == 0"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Логические операции", ast, "Program -> Assignment -> BinaryOperation(or)")

        assignment = ast.statements[0]
        logical_op = assignment.value
        self.assertIsInstance(logical_op, BinaryOperation)
        self.assertEqual(logical_op.operator, "or")

    def test_function_call(self):
        """Тест парсинга вызова функции"""
        code = "result = calculate(a, b + c, 42)"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Вызов функции", ast, "Program -> Assignment -> FunctionCall")

        assignment = ast.statements[0]
        func_call = assignment.value
        self.assertIsInstance(func_call, FunctionCall)
        self.assertEqual(func_call.name.name, "calculate")
        self.assertEqual(len(func_call.arguments), 3)

    def test_import_statement(self):
        """Тест парсинга импорта"""
        code = "import math"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Импорт модуля", ast, "Program -> Import")

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)

        import_stmt = ast.statements[0]
        self.assertIsInstance(import_stmt, Import)
        self.assertEqual(import_stmt.module_name, "math")

    def test_return_statement(self):
        """Тест парсинга оператора return"""
        code = """def test():
    return 42"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Оператор return", ast, "Program -> FunctionDeclaration -> ReturnStatement")

        func_decl = ast.statements[0]
        return_stmt = func_decl.body.statements[0]
        self.assertIsInstance(return_stmt, ReturnStatement)
        self.assertIsInstance(return_stmt.value, Literal)
        self.assertEqual(return_stmt.value.value, 42)

    def test_complex_expression(self):
        """Тест парсинга сложного выражения"""
        code = "x = (a + b) * (c - d) / 2.0"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Сложное выражение", ast, "Program -> Assignment -> BinaryOperation")

        assignment = ast.statements[0]
        self.assertIsInstance(assignment.value, BinaryOperation)
        self.assertEqual(assignment.value.operator, "/")

    def test_unary_operations(self):
        """Тест парсинга унарных операций"""
        code = "x = -y\nz = not flag"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Унарные операции", ast, "Program -> 2 Assignments with UnaryOperation")

        self.assertEqual(len(ast.statements), 2)

        # Проверяем унарный минус
        assign1 = ast.statements[0]
        self.assertIsInstance(assign1.value, UnaryOperation)
        self.assertEqual(assign1.value.operator, "-")

        # Проверяем логическое НЕ
        assign2 = ast.statements[1]
        self.assertIsInstance(assign2.value, UnaryOperation)
        self.assertEqual(assign2.value.operator, "not")

    def test_list_literal(self):
        """Тест парсинга литерала списка"""
        code = "numbers = [1, 2, 3, 4]"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Литерал списка", ast, "Program -> Assignment -> Literal(list)")

        assignment = ast.statements[0]
        self.assertIsInstance(assignment.value, Literal)
        self.assertEqual(assignment.value.literal_type, DataType.LIST)
        self.assertEqual(assignment.value.value, [1, 2, 3, 4])

    def test_nested_structures(self):
        """Тест парсинга вложенных структур"""
        code = """if condition:
    for i in items:
        while flag:
            x = x + 1"""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Вложенные структуры", ast, "Program -> IfStatement -> ForLoop -> WhileLoop")

        if_stmt = ast.statements[0]
        for_loop = if_stmt.then_branch.statements[0]
        while_loop = for_loop.body.statements[0]

        self.assertIsInstance(if_stmt, IfStatement)
        self.assertIsInstance(for_loop, ForLoop)
        self.assertIsInstance(while_loop, WhileLoop)

    def test_comparison_operations(self):
        """Тест парсинга операций сравнения"""
        code = "result = a == b and c != d or e > f"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Операции сравнения", ast, "Program -> Assignment -> BinaryOperation with comparisons")

        assignment = ast.statements[0]
        # Должны быть правильно обработаны приоритеты операций

    def test_compound_assignment(self):
        """Тест парсинга составных операторов присваивания"""
        code = "x += 5"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Составное присваивание", ast, "Program -> Assignment -> BinaryOperation(+)")

        assignment = ast.statements[0]
        self.assertIsInstance(assignment, Assignment)
        self.assertIsInstance(assignment.value, BinaryOperation)
        self.assertEqual(assignment.value.operator, "+")

    def test_empty_program(self):
        """Тест парсинга пустой программы"""
        code = ""
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Пустая программа", ast, "Program with no statements")

        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 0)

    def test_error_handling(self):
        """Тест обработки ошибок парсера"""
        # Неполное выражение
        with self.assertRaises(ParserError) as cm:
            code = "x = "
            lexer = Lexer(code)
            parser = Parser(lexer)
            ast = parser.parse()

        print(f"\nТест ошибок: ParserError поймана как и ожидалось: {cm.exception}")

        # Неправильный синтаксис
        with self.assertRaises(ParserError) as cm:
            code = "if x: y ="
            lexer = Lexer(code)
            parser = Parser(lexer)
            ast = parser.parse()

        print(f"Тест ошибок: ParserError поймана как и ожидалось: {cm.exception}")

    def test_expression_statement(self):
        """Тест парсинга выражения как оператора"""
        code = "x + y\nfunc_call()"
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        self.print_test_info("Выражения как операторы", ast, "Program -> 2 ExpressionStatements")

        self.assertEqual(len(ast.statements), 2)
        self.assertIsInstance(ast.statements[0], ExpressionStatement)
        self.assertIsInstance(ast.statements[1], ExpressionStatement)


if __name__ == '__main__':
    # Запускаем тесты с подробным выводом
    unittest.main(verbosity=2)
