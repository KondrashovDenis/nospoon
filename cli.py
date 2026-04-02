#!/usr/bin/env python3
"""CLI прототип Spoon Messenger — проверка цепочки кодирования"""

import sys
import os
import time
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.compiler import compile_text
from core.transcoder import encode_to_bin, decode_from_bin
from core.interpreter import run_bf, BrainfuckError
from core.ttl import wrap_simple, get_stdin_token

TTL_OPTIONS = {
    '1h':  3600,
    '6h':  21600,
    '24h': 86400,
    '7d':  604800,
}


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python cli.py encode \"текст\" [ttl]  — закодировать (ttl: 1h/6h/24h/7d)")
        print("  python cli.py decode file.bin       — показать BF код")
        print("  python cli.py run file.bin          — выполнить и вывести текст")
        return

    command = sys.argv[1]

    if command == 'encode':
        if len(sys.argv) < 3:
            print("Укажи текст: python cli.py encode \"Hello\"")
            return

        text = sys.argv[2]
        ttl_key = sys.argv[3] if len(sys.argv) > 3 else '24h'
        ttl_seconds = TTL_OPTIONS.get(ttl_key, 86400)

        print(f"Входной текст:  {text!r}")
        print(f"TTL:            {ttl_key} ({ttl_seconds} сек)")
        print()

        bf_code = compile_text(text)
        bf_with_ttl, expires_at = wrap_simple(bf_code, ttl_seconds)

        print(f"Brainfuck без TTL  ({len(bf_code)} символов)")
        print(f"Brainfuck с TTL    ({len(bf_with_ttl)} символов)")
        print(f"Истекает:          {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_at))}")
        print()

        binary = encode_to_bin(bf_with_ttl)
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
            stdin_token = get_stdin_token()
            result = run_bf(bf_code, stdin=stdin_token)
            if result:
                print(f"Результат:")
                print(result)
            else:
                print("Сообщение недоступно (TTL истёк или неверный токен)")
        except BrainfuckError as e:
            print(f"Ошибка выполнения: {e}")


if __name__ == "__main__":
    main()
