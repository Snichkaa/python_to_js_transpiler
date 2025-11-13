from typing import List
from backend.src.parser.ast_nodes import *


class CodeGenerator:
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.declared_variables = set()  # Отслеживаем объявленные переменные

    def generate(self, node: Node) -> str:
        """Генерирует JavaScript код из AST"""
        print(f"DEBUG GENERATOR: Starting code generation for {type(node).__name__}")
        if hasattr(node, 'statements'):
            print(f"DEBUG GENERATOR: Number of statements: {len(node.statements)}")
            for i, stmt in enumerate(node.statements):
                print(f"DEBUG GENERATOR: Statement {i}: {type(stmt).__name__}")

        self.output = []
        self.indent_level = 0
        self.declared_variables = set()

        # Добавляем строгий режим
        self.add_line('"use strict";')
        self.add_line()

        # Обрабатываем программу
        self.visit_program(node)

        return '\n'.join(self.output)

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

    def add_line(self, line: str = ""):
        indent = '    ' * self.indent_level
        self.output.append(indent + line)

    def visit_program(self, node: Program):
        """Обработка программы"""
        for stmt in node.statements:
            self.visit(stmt)

    def visit(self, node):
        """Универсальный метод для посещения узлов"""
        if node is None:
            return ""

        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Обход неподдерживаемых узлов"""
        print(f"DEBUG GENERATOR: Unhandled node: {type(node).__name__}")
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self.visit(stmt)
        return ""

    def visit_expressionstatement(self, node: ExpressionStatement):
        """Обработка выражения-оператора"""
        expr_code = self.visit(node.expression)
        if expr_code:
            # ЕСЛИ это вызов функции (особенно print), добавляем точку с запятой
            if "console.log" in expr_code or "(" in expr_code:
                self.add_line(f"{expr_code};")
            else:
                # Для простых выражений тоже добавляем точку с запятой
                self.add_line(f"{expr_code};")

    def visit_assignment(self, node: Assignment):
        """Обработка присваивания - преобразуем в объявление переменной"""
        target_name = self.visit(node.target)
        value = self.visit(node.value)

        # Если переменная еще не объявлена, используем let
        if target_name not in self.declared_variables:
            self.declared_variables.add(target_name)
            self.add_line(f"let {target_name} = {value};")
        else:
            # Если уже объявлена, просто присваиваем
            self.add_line(f"{target_name} = {value};")

    def visit_binaryoperation(self, node: BinaryOperation):
        """Обработка бинарной операции"""
        left = self.visit(node.left)
        right = self.visit(node.right)

        operator_map = {
            'and': '&&',
            'or': '||',
            'is': '===',
            'is not': '!=='
        }

        operator = operator_map.get(node.operator, node.operator)

        # УМНЫЕ СКОБКИ: добавляем скобки только когда нужно
        # Для простых идентификаторов и литералов скобки не нужны
        needs_parentheses = True

        # Если оба операнда простые (идентификаторы или литералы), скобки не нужны
        if (isinstance(node.left, (Identifier, Literal)) and
                isinstance(node.right, (Identifier, Literal))):
            needs_parentheses = False

        # Для операторов сравнения тоже часто не нужны скобки
        if node.operator in ['==', '!=', '>', '<', '>=', '<=']:
            needs_parentheses = False

        if needs_parentheses:
            return f"({left} {operator} {right})"
        else:
            return f"{left} {operator} {right}"

    def visit_unaryoperation(self, node: UnaryOperation):
        """Обработка унарной операции"""
        operand = self.visit(node.operand)

        operator_map = {
            'not': '!',
            '+': '+',
            '-': '-'
        }

        operator = operator_map.get(node.operator, node.operator)

        # Для унарных операций тоже сохраняем скобки для безопасности
        if operator == '-' and isinstance(node.operand, (BinaryOperation, UnaryOperation)):
            return f"{operator}({operand})"
        return f"{operator}{operand}"

    def visit_identifier(self, node: Identifier):
        """Обработка идентификатора"""
        return node.name

    def visit_literal(self, node: Literal):
        """Обработка литерала"""
        if node.value is None:
            return "null"
        elif node.value is True:
            return "true"
        elif node.value is False:
            return "false"
        elif isinstance(node.value, str):
            # Экранируем кавычки в строках
            escaped_value = node.value.replace('"', '\\"')
            return f'"{escaped_value}"'
        elif isinstance(node.value, list):
            # Обработка списков
            elements = []
            for elem in node.value:
                if isinstance(elem, (int, float, str, bool)) or elem is None:
                    elements.append(self.visit_literal(Literal(elem, DataType.ANY, node.line, node.column)))
                else:
                    elements.append(str(elem))
            return f"[{', '.join(elements)}]"
        else:
            return str(node.value)

    def visit_functiondeclaration(self, node: FunctionDeclaration):
        """Обработка объявления функции"""
        params = ', '.join([param.name for param in node.parameters])
        self.add_line(f"function {node.name}({params}) {{")
        self.indent()

        # Добавляем параметры в объявленные переменные
        for param in node.parameters:
            self.declared_variables.add(param.name)

        self.visit(node.body)
        self.dedent()
        self.add_line("}")
        self.add_line()

    def visit_block(self, node: Block):
        """Обработка блока кода"""
        for statement in node.statements:
            self.visit(statement)

    def visit_ifstatement(self, node: IfStatement):
        """Обработка условного оператора"""
        condition = self.visit(node.condition)
        # Убираем внешние скобки, так как они уже есть в условии if
        condition_clean = condition[1:-1] if condition.startswith('(') and condition.endswith(')') else condition

        self.add_line(f"if ({condition_clean}) {{")
        self.indent()
        self.visit(node.then_branch)
        self.dedent()

        # Обработка else/elif
        if node.else_branch:
            if isinstance(node.else_branch, IfStatement):
                # Это elif
                self.add_line(f"}} else ", end="")
                else_code = self.visit(node.else_branch)
                # Убираем начальный if из кода
                if else_code.startswith("if "):
                    self.output[-1] += else_code
                else:
                    self.add_line(else_code)
            else:
                # Это else
                self.add_line("} else {")
                self.indent()
                self.visit(node.else_branch)
                self.dedent()
                self.add_line("}")
        else:
            self.add_line("}")

    def visit_whileloop(self, node: WhileLoop):
        """Обработка цикла while"""
        condition = self.visit(node.condition)
        # Убираем внешние скобки
        condition_clean = condition[1:-1] if condition.startswith('(') and condition.endswith(')') else condition

        self.add_line(f"while ({condition_clean}) {{")
        self.indent()
        self.visit(node.body)
        self.dedent()
        self.add_line("}")

    def visit_forloop(self, node: ForLoop):
        """Обработка цикла for"""
        variable = node.variable.name
        iterable = self.visit(node.iterable)

        # Добавляем переменную цикла в объявленные
        self.declared_variables.add(variable)

        self.add_line(f"for (let {variable} of {iterable}) {{")
        self.indent()
        self.visit(node.body)
        self.dedent()
        self.add_line("}")

    def visit_functioncall(self, node: FunctionCall):
        """Обработка вызова функции"""
        name = self.visit(node.name)
        args = ', '.join([self.visit(arg) for arg in node.arguments])

        # Специальная обработка для print -> console.log
        if name == "print":
            return f"console.log({args})"

        return f"{name}({args})"

    def visit_returnstatement(self, node: ReturnStatement):
        """Обработка оператора return"""
        if node.value:
            value = self.visit(node.value)
            self.add_line(f"return {value};")
        else:
            self.add_line("return;")

    def visit_breakstatement(self, node: BreakStatement):
        """Обработка оператора break"""
        self.add_line("break;")

    def visit_continuestatement(self, node: ContinueStatement):
        """Обработка оператора continue"""
        self.add_line("continue;")

    def visit_import(self, node: Import):
        """Обработка импорта (заглушка)"""
        self.add_line(f"// import {node.module_name}")

    def visit_variabledeclaration(self, node: VariableDeclaration):
        """Обработка объявления переменной"""
        if node.value:
            value = self.visit(node.value)
            self.add_line(f"let {node.name} = {value};")
        else:
            self.add_line(f"let {node.name};")
        self.declared_variables.add(node.name)
