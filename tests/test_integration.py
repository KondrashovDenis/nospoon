"""
Интеграционный тест полного флоу Spoon Messenger.
Требует реальных подключений к IPFS и relay.
Запускать отдельно: pytest tests/test_integration.py -v
"""

import pytest
import sys
sys.path.insert(0, 'd:/VS_projects/nospoon')


def test_full_flow():
    """
    Полный флоу: encode → upload IPFS → publish relay
                 → get feed → download IPFS → decode
    """
    from transport.messenger import SpoonMessenger

    messenger = SpoonMessenger()
    circle_key = 'test_circle_integration'
    text = 'Hello from Spoon Messenger'

    # Отправить
    send_result = messenger.send(
        text=text,
        circle_key=circle_key,
        ttl_seconds=3600
    )
    assert send_result['success'] is True
    assert send_result['cid']
    print(f"\nCID: {send_result['cid']}")

    # Получить
    messages = messenger.receive(circle_key=circle_key)
    assert len(messages) > 0

    # Найти наше сообщение
    our_message = next(
        (m for m in messages if m['cid'] == send_result['cid']),
        None
    )
    assert our_message is not None
    assert our_message['success'] is True
    assert our_message['text'] == text
    print(f"Декодировано: {our_message['text']!r}")


def test_stats():
    """Статистика доступна"""
    from transport.relay_client import RelayClient
    client = RelayClient()
    stats = client.get_stats()
    assert 'total_messages' in stats
    print(f"\nStats: {stats}")
