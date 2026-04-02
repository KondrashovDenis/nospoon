#!/usr/bin/env python3
"""CLI прототип Spoon Messenger — проверка цепочки кодирования"""

import sys
import os
import time
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.codec import encode, decode, get_ttl_options


def main():
    if len(sys.argv) < 2:
        print("Spoon Messenger CLI")
        print()
        print("Использование:")
        print("  python cli.py encode \"текст\" [ttl] [пароль]")
        print("  python cli.py decode file.bin [пароль]")
        print()
        print("TTL варианты: 1h / 6h / 24h / 7d (по умолчанию: 24h)")
        print()
        print("Примеры:")
        print("  python cli.py encode \"Hello\" 1h")
        print("  python cli.py encode \"Secret\" 24h mypassword")
        print("  python cli.py decode message.bin")
        print("  python cli.py decode message.bin mypassword")
        return

    command = sys.argv[1]
    ttl_options = get_ttl_options()

    if command == 'encode':
        if len(sys.argv) < 3:
            print("Укажи текст: python cli.py encode \"Hello\"")
            return

        text     = sys.argv[2]
        ttl_key  = sys.argv[3] if len(sys.argv) > 3 else '24h'
        password = sys.argv[4] if len(sys.argv) > 4 else None
        ttl_seconds = ttl_options.get(ttl_key, 86400)

        print("Кодирование...")
        print(f"   Текст:    {text!r}")
        print(f"   TTL:      {ttl_key}")
        if password:
            print(f"   Пароль:   {'*' * len(password)}")
        print()

        try:
            result = encode(text, ttl_seconds=ttl_seconds, password=password)

            print(f"   BF код:   {len(result.bf_code)} символов")
            print(f"   С TTL:    {len(result.bf_with_ttl)} символов")
            print(f"   .bin:     {result.size_bytes} байт")
            print(f"   Истекает: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.expires_at))}")
            print()

            filename = 'message.bin'
            with open(filename, 'wb') as f:
                f.write(result.binary)
            print(f"Сохранено: {filename}")

        except ValueError as e:
            print(f"Ошибка: {e}")

    elif command == 'decode':
        if len(sys.argv) < 3:
            print("Укажи файл: python cli.py decode message.bin")
            return

        filename = sys.argv[2]
        password = sys.argv[3] if len(sys.argv) > 3 else None

        if not os.path.exists(filename):
            print(f"Файл не найден: {filename}")
            return

        print(f"Декодирование {filename}...")
        if password:
            print(f"   Пароль: {'*' * len(password)}")
        print()

        with open(filename, 'rb') as f:
            data = f.read()

        result = decode(data, password=password)

        if result.success:
            print("Результат:")
            print()
            print(result.text)
        else:
            print(f"Ошибка: {result.error}")


if __name__ == "__main__":
    main()
