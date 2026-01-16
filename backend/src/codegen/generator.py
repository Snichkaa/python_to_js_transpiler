from typing import List
from backend.src.parser.ast_nodes import *


class CodeGenerator:
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.declared_variables = set()  # Отслеживаем объявленные переменные
        self.should_call_main = False


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

        # Вспомогательные функции рантайма для Python-подмножества (range, str, ...)
        needs_range, needs_str = self._scan_runtime_needs(node)
        if needs_range:
            self._emit_range_helper()
            self.add_line()
        if needs_str:
            self.add_line('function str(value) {')
            self.indent()
            self.add_line('return String(value);')
            self.dedent()
            self.add_line('}')
            self.add_line()

        # Обрабатываем программу
        self.visit_program(node)

        # Добавляем вызов main(), если встретили if __name__ == "__main__"
        if self.should_call_main:
            self.add_line()
            self.add_line("main();")


        return '\n'.join(self.output)

    def _scan_runtime_needs(self, node: Node):
        """Проходит по AST и определяет, нужны ли рантайм-хелперы."""
        needs_range = False
        needs_str = False

        def walk(n: Node):
            nonlocal needs_range, needs_str
            if n is None:
                return
            # FunctionCall name хранится как Identifier
            if isinstance(n, FunctionCall):
                name = self.visit(n.name)
                if name == 'range':
                    needs_range = True
                elif name == 'str':
                    needs_str = True
            # Рекурсивно обходим все поля узла
            for v in getattr(n, '__dict__', {}).values():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, Node):
                            walk(item)
                elif isinstance(v, Node):
                    walk(v)

        walk(node)
        return needs_range, needs_str

    def _emit_range_helper(self):
        """Эмуляция Python range(...) в JS как массива чисел."""
        self.add_line('function range() {')
        self.indent()
        self.add_line('const args = Array.from(arguments);')
        self.add_line('let start = 0, stop = 0, step = 1;')
        self.add_line('if (args.length === 1) {')
        self.indent()
        self.add_line('stop = args[0];')
        self.dedent()
        self.add_line('} else if (args.length === 2) {')
        self.indent()
        self.add_line('start = args[0]; stop = args[1];')
        self.dedent()
        self.add_line('} else if (args.length >= 3) {')
        self.indent()
        self.add_line('start = args[0]; stop = args[1]; step = args[2];')
        self.dedent()
        self.add_line('}')
        self.add_line('if (step === 0) { throw new Error("range() step argument must not be zero"); }')
        self.add_line('const out = [];')
        self.add_line('if (step > 0) {')
        self.indent()
        self.add_line('for (let i = start; i < stop; i += step) out.push(i);')
        self.dedent()
        self.add_line('} else {')
        self.indent()
        self.add_line('for (let i = start; i > stop; i += step) out.push(i);')
        self.dedent()
        self.add_line('}')
        self.add_line('return out;')
        self.dedent()
        self.add_line('}')

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

    def add_line(self, line: str = ""):
        indent = '    ' * self.indent_level
        self.output.append(indent + line)

    # ---- НОВЫЕ/ИСПРАВЛЕННЫЕ ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ----
    def _strip_parentheses_if_simple(self, expr: str) -> str:
        """Удаляет внешние скобки, если выражение простое"""
        if expr.startswith('(') and expr.endswith(')'):
            inner = expr[1:-1]
            if all(op not in inner for op in ['&&','||','+','-','*','/','>','<','=','!']):
                return inner
        return expr

    # ---- ПОСЕЩЕНИЕ УЗЛОВ ----
    def visit_program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit(self, node):
        if node is None:
            return ""
        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        print(f"DEBUG GENERATOR: Unhandled node: {type(node).__name__}")
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self.visit(stmt)
        return ""

    def visit_expressionstatement(self, node: ExpressionStatement):
        expr_code = self.visit(node.expression)
        if expr_code:
            self.add_line(f"{expr_code};")
        print(f"DEBUG GENERATOR: ExpressionStatement: {expr_code}")

    # ---- ПРИСВАИВАНИЕ ----
    def visit_assignment(self, node: Assignment):
        target_name = self.visit(node.target)
        value = self.visit(node.value)
        if value.startswith('(') and value.endswith(')'):
            inner = value[1:-1]
            if '&&' not in inner and '||' not in inner:
                value = inner
        if target_name not in self.declared_variables:
            self.declared_variables.add(target_name)
            self.add_line(f"let {target_name} = {value};")
        else:
            self.add_line(f"{target_name} = {value};")

    # ---- БИНАРНЫЕ ОПЕРАЦИИ ----
    def _get_operator_precedence(self, operator):
        precedence = {
            '**': 4,
            '*': 3, '/': 3, '%': 3,
            '+': 2, '-': 2,
            '>': 1, '<': 1, '>=': 1, '<=': 1, '==': 1, '!=': 1,
            '&&': 0, '||': 0
        }
        return precedence.get(operator, 0)

    def visit_binaryoperation(self, node: BinaryOperation):
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator_map = {'and': '&&', 'or': '||', 'is': '===', 'is not': '!=='}
        operator = operator_map.get(node.operator, node.operator)

        if operator in ['&&', '||']:
            left_is_cmp = isinstance(node.left, BinaryOperation) and node.left.operator in ['==','!=','>','<','>=','<=']
            right_is_cmp = isinstance(node.right, BinaryOperation) and node.right.operator in ['==','!=','>','<','>=','<=']
            left_str = f"({left})" if left_is_cmp else left
            right_str = f"({right})" if right_is_cmp else right
            return f"{left_str} {operator} {right_str}"

        current_prec = self._get_operator_precedence(operator)
        left_needs_paren = isinstance(node.left, BinaryOperation) and self._get_operator_precedence(node.left.operator) < current_prec
        right_needs_paren = isinstance(node.right, BinaryOperation) and self._get_operator_precedence(node.right.operator) <= current_prec
        if operator == '**' and isinstance(node.right, BinaryOperation):
            right_needs_paren = self._get_operator_precedence(node.right.operator) < current_prec
        left_str = f"({left})" if left_needs_paren else left
        right_str = f"({right})" if right_needs_paren else right
        return f"{left_str} {operator} {right_str}"

    # ---- УНАРНЫЕ ОПЕРАЦИИ ----
    def visit_unaryoperation(self, node: UnaryOperation):
        operand = self.visit(node.operand)
        op_map = {'not': '!', '+': '+', '-': '-'}
        operator = op_map.get(node.operator, node.operator)
        if operator == '-' and isinstance(node.operand, (BinaryOperation, UnaryOperation)):
            return f"{operator}({operand})"
        return f"{operator}{operand}"

    def visit_identifier(self, node: Identifier):
        return node.name

    def visit_literal(self, node: Literal):
        if node.value is None: return "null"
        elif node.value is True: return "true"
        elif node.value is False: return "false"
        elif isinstance(node.value, str):
            raw = node.value

            # Удаляем внешние кавычки, если парсер их оставил
            if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                raw = raw[1:-1]

            if self._is_fstring(raw):
                return self.generate_fstring(raw)

            return '"' + raw.replace('"', '\\"') + '"'

        elif isinstance(node.value, list):
            elems = [self.visit_literal(Literal(e, DataType.ANY, node.line, node.column)) if isinstance(e, (int,float,str,bool)) or e is None else str(e) for e in node.value]
            return f"[{', '.join(elems)}]"
        else:
            return str(node.value)

    def _is_fstring(self, value: str) -> bool:
        return '{' in value and '}' in value

    def generate_fstring(self, fstring: str) -> str:
        result = []
        i = 0
        while i < len(fstring):
            if fstring[i] == '{':
                j = i + 1; brace_count = 1
                while j < len(fstring) and brace_count > 0:
                    if fstring[j] == '{': brace_count += 1
                    elif fstring[j] == '}': brace_count -= 1
                    j += 1
                expr = fstring[i+1:j-1]
                result.append(f"${{{expr}}}")
                i = j
            else:
                j = i
                while j < len(fstring) and fstring[j] != '{': j += 1
                text = fstring[i:j].replace('`','\\`').replace('$','\\$')
                result.append(text)
                i = j
        return f"`{''.join(result)}`"

    # ---- ФУНКЦИИ ----
    def visit_functiondeclaration(self, node: FunctionDeclaration):
        params = ', '.join([p.name for p in node.parameters])
        self.add_line(f"function {node.name}({params}) {{")
        self.indent()
        for p in node.parameters: self.declared_variables.add(p.name)
        self.visit(node.body)
        self.dedent()
        self.add_line("}")
        self.add_line()

    def visit_block(self, node: Block):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ifstatement(self, node: IfStatement):
        condition = self.visit(node.condition)
        is_main_check = isinstance(node.condition, BinaryOperation) and self.visit(node.condition.left) == '__name__' and self.visit(node.condition.right) == '"__main__"'
        if is_main_check:
            # Не вставляем вызов main() внутрь функции!
            self.should_call_main = True
            return
        condition_clean = self._strip_parentheses_if_simple(condition)
        self.add_line(f"if ({condition_clean}) {{")
        self.indent()
        self.visit(node.then_branch)
        self.dedent()
        if node.else_branch:
            if isinstance(node.else_branch, IfStatement):
                self.add_line(f"}} else ", end="")
                else_code = self.visit(node.else_branch)
                if else_code.startswith("if "): self.output[-1] += else_code
                else: self.add_line(else_code)
            else:
                self.add_line("} else {")
                self.indent()
                self.visit(node.else_branch)
                self.dedent()
                self.add_line("}")
        else:
            self.add_line("}")

    def visit_whileloop(self, node: WhileLoop):
        condition = self._strip_parentheses_if_simple(self.visit(node.condition))
        self.add_line(f"while ({condition}) {{")
        self.indent()
        self.visit(node.body)
        self.dedent()
        self.add_line("}")

    def visit_forloop(self, node: ForLoop):
        variable = node.variable.name
        self.declared_variables.add(variable)
        iter_code = self.visit(node.iterable)
        self.add_line(f"for (let {variable} of {iter_code}) {{")
        self.indent()
        self.visit(node.body)
        self.dedent()
        self.add_line("}")

    def visit_functioncall(self, node: FunctionCall):
        name = self.visit(node.name)
        args = ', '.join([self.visit(a) for a in node.arguments])
        # Встроенная функция print
        if name == "print":
            return f"console.log({args})"
        return f"{name}({args})"

    def visit_returnstatement(self, node: ReturnStatement):
        if node.value:
            value = self._strip_parentheses_if_simple(self.visit(node.value))
            self.add_line(f"return {value};")
        else: self.add_line("return;")

    def visit_breakstatement(self, node: BreakStatement):
        self.add_line("break;")

    def visit_continuestatement(self, node: ContinueStatement):
        self.add_line("continue;")

    def visit_import(self, node: Import):
        self.add_line(f"// import {node.module_name}")

    def visit_variabledeclaration(self, node: VariableDeclaration):
        if node.value:
            value = self.visit(node.value)
            self.add_line(f"let {node.name} = {value};")
        else:
            self.add_line(f"let {node.name};")
        self.declared_variables.add(node.name)
 #Чисто для проверки
