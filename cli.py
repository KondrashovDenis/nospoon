#!/usr/bin/env python3
"""CLI прототип Spoon Messenger — проверка цепочки кодирования"""

import sys
import os
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.compiler import compile_text
from core.transcoder import encode_to_bin, decode_from_bin
from core.interpreter import run_bf, BrainfuckError


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python cli.py encode \"текст\"     — закодировать текст в .bin")
        print("  python cli.py decode file.bin    — декодировать .bin → текст")
        print("  python cli.py run file.bin       — выполнить .bin и вывести текст")
        return

    command = sys.argv[1]

    if command == 'encode':
        if len(sys.argv) < 3:
            print("Укажи текст: python cli.py encode \"Hello\"")
            return

        text = sys.argv[2]
        print(f"Входной текст:  {text!r}")
        print(f"ASCII значения: {[ord(c) for c in text]}")
        print()

        bf_code = compile_text(text)
        print(f"Brainfuck ({len(bf_code)} символов):")
        print(bf_code[:80] + ('...' if len(bf_code) > 80 else ''))
        print()

        binary = encode_to_bin(bf_code)
        print(f"Spoon .bin ({len(binary)} байт):")
        print(binary.hex())
        print()

        filename = 'message.bin'
        with open(filename, 'wb') as f:
            f.write(binary)
        print(f"Сохранено: {filename}")

    elif command == 'decode':
        if len(sys.argv) < 3:
            print("Укажи файл: python cli.py decode message.bin")
            return

        filename = sys.argv[2]
        if not os.path.exists(filename):
            print(f"Файл не найден: {filename}")
            return

        with open(filename, 'rb') as f:
            binary = f.read()

        print(f"Файл: {filename} ({len(binary)} байт)")
        bf_code = decode_from_bin(binary)
        print(f"Brainfuck ({len(bf_code)} символов):")
        print(bf_code[:80] + ('...' if len(bf_code) > 80 else ''))

    elif command == 'run':
        if len(sys.argv) < 3:
            print("Укажи файл: python cli.py run message.bin")
            return

        filename = sys.argv[2]
        if not os.path.exists(filename):
            print(f"Файл не найден: {filename}")
            return

        with open(filename, 'rb') as f:
            binary = f.read()

        print(f"Выполняю {filename}...")
        print()

        try:
            bf_code = decode_from_bin(binary)
            result = run_bf(bf_code)
            print(f"Результат:")
            print(result)
        except BrainfuckError as e:
            print(f"Ошибка выполнения: {e}")


if __name__ == "__main__":
    main()
