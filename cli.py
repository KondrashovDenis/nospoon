#!/usr/bin/env python3
"""CLI прототип Spoon Messenger"""

import sys
import os
import time
sys.path.insert(0, 'd:/VS_projects/nospoon')

from core.codec import encode, decode, get_ttl_options
from transport.messenger import SpoonMessenger, MessengerError


def main():
    if len(sys.argv) < 2:
        print("Spoon Messenger CLI v1.0.0")
        print()
        print("Локальные команды:")
        print("  python cli.py encode \"текст\" [ttl] [пароль]")
        print("  python cli.py decode file.bin [пароль]")
        print()
        print("Сетевые команды:")
        print("  python cli.py send \"текст\" circle_key [ttl] [пароль]")
        print("  python cli.py inbox circle_key [пароль]")
        print("  python cli.py stats")
        print()
        print("TTL варианты: 1h / 6h / 24h / 7d (по умолчанию: 24h)")
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
        with open(filename, 'rb') as f:
            data = f.read()

        result = decode(data, password=password)
        if result.success:
            print("Результат:")
            print()
            print(result.text)
        else:
            print(f"Ошибка: {result.error}")

    elif command == 'send':
        if len(sys.argv) < 4:
            print("Использование: python cli.py send \"текст\" circle_key [ttl] [пароль]")
            return

        text       = sys.argv[2]
        circle_key = sys.argv[3]
        ttl_key    = sys.argv[4] if len(sys.argv) > 4 else '24h'
        password   = sys.argv[5] if len(sys.argv) > 5 else None
        ttl_seconds = ttl_options.get(ttl_key, 86400)

        print(f"Отправка в круг {circle_key!r}...")
        print(f"   Текст: {text!r}")
        print(f"   TTL:   {ttl_key}")
        print()

        try:
            messenger = SpoonMessenger()
            result = messenger.send(
                text=text,
                circle_key=circle_key,
                ttl_seconds=ttl_seconds,
                password=password
            )
            print("Отправлено!")
            print(f"   CID:      {result['cid']}")
            print(f"   Размер:   {result['size_bytes']} байт")
            print(f"   Истекает: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['expires_at']))}")
        except MessengerError as e:
            print(f"Ошибка: {e}")

    elif command == 'inbox':
        if len(sys.argv) < 3:
            print("Использование: python cli.py inbox circle_key [пароль]")
            return

        circle_key = sys.argv[2]
        password   = sys.argv[3] if len(sys.argv) > 3 else None

        print(f"Получение сообщений из круга {circle_key!r}...")
        print()

        try:
            messenger = SpoonMessenger()
            messages = messenger.receive(circle_key=circle_key, password=password)

            if not messages:
                print("Сообщений нет")
                return

            for i, msg in enumerate(messages, 1):
                published = msg.get('published_at', 0)
                if published:
                    published_str = time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        time.localtime(published / 1000)
                    )
                else:
                    published_str = 'неизвестно'

                print(f"[{i}] CID: {msg['cid'][:20]}...")
                print(f"     Опубликовано: {published_str}")
                if msg['success']:
                    print(f"     Текст: {msg['text']}")
                else:
                    print(f"     Ошибка: {msg['error']}")
                print()

        except MessengerError as e:
            print(f"Ошибка: {e}")

    elif command == 'stats':
        try:
            messenger = SpoonMessenger()
            stats = messenger.get_stats()
            print("Spoon Network Stats")
            print(f"   Сообщений всего: {stats.get('total_messages', 0)}")
            print(f"   Обновлено:       {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.get('updated_at', 0) / 1000))}")
        except MessengerError as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
