#!/usr/bin/env python3
"""CLI прототип Spoon Messenger — проверка цепочки кодирования"""

import sys
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.compiler import compile_text


def main():
    if len(sys.argv) < 2:
        print("Использование: python cli.py \"текст сообщения\"")
        print("Пример:        python cli.py \"Hello\"")
        return

    text = sys.argv[1]
    print(f"Входной текст:  {text!r}")
    print(f"ASCII значения: {[ord(c) for c in text]}")
    print()

    bf_code = compile_text(text)
    print(f"Brainfuck код ({len(bf_code)} символов):")
    print(bf_code)


if __name__ == "__main__":
    main()
