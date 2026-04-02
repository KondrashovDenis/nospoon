def find_best_factor(n: int) -> int:
    """Найти лучший множитель для n (минимизировать длину BF кода)"""
    if n == 0:
        return 1
    best = 1
    best_cost = n  # наивный вариант — просто n плюсов
    for i in range(2, int(n**0.5) + 2):
        if i > n:
            break
        q, r = divmod(n, i)
        # стоимость: i (внешний цикл) + q (внутренний) + r (остаток) + 6 (служебные символы петли)
        cost = i + q + r + 6
        if cost < best_cost:
            best_cost = cost
            best = i
    return best


def compile_char(ascii_val: int, cell_index: int = 0) -> str:
    """
    Скомпилировать один символ в BF код.
    Использует множители для компактности.

    Вход:  ascii_val = 72 (символ 'H')
    Выход: '++++++++[>+++++++++<-]>.'  (примерно)
    """
    if ascii_val == 0:
        return '.'

    factor = find_best_factor(ascii_val)
    quotient, remainder = divmod(ascii_val, factor)

    if factor == 1:
        # наивный вариант
        return '+' * ascii_val + '.'

    # структура: FACTOR плюсов во внешней ячейке
    # петля: переходим вправо, добавляем QUOTIENT, возвращаемся, декрементируем
    # остаток добавляем после петли
    bf = ''
    bf += '+' * factor          # заполнить счётчик
    bf += '[>+'                 # открыть петлю, перейти в рабочую ячейку
    bf += '+' * (quotient - 1)  # добавить quotient (один + уже есть)
    bf += '<-]'                 # вернуться, декрементировать счётчик
    bf += '>'                   # перейти в рабочую ячейку
    bf += '+' * remainder       # добавить остаток
    bf += '.'                   # вывести символ
    bf += '[-]'                 # очистить ячейку для следующего символа
    bf += '<'                   # вернуться к счётчику (для следующего символа)

    return bf


def compile_text(text: str) -> str:
    """
    Скомпилировать строку текста в BF программу.

    Вход:  "Hi"
    Выход: валидная BF программа которая выводит "Hi"
    """
    if not text:
        return ''

    bf_parts = []
    for char in text:
        ascii_val = ord(char)
        bf_parts.append(compile_char(ascii_val))

    return ''.join(bf_parts)
