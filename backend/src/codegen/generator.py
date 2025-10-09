from typing import List
from ..parser.ast_nodes import *


class CodeGenerator:
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.current_function = None

    def generate(self, node: Node) -> str:
        """Генерирует JavaScript код из AST"""
        self.output = []
        self.indent_level = 0
        node.accept(self)
        return '\n'.join(self.output)

    def indent(self):
        """Увеличивает уровень отступа"""
        self.indent_level += 1

    def dedent(self):
        """Уменьшает уровень отступа"""
        self.indent_level -= 1

    def add_line(self, line: str = ""):
        """Добавляет строку с правильным отступом"""
        indent = '    ' * self.indent_level
        self.output.append(indent + line)

    def visit_program(self, node: Program):
        """Генерация кода для программы"""
        # Добавляем строгий режим для JavaScript
        self.add_line('"use strict";')
        self.add_line()

        # Генерируем все операторы
        for statement in node.statements:
            statement.accept(self)
            self.add_line()

    def visit_function_declaration(self, node: FunctionDeclaration):
        """Генерация кода для объявления функции"""
        self.current_function = node.name

        # Генерируем параметры
        params = ', '.join([param.name for param in node.parameters])

        self.add_line(f"function {node.name}({params}) {{")
        self.indent()

        # Генерируем тело функции
        node.body.accept(self)

        self.dedent()
        self.add_line("}")
        self.add_line()

        self.current_function = None

    def visit_variable_declaration(self, node: VariableDeclaration):
        """Генерация кода для объявления переменной"""
        if node.value:
            value_code = []
            node.value.accept(self)
            # Значение уже должно быть в output, но нам нужно его извлечь
            # Для упрощения будем генерировать значение отдельно
            from io import StringIO
            import sys

            old_output = self.output
            self.output = []
            node.value.accept(self)
            value_str = ' '.join(self.output).strip()
            self.output = old_output

            self.add_line(f"let {node.name} = {value_str};")
        else:
            self.add_line(f"let {node.name};")

    def visit_assignment(self, node: Assignment):
        """Генерация кода для присваивания"""
        target_code = []
        value_code = []

        # Сохраняем текущий вывод и генерируем целевое выражение
        old_output = self.output
        self.output = target_code
        node.target.accept(self)
        self.output = value_code
        node.value.accept(self)
        self.output = old_output

        target_str = ' '.join(target_code).strip()
        value_str = ' '.join(value_code).strip()

        self.add_line(f"{target_str} = {value_str};")

    def visit_binary_operation(self, node: BinaryOperation):
        """Генерация кода для бинарной операции"""
        left_code = []
        right_code = []

        # Сохраняем текущий вывод
        old_output = self.output

        # Генерируем левую часть
        self.output = left_code
        node.left.accept(self)

        # Генерируем правую часть
        self.output = right_code
        node.right.accept(self)

        # Восстанавливаем вывод
        self.output = old_output

        left_str = ' '.join(left_code).strip()
        right_str = ' '.join(right_code).strip()

        # Преобразуем операторы Python в JavaScript
        operator_map = {
            'and': '&&',
            'or': '||',
            '**': '**',
            '//': '/',  # Целочисленное деление - упрощаем до обычного деления
            'is': '===',
            'is not': '!=='
        }

        operator = operator_map.get(node.operator, node.operator)

        # Добавляем скобки для сложных выражений
        self.output.append(f"({left_str} {operator} {right_str})")

    def visit_unary_operation(self, node: UnaryOperation):
        """Генерация кода для унарной операции"""
        operand_code = []

        old_output = self.output
        self.output = operand_code
        node.operand.accept(self)
        self.output = old_output

        operand_str = ' '.join(operand_code).strip()

        operator_map = {
            'not': '!'
        }

        operator = operator_map.get(node.operator, node.operator)
        self.output.append(f"{operator}{operand_str}")

    def visit_identifier(self, node: Identifier):
        """Генерация кода для идентификатора"""
        self.output.append(node.name)

    def visit_literal(self, node: Literal):
        """Генерация кода для литерала"""
        if node.literal_type == DataType.STRING:
            self.output.append(f'"{node.value}"')
        elif node.literal_type == DataType.BOOLEAN:
            self.output.append(str(node.value).lower())
        elif node.literal_type == DataType.NONE:
            self.output.append("null")
        else:
            self.output.append(str(node.value))

    def visit_list_literal(self, node: 'ListLiteral'):
        """Генерация кода для литерала списка"""
        elements = []
        old_output = self.output

        for element in node.elements:
            self.output = []
            element.accept(self)
            elements.append(' '.join(self.output).strip())

        self.output = old_output
        self.output.append(f"[{', '.join(elements)}]")

    def visit_if_statement(self, node: IfStatement):
        """Генерация кода для условного оператора"""
        condition_code = []

        old_output = self.output
        self.output = condition_code
        node.condition.accept(self)
        self.output = old_output

        condition_str = ' '.join(condition_code).strip()

        self.add_line(f"if ({condition_str}) {{")
        self.indent()
        node.then_branch.accept(self)
        self.dedent()

        if node.else_branch:
            self.add_line("} else {")
            self.indent()
            node.else_branch.accept(self)
            self.dedent()

        self.add_line("}")

    def visit_while_loop(self, node: WhileLoop):
        """Генерация кода для цикла while"""
        condition_code = []

        old_output = self.output
        self.output = condition_code
        node.condition.accept(self)
        self.output = old_output

        condition_str = ' '.join(condition_code).strip()

        self.add_line(f"while ({condition_str}) {{")
        self.indent()
        node.body.accept(self)
        self.dedent()
        self.add_line("}")

    def visit_for_loop(self, node: ForLoop):
        """Генерация кода для цикла for"""
        iterable_code = []

        old_output = self.output
        self.output = iterable_code
        node.iterable.accept(self)
        self.output = old_output

        iterable_str = ' '.join(iterable_code).strip()

        # Преобразуем Python for-in в JavaScript for-of
        self.add_line(f"for (let {node.variable.name} of {iterable_str}) {{")
        self.indent()
        node.body.accept(self)
        self.dedent()
        self.add_line("}")

    def visit_block(self, node: Block):
        """Генерация кода для блока"""
        for statement in node.statements:
            statement.accept(self)

    def visit_expression_statement(self, node: ExpressionStatement):
        """Генерация кода для выражения-оператора"""
        old_output = self.output
        self.output = []
        node.expression.accept(self)
        expression_str = ' '.join(self.output).strip()
        self.output = old_output

        self.add_line(f"{expression_str};")

    def visit_return_statement(self, node: ReturnStatement):
        """Генерация кода для оператора return"""
        if node.value:
            value_code = []
            old_output = self.output
            self.output = value_code
            node.value.accept(self)
            self.output = old_output

            value_str = ' '.join(value_code).strip()
            self.add_line(f"return {value_str};")
        else:
            self.add_line("return;")

    def visit_import(self, node: Import):
        """Генерация кода для импорта"""
        # В JavaScript нет прямой аналогии import из Python
        # Генерируем комментарий для импорта
        self.add_line(f"// import {node.module_name}")

    def visit_function_call(self, node: FunctionCall):
        """Генерация кода для вызова функции"""
        args_code = []
        old_output = self.output

        for arg in node.arguments:
            self.output = []
            arg.accept(self)
            args_code.append(' '.join(self.output).strip())

        self.output = old_output

        args_str = ', '.join(args_code)

        # Специальная обработка для print
        if node.name.name == 'print':
            self.output.append(f"console.log({args_str})")
        else:
            self.output.append(f"{node.name.name}({args_str})")