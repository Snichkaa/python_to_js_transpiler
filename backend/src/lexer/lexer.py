from .token import Token
from .token_types import TokenType, KEYWORDS, RESERVED_WORDS, OPERATORS, DELIMITERS
from backend.src.exceptions import LexerError, InvalidCharacterError, UnclosedStringError, InvalidNumberError

class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source_code[0] if source_code else None
        self.indent_stack = [0]  # стек для отслеживания отступов
        self.pending_tokens = []  # очередь для INDENT/DEDENT токенов

    def error(self, message, char=None):
        """Создаем исключение лексической ошибки"""
        if char is None and self.current_char is not None:
            char = self.current_char
        # Убираем лишний аргумент char
        raise LexerError(message, self.line, self.column)

    def advance(self):
        """Перемещаем указатель на следующий символ"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1
        if self.position >= len(self.source_code):
            self.current_char = None
        else:
            self.current_char = self.source_code[self.position]

    def peek(self, n=1):
        """Просматриваем следующий символ без перемещения указателя"""
        pos = self.position + n
        if pos >= len(self.source_code):
            return None
        return self.source_code[pos]

    def skip_whitespace(self):
        """Пропускаем пробельные символы (кроме новых строк)"""
        while self.current_char is not None and self.current_char in ' \t':
            self.advance()

    def skip_comment(self):
        """Пропускаем комментарии"""
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

    def handle_indentation(self):
        """Обрабатываем отступы Python (генерирует INDENT/DEDENT токены)"""
        if self.pending_tokens:
            return self.pending_tokens.pop(0)

        # Подсчитываем текущий отступ
        indent_level = 0
        while self.current_char in (' ', '\t'):
            if self.current_char == ' ':
                indent_level += 1
            else:  # таб
                indent_level = (indent_level // 4 + 1) * 4
            self.advance()

        # Если после пробелов идет конец строки, комментарий или конец файла - пропускаем
        if self.current_char in ('\n', '#', None):
            return None

        current_indent = self.indent_stack[-1]

        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            return Token(TokenType.INDENT, ' ' * indent_level, self.line, self.column)

        elif indent_level < current_indent:
            dedent_tokens = []
            while self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                dedent_tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))

            # Более мягкая проверка несоответствия отступов
            if self.indent_stack[-1] != indent_level:
                # Добавляем дополнительные DEDENT до базового уровня
                while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                    self.indent_stack.pop()
                    dedent_tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))

            if dedent_tokens:
                self.pending_tokens.extend(dedent_tokens)
                return self.pending_tokens.pop(0)

            return None

        return None

    def read_number(self):
        """Читаем числовой литерал"""
        start_line = self.line
        start_column = self.column
        result = ''
        has_dot = False

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_dot:
                    #Ошибка - лишняя точка в числе
                    raise InvalidNumberError(result + '.', start_line, start_column)
                has_dot = True
            result += self.current_char
            self.advance()

        #Проверяем, что после числа нет букв
        if self.current_char is not None and self.current_char.isalpha():
            raise InvalidNumberError(result + self.current_char, start_line, start_column)

        if has_dot:
            #Проверяем, что вещественное число корректно
            if result == '.' or result.endswith('.'):
                raise InvalidNumberError(result, start_line, start_column)
            return Token(TokenType.FLOAT_NUMBER, result, start_line, start_column)
        else:
            return Token(TokenType.INTEGER, result, start_line, start_column)

    def read_string(self, quote_char):
        """Читаем строковый или символьный литерал"""
        start_line = self.line
        start_column = self.column
        result = ''
        self.advance()  # пропускаем открывающую кавычку

        while self.current_char is not None and self.current_char != quote_char:
            #Обрабатываем escape-последовательностей
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == quote_char:
                    result += quote_char
                else:
                    result += '\\' + self.current_char
            else:
                result += self.current_char
            self.advance()

        if self.current_char != quote_char:
            #Ошибка - незакрытая строка
            if quote_char == "'":
                raise UnclosedStringError(start_line, start_column, "single")
            else:
                raise UnclosedStringError(start_line, start_column, "double")

        self.advance()  # пропускаем закрывающую кавычку

        #Определяем тип токена: CHAR или STRING
        if quote_char == "'" and len(result) == 1:
            return Token(TokenType.CHAR, result, start_line, start_column)
        else:
            return Token(TokenType.STRING, result, start_line, start_column)

    def read_identifier(self):
        """Читаем идентификатор или ключевое слово"""
        start_line = self.line
        start_column = self.column
        result = ''

        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()

        # Проверяем, является ли ключевым словом
        if result in KEYWORDS:
            return Token(KEYWORDS[result], result, start_line, start_column)
        elif result in RESERVED_WORDS:
            return Token(RESERVED_WORDS[result], result, start_line, start_column)
        else:
            return Token(TokenType.VARIABLE, result, start_line, start_column)

    def read_operator(self):
        """Читаем оператор"""
        start_line = self.line
        start_column = self.column

        # Двухсимвольные операторы
        two_char_op = self.current_char + (self.peek() or '')
        if two_char_op in OPERATORS:
            op = two_char_op
            self.advance()
            self.advance()
            return Token(OPERATORS[op], op, start_line, start_column)

        # Односимвольные операторы
        if self.current_char in OPERATORS:
            op = self.current_char
            self.advance()
            return Token(OPERATORS[op], op, start_line, start_column)

        return None

    def get_next_token(self):
        """Основной метод - возвращает следующий токен"""
        # Сначала обрабатываем pending токены (INDENT/DEDENT)
        if self.pending_tokens:
            return self.pending_tokens.pop(0)

        # Бесконечный цикл для пропуска пустого содержимого
        while True:
            # Обрабатываем отступы в начале строки
            if self.column == 1 and self.current_char in (' ', '\t'):
                indent_token = self.handle_indentation()
                if indent_token:
                    return indent_token

            # Пропускаем пробелы
            self.skip_whitespace()

            # Конец файла
            if self.current_char is None:
                if len(self.indent_stack) > 1:
                    self.indent_stack.pop()
                    return Token(TokenType.DEDENT, '', self.line, self.column)
                return Token(TokenType.EOF, '', self.line, self.column)

            # Новая строка
            if self.current_char == '\n':
                line = self.line
                column = self.column
                self.advance()
                # Если следующая строка пустая, продолжаем цикл
                continue

            # Комментарии
            if self.current_char == '#':
                self.skip_comment()
                continue  # продолжаем цикл после комментария

            # Если дошли сюда, значит есть значимое содержимое
            break

        # Теперь обрабатываем значимые токены

        # Числа
        if self.current_char.isdigit():
            return self.read_number()

        # Строки
        if self.current_char in ('"', "'"):
            return self.read_string(self.current_char)

        # Идентификаторы
        if self.current_char.isalpha() or self.current_char == '_':
            return self.read_identifier()

        # Операторы
        operator_token = self.read_operator()
        if operator_token:
            return operator_token

        # Разделители
        if self.current_char in DELIMITERS:
            delim = self.current_char
            line = self.line
            col = self.column
            self.advance()
            return Token(DELIMITERS[delim], delim, line, col)

        # Неизвестный символ
        self.error(f"Invalid character '{self.current_char}'")

    def tokenize(self):
        """Генерируем все токены из исходного кода"""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens