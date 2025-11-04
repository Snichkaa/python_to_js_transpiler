from .symbol_table import SymbolTable, SymbolType, DataType
from ..exceptions import UndefinedVariableError, RedeclarationError, TypeMismatchError
from ..parser.ast_nodes import *


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function_return_type = None
        self._initialize_builtin_functions()

    def _initialize_builtin_functions(self):
        """Инициализация встроенных функций"""
        builtin_functions = {
            'print': DataType.NONE,  # print ничего не возвращает
        }

        for func_name, return_type in builtin_functions.items():
            self.symbol_table.define(
                func_name,
                SymbolType.FUNCTION,
                return_type,
                0, 0  # line 0, column 0 для встроенных функций
            )

    def analyze(self, ast):
        """Основной метод семантического анализа"""
        self.errors = []
        self.visit(ast)
        return len(self.errors) == 0

    def visit(self, node):
        """Посещение узла AST"""
        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def visit_program(self, node):
        """Посещение программы"""
        for statement in node.statements:
            self.visit(statement)

    def visit_functiondeclaration(self, node):
        """Посещение объявления функции"""
        # Проверяем конфликты в текущей области видимости
        local_symbol = self.symbol_table.lookup_local(node.name)
        if local_symbol is not None and local_symbol.symbol_type == SymbolType.FUNCTION:
            self.errors.append(RedeclarationError(node.name, node.line, node.column))
            return

        # Добавляем функцию в текущую область видимости
        self.symbol_table.define(
            node.name,
            SymbolType.FUNCTION,
            node.return_type,
            node.line,
            node.column
        )

        # Входим в новую область видимости для тела функции
        self.symbol_table.enter_scope()

        # Добавляем параметры в область видимости функции
        for param in node.parameters:
            self.symbol_table.define(
                param.name,
                SymbolType.VARIABLE,
                DataType.ANY,
                param.line,
                param.column
            )

        # Сохраняем текущий тип возвращаемого значения
        old_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type

        # Анализируем тело функции
        for statement in node.body.statements:
            self.visit(statement)

        # Выходим из области видимости функции
        self.symbol_table.exit_scope()
        self.current_function_return_type = old_return_type

    def visit_block(self, node):
        """Посещение блока кода"""
        for statement in node.statements:
            self.visit(statement)

    def visit_assignment(self, node):
        """Посещение присваивания"""
        # Анализируем значение
        value_type = self.visit(node.value)

        # Проверяем, объявлена ли переменная
        symbol = self.symbol_table.lookup(node.target.name)

        if symbol is None:
            # Переменная не объявлена - создаем ее
            self.symbol_table.define(
                node.target.name,
                SymbolType.VARIABLE,
                value_type or DataType.ANY,
                node.target.line,
                node.target.column
            )
        else:
            # Переменная уже объявлена - проверяем совместимость типов
            if symbol.symbol_type != SymbolType.VARIABLE:
                self.errors.append(TypeMismatchError(
                    f"variable", f"{symbol.symbol_type.value}",
                    node.target.line, node.target.column
                ))

        return value_type

    def visit_binaryoperation(self, node):
        """Посещение бинарной операции"""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Для арифметических операций разрешаем числовые типы
        if node.operator in ['+', '-', '*', '/', '%', '**']:
            if self.is_numeric_type(left_type) and self.is_numeric_type(right_type):
                return self.get_numeric_result_type(left_type, right_type)
            elif node.operator == '+' and left_type == DataType.STRING and right_type == DataType.STRING:
                return DataType.STRING
            else:
                self.errors.append(TypeMismatchError(
                    f"numeric or string types",
                    f"{left_type.value} and {right_type.value}",
                    node.line, node.column
                ))
                return DataType.ANY

        # Для операций сравнения результат всегда boolean
        elif node.operator in ['==', '!=', '<', '>', '<=', '>=']:
            if self.are_types_comparable(left_type, right_type):
                return DataType.BOOLEAN
            else:
                self.errors.append(TypeMismatchError(
                    f"comparable types",
                    f"{left_type.value} and {right_type.value}",
                    node.line, node.column
                ))
                return DataType.ANY

        # Логические операции
        elif node.operator in ['and', 'or']:
            if left_type == DataType.BOOLEAN and right_type == DataType.BOOLEAN:
                return DataType.BOOLEAN
            else:
                self.errors.append(TypeMismatchError(
                    "boolean", f"{left_type.value} and {right_type.value}",
                    node.line, node.column
                ))
                return DataType.ANY

        return DataType.ANY

    def visit_identifier(self, node):
        """Посещение идентификатора"""
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self.errors.append(UndefinedVariableError(
                node.name, node.line, node.column
            ))
            return DataType.ANY
        return symbol.data_type

    def visit_literal(self, node):
        """Посещение литерала"""
        return node.literal_type

    def visit_listliteral(self, node):
        """Посещение литерала списка"""
        if hasattr(node, 'elements') and node.elements:
            # Анализируем все элементы
            for element in node.elements:
                self.visit(element)
        return DataType.LIST

    def visit_ifstatement(self, node):
        """Посещение условного оператора"""
        condition_type = self.visit(node.condition)
        if condition_type != DataType.BOOLEAN:
            self.errors.append(TypeMismatchError(
                "boolean", condition_type.value,
                node.condition.line, node.condition.column
            ))

        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

        return DataType.NONE

    def visit_whileloop(self, node):
        """Посещение цикла while"""
        condition_type = self.visit(node.condition)
        if condition_type != DataType.BOOLEAN:
            self.errors.append(TypeMismatchError(
                "boolean", condition_type.value,
                node.condition.line, node.condition.column
            ))

        self.visit(node.body)
        return DataType.NONE

    def visit_forloop(self, node):
        """Посещение цикла for"""
        # Анализируем итерируемое выражение
        iterable_type = self.visit(node.iterable)

        # Входим в новую область видимости цикла
        self.symbol_table.enter_scope()

        # Добавляем переменную цикла в область видимости
        self.symbol_table.define(
            node.variable.name,
            SymbolType.VARIABLE,
            DataType.ANY,
            node.variable.line,
            node.variable.column
        )

        # Анализируем тело цикла
        self.visit(node.body)

        # Выходим из области видимости цикла
        self.symbol_table.exit_scope()

        return DataType.NONE

    def visit_returnstatement(self, node):
        """Посещение оператора return"""
        if node.value:
            return_type = self.visit(node.value)
            if (self.current_function_return_type is not None and
                    self.current_function_return_type != DataType.ANY and
                    self.current_function_return_type != return_type):
                self.errors.append(TypeMismatchError(
                    self.current_function_return_type.value,
                    return_type.value,
                    node.line, node.column
                ))
        return DataType.NONE

    def visit_functioncall(self, node):
        """Посещение вызова функции"""
        # Проверяем, что функция объявлена
        symbol = self.symbol_table.lookup(node.function_name.name)
        if symbol is None:
            self.errors.append(UndefinedVariableError(
                node.function_name.name, node.function_name.line, node.function_name.column
            ))
            return DataType.ANY

        # Анализируем аргументы
        for arg in node.arguments:
            self.visit(arg)

        return symbol.data_type if symbol else DataType.ANY

    def visit_expressionstatement(self, node):
        """Посещение выражения как оператора"""
        return self.visit(node.expression)

    def visit_variabledeclaration(self, node):
        """Посещение объявления переменной"""
        value_type = DataType.ANY
        if node.value:
            value_type = self.visit(node.value)

        self.symbol_table.define(
            node.name,
            SymbolType.VARIABLE,
            value_type,
            node.line,
            node.column
        )
        return value_type

    # Вспомогательные методы
    def is_numeric_type(self, data_type):
        """Проверяет, является ли тип числовым"""
        return data_type in [DataType.INT, DataType.FLOAT, DataType.ANY]

    def is_iterable_type(self, data_type):
        """Проверяет, можно ли итерировать по типу"""
        return data_type in [DataType.LIST, DataType.ANY]

    def are_types_comparable(self, left_type, right_type):
        """Проверяет, можно ли сравнивать типы"""
        if left_type == DataType.ANY or right_type == DataType.ANY:
            return True
        return left_type == right_type

    def get_numeric_result_type(self, left_type, right_type):
        """Определяет результирующий тип для числовых операций"""
        if left_type == DataType.FLOAT or right_type == DataType.FLOAT:
            return DataType.FLOAT
        return DataType.INT

    def generic_visit(self, node):
        """Обход узлов по умолчанию"""
        # Для узлов с statements
        if hasattr(node, 'statements'):
            for statement in node.statements:
                self.visit(statement)
            return DataType.NONE

        # Для узлов с expression
        elif hasattr(node, 'expression'):
            return self.visit(node.expression)

        # Для узлов с elements (списки)
        elif hasattr(node, 'elements'):
            for element in node.elements:
                self.visit(element)
            return DataType.LIST

        # Для узлов с value
        elif hasattr(node, 'value'):
            return self.visit(node.value)

        # Для узлов с condition и body (if, while)
        elif hasattr(node, 'condition') and hasattr(node, 'body'):
            self.visit(node.condition)
            self.visit(node.body)
            if hasattr(node, 'else_branch') and node.else_branch:
                self.visit(node.else_branch)
            return DataType.NONE

        return DataType.ANY