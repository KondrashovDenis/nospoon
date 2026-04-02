"""
Brainfuck интерпретатор для Spoon Messenger.
Выполняет BF программу и возвращает текстовый вывод.
"""


class BrainfuckError(Exception):
    """Ошибка выполнения BF программы"""
    pass


class BrainfuckInterpreter:
    def __init__(self, tape_size: int = 30000, max_steps: int = 1_000_000):
        """
        tape_size  — размер ленты памяти (по умолчанию 30000)
        max_steps  — защита от бесконечных циклов
        """
        self.tape_size = tape_size
        self.max_steps = max_steps

    def run(self, bf_code: str, stdin: str = '') -> str:
        """
        Выполнить BF программу.

        Вход:  bf_code = '++++++++[>+++++++++<-]>.'
               stdin   = '' (опциональный ввод для команды ',')
        Выход: строка вывода программы

        Исключения:
            BrainfuckError — бесконечный цикл или ошибка выполнения
        """
        # инициализация
        tape = [0] * self.tape_size
        ptr = 0          # указатель на ленте
        pc = 0           # program counter
        output = []      # буфер вывода
        input_ptr = 0    # указатель на stdin
        steps = 0        # счётчик шагов

        # предкомпилировать таблицу переходов [ → ]
        bracket_map = self._build_bracket_map(bf_code)

        while pc < len(bf_code):
            cmd = bf_code[pc]
            steps += 1

            if steps > self.max_steps:
                raise BrainfuckError(
                    f"Превышен лимит шагов ({self.max_steps}). "
                    f"Возможно бесконечный цикл или истёк TTL."
                )

            if cmd == '+':
                tape[ptr] = (tape[ptr] + 1) % 256
            elif cmd == '-':
                tape[ptr] = (tape[ptr] - 1) % 256
            elif cmd == '>':
                ptr += 1
                if ptr >= self.tape_size:
                    raise BrainfuckError("Выход за пределы ленты (вправо)")
            elif cmd == '<':
                ptr -= 1
                if ptr < 0:
                    raise BrainfuckError("Выход за пределы ленты (влево)")
            elif cmd == '.':
                output.append(chr(tape[ptr]))
            elif cmd == ',':
                if input_ptr < len(stdin):
                    tape[ptr] = ord(stdin[input_ptr])
                    input_ptr += 1
                else:
                    tape[ptr] = 0  # EOF = 0
            elif cmd == '[':
                if tape[ptr] == 0:
                    pc = bracket_map[pc]
            elif cmd == ']':
                if tape[ptr] != 0:
                    pc = bracket_map[pc]

            pc += 1

        return ''.join(output)

    def _build_bracket_map(self, bf_code: str) -> dict:
        """
        Предкомпилировать таблицу переходов для [ и ].
        Возвращает dict: позиция_[ → позиция_]  и  позиция_] → позиция_[
        """
        stack = []
        bracket_map = {}

        for i, cmd in enumerate(bf_code):
            if cmd == '[':
                stack.append(i)
            elif cmd == ']':
                if not stack:
                    raise BrainfuckError(f"Несбалансированная скобка ] на позиции {i}")
                j = stack.pop()
                bracket_map[j] = i
                bracket_map[i] = j

        if stack:
            raise BrainfuckError(f"Несбалансированная скобка [ на позиции {stack[-1]}")

        return bracket_map


def run_bf(bf_code: str, stdin: str = '', max_steps: int = 1_000_000) -> str:
    """
    Удобная функция-обёртка для запуска BF программы.

    Вход:  bf_code — строка BF кода
           stdin   — опциональный ввод
    Выход: строка вывода
    """
    interpreter = BrainfuckInterpreter(max_steps=max_steps)
    return interpreter.run(bf_code, stdin)
