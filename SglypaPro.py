# -*- coding: utf-8 -*-
# meta developer: @Rezoxss
# scope: hikka_only

from .. import loader, utils
import logging
import random
import re
import asyncio
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

@loader.tds
class SmartSglypaMod(loader.Module):
    """Умный модуль сглыпы с ChatGPT логикой"""
    
    strings = {
        "name": "SmartSglypa",
        "on": "✅ Режим сглыпы включен! Теперь я буду отвечать сглыпами",
        "off": "❌ Режим сглыпы выключен",
        "already_on": "⚠️ Режим сглыпы уже включен",
        "already_off": "⚠️ Режим сглыпы уже выключен",
        "cleared": "🗑️ История чата очищена",
        "stats": "📊 Сообщений в истории: {}"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "reply_chance",
                40,
                "Шанс ответа в % (40%)",
                validator=loader.validators.Integer(minimum=1, maximum=100)
            ),
            loader.ConfigValue(
                "use_ai",
                True,
                "Использовать умные ответы",
                validator=loader.validators.Boolean()
            )
        )
        self.active = False
        self.chat_history = defaultdict(list)  # Бесконечная история
        self.words_db = self.load_words_database()

    def load_words_database(self):
        """База слов для умных ответов"""
        return {
            "nouns": [
                "кошка", "собака", "птица", "рыба", "мышь", "хомяк", "кролик", 
                "черепаха", "лягушка", "бегемот", "носорог", "слон", "жираф",
                "тигр", "лев", "волк", "лиса", "медведь", "енот", "бобер",
                "помидор", "огурец", "картошка", "морковка", "капуста", "яблоко",
                "груша", "апельсин", "банан", "клубника", "малина", "вишня",
                "пицца", "бургер", "суп", "салат", "мороженое", "шоколад",
                "стол", "стул", "кровать", "шкаф", "полка", "лампа", "окно",
                "дверь", "компьютер", "телефон", "книга", "тетрадь", "ручка",
                "человек", "друг", "брат", "сестра", "мама", "папа", "дед",
                "голова", "рука", "нога", "спина", "живот", "нос", "ухо"
            ],
            "adjectives": [
                "красный", "синий", "зеленый", "желтый", "оранжевый", "фиолетовый",
                "розовый", "коричневый", "черный", "белый", "серый", "голубой",
                "большой", "маленький", "огромный", "крошечный", "высокий", "низкий",
                "толстый", "тонкий", "пушистый", "гладкий", "шершавый", "мокрый",
                "сухой", "горячий", "холодный", "теплый", "прохладный", "свежий",
                "старый", "новый", "молодой", "древний", "современный", "быстрый",
                "медленный", "умный", "глупый", "веселый", "грустный", "злой",
                "смешной", "серьезный", "важный", "необычный", "странный", "удивительный"
            ],
            "verbs": [
                "бежит", "летит", "плывет", "ползет", "прыгает", "скачет",
                "сидит", "стоит", "лежит", "висит", "растет", "цветет",
                "падает", "поднимается", "вращается", "качается", "блестит",
                "шумит", "молчит", "поет", "говорит", "кричит", "шепчет",
                "ест", "пьет", "спит", "бодрствует", "работает", "отдыхает",
                "смеется", "плачет", "думает", "мечтает", "хочет", "может",
                "исследует", "открывает", "создает", "творит", "строит", "играет"
            ]
        }

    async def client_ready(self, client, db):
        self._client = client

    def add_to_history(self, chat_id, text):
        """Добавляем сообщение в бесконечную историю"""
        if text and len(text) > 2:
            words = re.findall(r'\b[а-яё]{3,}\b', text.lower())
            for word in words:
                if word not in ['это', 'вот', 'как', 'что', 'там', 'здесь']:
                    self.chat_history[chat_id].append(word)

    def get_chat_words(self, chat_id, count=3):
        """Получаем слова из истории чата"""
        if chat_id in self.chat_history and self.chat_history[chat_id]:
            history_words = list(self.chat_history[chat_id])
            if len(history_words) >= count:
                return random.sample(history_words, count)
            else:
                # Дополняем случайными словами если не хватает
                result = history_words.copy()
                while len(result) < count:
                    result.append(random.choice(self.words_db["nouns"]))
                return result
        return
