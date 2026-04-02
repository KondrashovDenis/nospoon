"""
Cloudflare Workers relay клиент для Spoon Messenger.
Публикация и получение CID по ключу круга.
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# URL задеплоенного Worker — заполним после деплоя
RELAY_URL = os.getenv('RELAY_URL', 'https://spoon-messenger-relay.workers.dev')


class RelayError(Exception):
    """Ошибка relay клиента"""
    pass


class RelayClient:
    def __init__(self, relay_url: str = None):
        self.relay_url = relay_url or RELAY_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def publish(
        self,
        circle_key: str,
        cid: str,
        expires_at: Optional[int] = None
    ) -> bool:
        """
        Опубликовать CID в круг.

        Вход:
            circle_key — ключ круга
            cid        — IPFS CID хэш
            expires_at — Unix timestamp истечения (опционально)
        Выход:
            True если успешно
        """
        url = f"{self.relay_url}/circle/{circle_key}/publish"
        payload = {'cid': cid}
        if expires_at:
            payload['expires_at'] = expires_at * 1000  # в миллисекунды

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('success', False)
        except requests.RequestException as e:
            raise RelayError(f"Ошибка публикации CID: {e}")

    def get_feed(self, circle_key: str) -> list:
        """
        Получить список CID для круга.

        Вход:
            circle_key — ключ круга
        Выход:
            список dict с полями: cid, published_at, expires_at
        """
        url = f"{self.relay_url}/circle/{circle_key}/feed"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('entries', [])
        except requests.RequestException as e:
            raise RelayError(f"Ошибка получения feed: {e}")

    def get_stats(self) -> dict:
        """
        Получить статистику сети.

        Выход:
            dict с полями: total_messages, updated_at
        """
        url = f"{self.relay_url}/stats"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RelayError(f"Ошибка получения stats: {e}")

    def delete_cid(self, circle_key: str, cid: str) -> bool:
        """
        Удалить CID из круга.
        """
        url = f"{self.relay_url}/circle/{circle_key}/cid/{cid}"

        try:
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('success', False)
        except requests.RequestException as e:
            raise RelayError(f"Ошибка удаления CID: {e}")


def get_relay_client() -> RelayClient:
    """Фабричная функция — получить настроенный клиент"""
    return RelayClient()
