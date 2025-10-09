from typing import Dict, List, Optional
from ..parser.ast_nodes import *
from .symbol_table import SymbolTable, SymbolType, DataType
from ..exceptions import SemanticError, UndefinedVariableError, RedeclarationError, TypeMismatchError


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.current_function_return_type: Optional[DataType] = None

    def analyze(self, node: Node) -> bool:
        """Запуск семантического анализа"""
        try:
            node.accept(self)
            return len(self.errors) == 0
        except SemanticError as e:
            self.errors.append(e)
            return False

    def generic_visit(self, node: Node):
        """Обход всех дочерних узлов"""
        for attr_name in dir(node):
            if not attr_name.startswith('_'):
                attr = getattr(node, attr_name)
                if isinstance(attr, Node):
                    attr.accept(self)
                elif isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, Node):
                            item.accept(self)

    def visit_program(self, node: Program):
        """Анализ программы"""
        for statement in node.statements:
            statement.accept(self)

    def visit_function_declaration(self, node: FunctionDeclaration):
        """Анализ объявления функции"""
        # Объявляем функцию в текущей области видимости
        if not self.symbol_table.declare(node.name, SymbolType.FUNCTION, node.return_type,
                                         line=node.line, column=node.column):
            self.errors.append(RedeclarationError(node.name, node.line, node.column))
            return

        # Входим в новую область видимости функции
        self.symbol_table.enter_scope()
        old_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type

        # Объявляем параметры
        for param in node.parameters:
            if not self.symbol_table.declare(param.name, SymbolType.PARAMETER,
                                             line=param.line, column=param.column):
                self.errors.append(RedeclarationError(param.name, param.line, param.column))

        # Анализируем тело функции
        node.body.accept(self)

        # Выходим из области видимости функции
        self.symbol_table.exit_scope()
        self.current_function_return_type = old_return_type

    def visit_variable_declaration(self, node: VariableDeclaration):
        """Анализ объявления переменной"""
        if not self.symbol_table.declare(node.name, SymbolType.VARIABLE, node.var_type,
                                         line=node.line, column=node.column):
            self.errors.append(RedeclarationError(node.name, node.line, node.column))

        # Анализируем значение, если оно есть
        if node.value:
            node.value.accept(self)

            # Проверяем совместимость типов
            if node.var_type != DataType.ANY:
                value_type = self._get_expression_type(node.value)
                if not self._are_types_compatible(node.var_type, value_type):
                    self.errors.append(TypeMismatchError(
                        node.var_type.value, value_type.value, node.line, node.column
                    ))

    def visit_assignment(self, node: Assignment):
        """Анализ присваивания"""
        # Проверяем, что переменная объявлена
        symbol = self.symbol_table.lookup(node.target.name)
        if not symbol:
            self.errors.append(UndefinedVariableError(node.target.name, node.line, node.column))
            return

        # Анализируем значение
        node.value.accept(self)

        # Проверяем совместимость типов
        value_type = self._get_expression_type(node.value)
        if not self._are_types_compatible(symbol.data_type, value_type):
            self.errors.append(TypeMismatchError(
                symbol.data_type.value, value_type.value, node.line, node.column
            ))

    def visit_binary_operation(self, node: BinaryOperation):
        """Анализ бинарной операции"""
        node.left.accept(self)
        node.right.accept(self)

        left_type = self._get_expression_type(node.left)
        right_type = self._get_expression_type(node.right)

        # Проверяем совместимость типов для операции
        if not self._are_operands_compatible(node.operator, left_type, right_type):
            self.errors.append(TypeMismatchError(
                left_type.value, right_type.value, node.line, node.column
            ))

    def visit_identifier(self, node: Identifier):
        """Анализ идентификатора"""
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.errors.append(UndefinedVariableError(node.name, node.line, node.column))

    def visit_if_statement(self, node: IfStatement):
        """Анализ условного оператора"""
        node.condition.accept(self)

        # Проверяем, что условие - булево
        condition_type = self._get_expression_type(node.condition)
        if condition_type != DataType.BOOLEAN:
            self.errors.append(TypeMismatchError(
                DataType.BOOLEAN.value, condition_type.value, node.line, node.column
            ))

        node.then_branch.accept(self)
        if node.else_branch:
            node.else_branch.accept(self)

    def visit_while_loop(self, node: WhileLoop):
        """Анализ цикла while"""
        node.condition.accept(self)

        # Проверяем, что условие - булево
        condition_type = self._get_expression_type(node.condition)
        if condition_type != DataType.BOOLEAN:
            self.errors.append(TypeMismatchError(
                DataType.BOOLEAN.value, condition_type.value, node.line, node.column
            ))

        node.body.accept(self)

    def visit_for_loop(self, node: ForLoop):
        """Анализ цикла for"""
        # Входим в область видимости цикла
        self.symbol_table.enter_scope()

        # Объявляем переменную цикла
        self.symbol_table.declare(node.variable.name, SymbolType.VARIABLE,
                                  line=node.variable.line, column=node.variable.column)

        node.iterable.accept(self)
        node.body.accept(self)

        # Выходим из области видимости цикла
        self.symbol_table.exit_scope()

    def visit_block(self, node: Block):
        """Анализ блока кода"""
        self.symbol_table.enter_scope()

        for statement in node.statements:
            statement.accept(self)

        self.symbol_table.exit_scope()

    def visit_return_statement(self, node: ReturnStatement):
        """Анализ оператора return"""
        if node.value:
            node.value.accept(self)

            # Проверяем совместимость с типом возвращаемого значения функции
            if self.current_function_return_type != DataType.NONE:
                value_type = self._get_expression_type(node.value)
                if not self._are_types_compatible(self.current_function_return_type, value_type):
                    self.errors.append(TypeMismatchError(
                        self.current_function_return_type.value, value_type.value,
                        node.line, node.column
                    ))
        else:
            # Пустой return - проверяем, что функция ожидает None
            if self.current_function_return_type != DataType.NONE:
                self.errors.append(TypeMismatchError(
                    self.current_function_return_type.value, DataType.NONE.value,
                    node.line, node.column
                ))

    def visit_function_call(self, node: FunctionCall):
        """Анализ вызова функции"""
        # Проверяем, что функция объявлена
        symbol = self.symbol_table.lookup(node.name.name)
        if not symbol or symbol.symbol_type != SymbolType.FUNCTION:
            self.errors.append(UndefinedVariableError(node.name.name, node.line, node.column))
            return

        # Анализируем аргументы
        for arg in node.arguments:
            arg.accept(self)

    # Вспомогательные методы
    def _get_expression_type(self, node: Node) -> DataType:
        """Определяет тип выражения"""
        if isinstance(node, Literal):
            return node.literal_type
        elif isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)
            return symbol.data_type if symbol else DataType.ANY
        elif isinstance(node, BinaryOperation):
            left_type = self._get_expression_type(node.left)
            right_type = self._get_expression_type(node.right)

            # Для арифметических операций определяем результирующий тип
            if node.operator in ['+', '-', '*', '/']:
                if left_type == DataType.STRING or right_type == DataType.STRING:
                    return DataType.STRING
                elif left_type == DataType.FLOAT or right_type == DataType.FLOAT:
                    return DataType.FLOAT
                else:
                    return DataType.INT
            elif node.operator in ['==', '!=', '>', '<', '>=', '<=', 'and', 'or']:
                return DataType.BOOLEAN

        return DataType.ANY

    def _are_types_compatible(self, type1: DataType, type2: DataType) -> bool:
        """Проверяет совместимость типов"""
        if type1 == DataType.ANY or type2 == DataType.ANY:
            return True

        # Числовые типы совместимы
        if {type1, type2} <= {DataType.INT, DataType.FLOAT}:
            return True

        return type1 == type2

    def _are_operands_compatible(self, operator: str, left_type: DataType, right_type: DataType) -> bool:
        """Проверяет совместимость операндов для операции"""
        if operator in ['+', '-', '*', '/', '%']:
            # Арифметические операции
            return self._are_types_compatible(left_type, right_type) and \
                left_type in [DataType.INT, DataType.FLOAT, DataType.STRING] and \
                right_type in [DataType.INT, DataType.FLOAT, DataType.STRING]

        elif operator in ['==', '!=', '>', '<', '>=', '<=']:
            # Операции сравнения
            return self._are_types_compatible(left_type, right_type)

        elif operator in ['and', 'or']:
            # Логические операции
            return left_type == DataType.BOOLEAN and right_type == DataType.BOOLEAN

        return True