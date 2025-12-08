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

        # ДОБАВЛЕНО: Автоматически добавляем вызов main() если он есть
        # Проверяем, есть ли функция main в программе
        has_main_function = False
        if isinstance(node, Program):
            for stmt in node.statements:
                if isinstance(stmt, FunctionDeclaration) and stmt.name == "main":
                    has_main_function = True
                    break

        # Если есть функция main, вызываем её
        if has_main_function:
            self.add_line()
            self.add_line("// Автоматический вызов main()")
            self.add_line("main();")

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

        # ОБНОВЛЕНО: Всегда добавляем точку с запятой
        # И проверяем, что это не просто идентификатор
        if expr_code:
            self.add_line(f"{expr_code};")

        # Добавим отладочный вывод
        print(f"DEBUG GENERATOR: ExpressionStatement: {expr_code}")

    def _needs_parentheses_for_logical(self, node, parent_operator=None):
        """Определяет, нужны ли скобки для логического выражения"""
        if not isinstance(node, BinaryOperation):
            return False

        # Если это логическая операция внутри другой логической операции
        if node.operator in ['&&', '||'] and parent_operator in ['&&', '||']:
            # Проверяем приоритет
            precedence = {'&&': 1, '||': 0}
            node_precedence = precedence.get(node.operator, 0)
            parent_precedence = precedence.get(parent_operator, 0)
            return node_precedence < parent_precedence

        return False

    def visit_assignment(self, node: Assignment):
        """Обработка присваивания - преобразуем в объявление переменной"""
        target_name = self.visit(node.target)
        value = self.visit(node.value)

        # Убираем лишние внешние скобки из значения
        if value.startswith('(') and value.endswith(')'):
            # Проверяем, можно ли убрать скобки
            inner = value[1:-1]
            # Если внутри нет сложной логики с операторами сравнения/логики, убираем скобки
            if '&&' not in inner and '||' not in inner:
                value = inner

        # Если переменная еще не объявлена, используем let
        if target_name not in self.declared_variables:
            self.declared_variables.add(target_name)
            self.add_line(f"let {target_name} = {value};")
        else:
            # Если уже объявлена, просто присваиваем
            self.add_line(f"{target_name} = {value};")

    def _get_operator_precedence(self, operator):
        """Возвращает приоритет оператора"""
        precedence = {
            '**': 4,
            '*': 3, '/': 3, '%': 3,
            '+': 2, '-': 2,
            '>': 1, '<': 1, '>=': 1, '<=': 1, '==': 1, '!=': 1,
            '&&': 0, '||': 0
        }
        return precedence.get(operator, 0)

    def visit_binaryoperation(self, node: BinaryOperation):
        """Обработка бинарной операции"""
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Если это конкатенация строк, и одна из них f-строка
        if node.operator == '+':
            # Проверяем, не является ли это результатом разбора f-строки
            # Если да, можем объединить в одну шаблонную строку
            pass

        operator_map = {
            'and': '&&',
            'or': '||',
            'is': '===',
            'is not': '!=='
        }

        operator = operator_map.get(node.operator, node.operator)

        # Специальная обработка для логических операторов
        # Если оператор логический (&& или ||), всегда добавляем скобки к сравнениям
        if operator in ['&&', '||']:
            # Проверяем, является ли левая часть сравнением
            left_is_comparison = isinstance(node.left, BinaryOperation) and node.left.operator in ['==', '!=', '>', '<',
                                                                                                   '>=', '<=']
            # Проверяем, является ли правая часть сравнением
            right_is_comparison = isinstance(node.right, BinaryOperation) and node.right.operator in ['==', '!=', '>',
                                                                                                      '<', '>=', '<=']

            # Для логических операций всегда добавляем скобки вокруг сравнений
            left_str = f"({left})" if left_is_comparison else left
            right_str = f"({right})" if right_is_comparison else right

            return f"{left_str} {operator} {right_str}"

        # Остальная логика для других операторов остается прежней
        current_precedence = self._get_operator_precedence(operator)

        # Проверяем, нужно ли добавлять скобки для левой части
        left_needs_paren = False
        if isinstance(node.left, BinaryOperation):
            left_precedence = self._get_operator_precedence(node.left.operator)
            left_needs_paren = left_precedence < current_precedence

        # Проверяем, нужно ли добавлять скобки для правой части
        right_needs_paren = False
        if isinstance(node.right, BinaryOperation):
            right_precedence = self._get_operator_precedence(node.right.operator)
            right_needs_paren = right_precedence <= current_precedence

        # Особый случай: для оператора возведения в степень (**) правоассоциативен
        if operator == '**' and isinstance(node.right, BinaryOperation):
            right_precedence = self._get_operator_precedence(node.right.operator)
            right_needs_paren = right_precedence < current_precedence

        left_str = f"({left})" if left_needs_paren else left
        right_str = f"({right})" if right_needs_paren else right

        return f"{left_str} {operator} {right_str}"

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
            # Проверяем, является ли это f-строкой
            if self._is_fstring(node.value):
                return self.generate_fstring(node.value)
            else:
                escaped_value = node.value.replace('"', '\\"')
                return f'"{escaped_value}"'
        elif isinstance(node.value, list):
            elements = []
            for elem in node.value:
                if isinstance(elem, (int, float, str, bool)) or elem is None:
                    elements.append(self.visit_literal(Literal(elem, DataType.ANY, node.line, node.column)))
                else:
                    elements.append(str(elem))
            return f"[{', '.join(elements)}]"
        else:
            return str(node.value)

    def _is_fstring(self, value: str) -> bool:
        """Проверяем, содержит ли строка {}"""
        return '{' in value and '}' in value

    def generate_fstring(self, fstring: str) -> str:
        """Генерируем шаблонную строку JavaScript из f-строки Python"""
        # Преобразуем f"Hello {name}" в `Hello ${name}`
        # Обрабатываем экранирование
        result = []
        i = 0

        while i < len(fstring):
            if fstring[i] == '{':
                # Находим закрывающую }
                j = i + 1
                brace_count = 1
                while j < len(fstring) and brace_count > 0:
                    if fstring[j] == '{':
                        brace_count += 1
                    elif fstring[j] == '}':
                        brace_count -= 1
                    j += 1

                # Выражение внутри {}
                expr = fstring[i + 1:j - 1]  # без внешних {}

                # ОБНОВЛЕНО: Удаляем f-префикс и оставляем только выражение
                # Например, "add(x, y)" оставляем как add(x, y)
                result.append(f"${{{expr}}}")
                i = j
            else:
                # Текстовая часть
                j = i
                while j < len(fstring) and fstring[j] != '{':
                    j += 1

                text = fstring[i:j]
                # Экранируем обратные кавычки и доллары
                text = text.replace('`', '\\`').replace('$', '\\$')
                result.append(text)
                i = j

        # Собираем шаблонную строку
        return f"`{''.join(result)}`"

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

        # Проверяем, является ли это условием __name__ == "__main__"
        is_name_main_check = False
        if isinstance(node.condition, BinaryOperation):
            left = self.visit(node.condition.left)
            right = self.visit(node.condition.right)
            # Проверяем, является ли это __name__ == "__main__"
            if left == '__name__' and right == '"__main__"':
                is_name_main_check = True

        # Если это проверка __name__ == "__main__", обрабатываем по-особому
        if is_name_main_check:
            # Для JavaScript не генерируем if (__name__ == "__main__")
            # Вместо этого выполняем тело блока сразу
            self.visit(node.then_branch)
        else:
            # Обычная обработка if
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

        print(f"DEBUG GENERATOR: FunctionCall: name={name}, args={args}")  # ДЛЯ ОТЛАДКИ

        # Специальная обработка для print -> console.log
        if name == "print":
            return f"console.log({args})"

        return f"{name}({args})"

    def visit_returnstatement(self, node: ReturnStatement):
        """Обработка оператора return"""
        if node.value:
            value = self.visit(node.value)
            # Убираем лишние скобки вокруг простых выражений
            if value.startswith('(') and value.endswith(')'):
                # Проверяем, действительно ли нужны скобки
                inner = value[1:-1]
                # Если это простое выражение без вложенных скобок, убираем внешние
                if '(' not in inner and ')' not in inner:
                    value = inner
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
