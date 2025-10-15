from typing import List, Optional
from ..lexer.lexer import Lexer
from ..lexer.token_types import TokenType
from .ast_nodes import *
from ..exceptions import ParserError, UnexpectedTokenError, MissingTokenError


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = None
        self.next_token()

    def next_token(self):
        """Получаем следующий токен"""
        self.current_token = self.lexer.get_next_token()
        return self.current_token

    def expect(self, token_type: TokenType, error_message: str = None):
        """Проверяем, что текущий токен соответствует ожидаемому"""
        if self.current_token.type != token_type:
            if not error_message:
                error_message = f"Expected {token_type.name}, got {self.current_token.type.name}"
            raise UnexpectedTokenError(
                token_type.name,
                self.current_token.type.name,
                self.current_token.line,
                self.current_token.column
            )
        token = self.current_token
        self.next_token()
        return token

    def peek(self, token_type: TokenType) -> bool:
        """Проверяем следующий токен без потребления"""
        return self.current_token.type == token_type

    def skip_newlines(self):
        """Пропускаем переводы строк"""
        while self.peek(TokenType.NEWLINE):
            self.next_token()

    def parse(self) -> Program:
        """Начало разбора - программа"""
        statements = []
        self.skip_newlines()

        while not self.peek(TokenType.EOF):
            if self.peek(TokenType.IMPORT):
                statements.append(self.parse_import())
            elif self.peek(TokenType.DEF):
                statements.append(self.parse_function_declaration())
            elif self.peek(TokenType.IF):
                statements.append(self.parse_if_statement())
            elif self.peek(TokenType.WHILE):
                statements.append(self.parse_while_loop())
            elif self.peek(TokenType.FOR):
                statements.append(self.parse_for_loop())
            else:
                statements.append(self.parse_statement())

            self.skip_newlines()

        return Program(statements, 1, 1)

    def parse_import(self) -> Import:
        """Разбор импорта"""
        token = self.expect(TokenType.IMPORT, "Ожидался 'import'")
        module_name = self.expect(TokenType.VARIABLE, "Ожидалось имя модуля")
        return Import(module_name.value, token.line, token.column)

    def parse_function_declaration(self) -> FunctionDeclaration:
        """Разбор объявления функции"""
        token = self.expect(TokenType.DEF, "Ожидался 'def'")
        name = self.expect(TokenType.VARIABLE, "Ожидалось имя функции")

        self.expect(TokenType.LPAREN, "Ожидалась '('")
        parameters = self.parse_parameter_list()
        self.expect(TokenType.RPAREN, "Ожидалась ')'")
        self.expect(TokenType.COLON, "Ожидался ':'")

        # Пропускаем возможные newline после двоеточия
        self.skip_newlines()

        body = self.parse_block()

        return FunctionDeclaration(name.value, parameters, body, line=token.line, column=token.column)

    def parse_parameter_list(self) -> List[Identifier]:
        """Разбор списка параметров"""
        parameters = []

        if not self.peek(TokenType.RPAREN):
            parameters.append(Identifier(
                self.expect(TokenType.VARIABLE, "Ожидался идентификатор параметра").value,
                self.current_token.line,
                self.current_token.column
            ))

            while self.peek(TokenType.COMMA):
                self.next_token()  # пропускаем запятую
                parameters.append(Identifier(
                    self.expect(TokenType.VARIABLE, "Ожидался идентификатор параметра").value,
                    self.current_token.line,
                    self.current_token.column
                ))

        return parameters

    def parse_block(self) -> Block:
        """Разбор блока кода"""
        # Ожидаем отступ
        if not self.peek(TokenType.INDENT):
            # Если нет INDENT, создаем блок с одной строкой
            statements = [self.parse_statement()]
            return Block(statements, self.current_token.line, self.current_token.column)

        self.next_token()  # пропускаем INDENT

        statements = []
        self.skip_newlines()

        # Читаем все операторы до следующего DEDENT
        while not self.peek(TokenType.DEDENT) and not self.peek(TokenType.EOF):
            statements.append(self.parse_statement())
            self.skip_newlines()

        if self.peek(TokenType.DEDENT):
            self.next_token()  # пропускаем DEDENT

        return Block(statements, self.current_token.line, self.current_token.column)

    def parse_statement(self) -> Node:
        """Разбор оператора"""
        if self.peek(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.peek(TokenType.IF):
            return self.parse_if_statement()
        elif self.peek(TokenType.WHILE):
            return self.parse_while_loop()
        elif self.peek(TokenType.FOR):
            return self.parse_for_loop()
        elif self.peek(TokenType.VARIABLE) and self._peek_assign():
            return self.parse_assignment()
        else:
            return ExpressionStatement(self.parse_expression(),
                                       self.current_token.line, self.current_token.column)

    def parse_return_statement(self) -> ReturnStatement:
        """Разбор оператора return"""
        token = self.expect(TokenType.RETURN, "Ожидался 'return'")

        if self.peek(TokenType.NEWLINE) or self.peek(TokenType.DEDENT) or self.peek(TokenType.EOF):
            value = None
        else:
            value = self.parse_expression()

        return ReturnStatement(value, token.line, token.column)

    def parse_assignment(self) -> Assignment:
        """Разбор присваивания"""
        target = Identifier(self.current_token.value, self.current_token.line, self.current_token.column)
        self.next_token()

        # Проверяем операторы присваивания
        if self.peek(TokenType.ASSIGN):
            operator_token = self.expect(TokenType.ASSIGN)
        elif self.peek(TokenType.PLUS_ASSIGN):
            operator_token = self.expect(TokenType.PLUS_ASSIGN)
            # Преобразуем a += b в a = a + b
            value = BinaryOperation(
                Identifier(target.name, target.line, target.column),
                '+',
                self.parse_expression(),
                operator_token.line,
                operator_token.column
            )
            return Assignment(target, value, target.line, target.column)
        else:
            raise UnexpectedTokenError("assignment operator", self.current_token.type.name,
                                       self.current_token.line, self.current_token.column)

        value = self.parse_expression()
        return Assignment(target, value, target.line, target.column)

    def parse_if_statement(self) -> IfStatement:
        """Разбор условного оператора if"""
        token = self.expect(TokenType.IF, "Ожидался 'if'")
        condition = self.parse_expression()
        self.expect(TokenType.COLON, "Ожидался ':'")

        # Пропускаем возможные newline после двоеточия
        self.skip_newlines()

        then_branch = self.parse_block()
        else_branch = None

        # Пропускаем пустые строки после then_branch
        self.skip_newlines()

        if self.peek(TokenType.ELSE):
            self.next_token()  # пропускаем else
            self.expect(TokenType.COLON, "Ожидался ':'")

            # Пропускаем возможные newline после двоеточия
            self.skip_newlines()

            else_branch = self.parse_block()

        return IfStatement(condition, then_branch, else_branch, token.line, token.column)

    def parse_while_loop(self) -> WhileLoop:
        """Разбор цикла while"""
        token = self.expect(TokenType.WHILE, "Ожидался 'while'")
        condition = self.parse_expression()
        self.expect(TokenType.COLON, "Ожидался ':'")

        # Пропускаем возможные newline после двоеточия
        self.skip_newlines()

        body = self.parse_block()

        return WhileLoop(condition, body, token.line, token.column)

    def parse_for_loop(self) -> ForLoop:
        """Разбор цикла for"""
        token = self.expect(TokenType.FOR, "Ожидался 'for'")
        variable = Identifier(
            self.expect(TokenType.VARIABLE, "Ожидался идентификатор переменной").value,
            self.current_token.line,
            self.current_token.column
        )
        self.expect(TokenType.IN, "Ожидался 'in'")
        iterable = self.parse_expression()
        self.expect(TokenType.COLON, "Ожидался ':'")

        # Пропускаем возможные newline после двоеточия
        self.skip_newlines()

        body = self.parse_block()

        return ForLoop(variable, iterable, body, token.line, token.column)

    # Разбор выражений с приоритетами
    def parse_expression(self) -> Node:
        return self.parse_logical_or()

    def parse_logical_or(self) -> Node:
        """Логическое ИЛИ"""
        node = self.parse_logical_and()

        while self.peek(TokenType.OR):
            operator_token = self.current_token
            self.next_token()
            right = self.parse_logical_and()

            # Используем правильное строковое представление оператора
            operator_str = operator_token.value
            node = BinaryOperation(node, operator_str, right,
                                   operator_token.line, operator_token.column)

        return node

    def parse_logical_and(self) -> Node:
        """Логическое И"""
        node = self.parse_comparison()

        while self.peek(TokenType.AND):
            operator_token = self.current_token
            self.next_token()
            right = self.parse_comparison()

            # Используем правильное строковое представление оператора
            operator_str = operator_token.value
            node = BinaryOperation(node, operator_str, right,
                                   operator_token.line, operator_token.column)

        return node

    def parse_comparison(self) -> Node:
        """Операции сравнения"""
        node = self.parse_addition()

        while True:
            # Проверяем текущий токен на соответствие операторам сравнения
            if self.current_token.type == TokenType.EQUALS:
                operator = '=='
            elif self.current_token.type == TokenType.NOT_EQUALS:
                operator = '!='
            elif self.current_token.type == TokenType.GREATER:
                operator = '>'
            elif self.current_token.type == TokenType.LESS:
                operator = '<'
            elif self.current_token.type == TokenType.GREATER_EQUAL:
                operator = '>='
            elif self.current_token.type == TokenType.LESS_EQUAL:
                operator = '<='
            else:
                break  # Если не оператор сравнения, выходим из цикла

            operator_token = self.current_token
            self.next_token()  # переходим к следующему токену
            right = self.parse_addition()
            node = BinaryOperation(node, operator, right,
                                   operator_token.line, operator_token.column)

        return node

    def parse_addition(self) -> Node:
        """Сложение и вычитание"""
        node = self.parse_multiplication()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            operator_token = self.current_token
            self.next_token()
            right = self.parse_multiplication()

            # Используем правильное строковое представление оператора
            operator_str = operator_token.value
            node = BinaryOperation(node, operator_str, right,
                                   operator_token.line, operator_token.column)

        return node

    def parse_multiplication(self) -> Node:
        """Умножение, деление, остаток от деления"""
        node = self.parse_power()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator_token = self.current_token
            self.next_token()
            right = self.parse_power()

            # Используем правильное строковое представление оператора
            operator_str = operator_token.value
            node = BinaryOperation(node, operator_str, right,
                                   operator_token.line, operator_token.column)

        return node

    def parse_power(self) -> Node:
        """Возведение в степень"""
        node = self.parse_unary()

        if self.peek(TokenType.POWER):
            operator_token = self.current_token
            self.next_token()
            right = self.parse_power()

            # Используем правильное строковое представление оператора
            operator_str = operator_token.value
            node = BinaryOperation(node, operator_str, right,
                                   operator_token.line, operator_token.column)

        return node

    def parse_unary(self) -> Node:
        """Унарные операции"""
        if self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.NOT):
            operator_token = self.current_token
            self.next_token()
            operand = self.parse_unary()

            # Используем правильное строковое представление оператора
            operator_str = operator_token.value
            return UnaryOperation(operator_str, operand,
                                  operator_token.line, operator_token.column)

        return self.parse_primary()

    def parse_primary(self) -> Node:
        """Разбор первичных выражений"""
        token = self.current_token

        if self.peek(TokenType.VARIABLE) or self.peek(TokenType.PRINT):
            self.next_token()

            # Проверяем, является ли это вызовом функции
            if self.peek(TokenType.LPAREN):
                return self.parse_function_call(Identifier(token.value, token.line, token.column))
            else:
                return Identifier(token.value, token.line, token.column)

        elif self.peek(TokenType.INTEGER):
            self.next_token()
            return Literal(int(token.value), DataType.INT, token.line, token.column)

        elif self.peek(TokenType.FLOAT_NUMBER):
            self.next_token()
            return Literal(float(token.value), DataType.FLOAT, token.line, token.column)

        elif self.peek(TokenType.STRING) or self.peek(TokenType.CHAR):
            self.next_token()
            return Literal(token.value, DataType.STRING, token.line, token.column)

        elif self.peek(TokenType.TRUE):
            self.next_token()
            return Literal(True, DataType.BOOLEAN, token.line, token.column)

        elif self.peek(TokenType.FALSE):
            self.next_token()
            return Literal(False, DataType.BOOLEAN, token.line, token.column)

        elif self.peek(TokenType.NONE):
            self.next_token()
            return Literal(None, DataType.NONE, token.line, token.column)

        elif self.peek(TokenType.LPAREN):
            self.next_token()  # пропускаем '('
            node = self.parse_expression()
            self.expect(TokenType.RPAREN, "Ожидалась ')'")
            return node

        elif self.peek(TokenType.LBRACKET):
            return self.parse_list_literal()

        else:
            raise UnexpectedTokenError("expression", token.type.name, token.line, token.column)

    def parse_function_call(self, name: Identifier) -> FunctionCall:
        """Разбор вызова функции"""
        self.expect(TokenType.LPAREN, "Ожидалась '('")
        arguments = self.parse_argument_list()
        self.expect(TokenType.RPAREN, "Ожидалась ')'")

        return FunctionCall(name, arguments, name.line, name.column)

    def parse_argument_list(self) -> List[Node]:
        """Разбор списка аргументов"""
        arguments = []

        if not self.peek(TokenType.RPAREN):
            arguments.append(self.parse_expression())

            while self.peek(TokenType.COMMA):
                self.next_token()  # пропускаем запятую
                arguments.append(self.parse_expression())

        return arguments

    def parse_list_literal(self) -> Literal:
        """Разбор литерала списка"""
        token = self.expect(TokenType.LBRACKET, "Ожидалась '['")
        elements = []

        if not self.peek(TokenType.RBRACKET):
            elements.append(self.parse_expression())

            while self.peek(TokenType.COMMA):
                self.next_token()  # пропускаем запятую
                elements.append(self.parse_expression())

        self.expect(TokenType.RBRACKET, "Ожидалась ']'")

        # Извлекаем значения из Literal узлов, если они есть
        literal_values = []
        for element in elements:
            if isinstance(element, Literal):
                literal_values.append(element.value)
            else:
                # Если элемент не Literal (например, идентификатор или выражение),
                # оставляем как есть, но в тесте ожидаются только литералы
                literal_values.append(element)

        return Literal(literal_values, DataType.LIST, token.line, token.column)

    def _peek_assign(self) -> bool:
        """Проверяем, является ли следующий токен оператором присваивания"""
        # Временно сохраняем текущее состояние
        current_pos = self.lexer.position
        current_line = self.lexer.line
        current_column = self.lexer.column
        current_char = self.lexer.current_char

        # Получаем следующий токен
        next_token = self.lexer.get_next_token()

        # Восстанавливаем состояние
        self.lexer.position = current_pos
        self.lexer.line = current_line
        self.lexer.column = current_column
        self.lexer.current_char = current_char

        # Проверяем тип токена
        return next_token.type in [
            TokenType.ASSIGN,
            TokenType.PLUS_ASSIGN,
            TokenType.MINUS_ASSIGN,
            TokenType.MULTIPLY_ASSIGN,
            TokenType.DIVIDE_ASSIGN,
            TokenType.MODULO_ASSIGN
        ]