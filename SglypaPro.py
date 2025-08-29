# -*- coding: utf-8 -*-
# meta developer: @Rezoxss
# scope: hikka_only

from .. import loader, utils
import logging
import random
import re
from collections import deque

logger = logging.getLogger(__name__)

@loader.tds
class SglypaMod(loader.Module):
    """Модуль для генерации сглып как у @sglypa_tg_bot"""
    
    strings = {
        "name": "Sglypa",
        "on": "✅ Режим сглыпы включен! Теперь я буду отвечать сглыпами",
        "off": "❌ Режим сглыпы выключен",
        "already_on": "⚠️ Режим сглыпы уже включен",
        "already_off": "⚠️ Режим сглыпы уже выключен",
    }

    def __init__(self):
        self.active = False
        self.chat_history = {}
        self.words_db = self.load_words_database()

    def load_words_database(self):
        """База слов для генерации сглып"""
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
                "голова", "рука", "нога", "спина", "живот", "нос", "ухо",
                "придурок", "болван", "чудак", "странник", "мечтатель", "фантазер"
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
        """Добавляем слова в историю чата"""
        if chat_id not in self.chat_history:
            self.chat_history[chat_id] = deque(maxlen=50)
        
        if not text:
            return
            
        words = re.findall(r'\b[а-яё]{3,}\b', text.lower())
        for word in words:
            if word not in ['это', 'вот', 'как', 'что', 'там', 'здесь', 'тут']:
                self.chat_history[chat_id].append(word)

    def get_chat_word(self, chat_id):
        """Берём слово из истории чата"""
        if chat_id in self.chat_history and self.chat_history[chat_id]:
            return random.choice(list(self.chat_history[chat_id]))
        return None

    def generate_sglypa(self, chat_id=None):
        """Генерируем сглыпу"""
        patterns = [
            "А вот и {} {} {}", "И тут {} {} {}", "Внезапно {} {} {}",
            "Неожиданно {} {} {}", "Как же {} {} {}", "Ох уж эта {} {} {}",
            "Что за {} {} {}", "Эта {} {} {}", "Моя {} {} {}", "Твоя {} {} {}",
            "Наша {} {} {}", "{} {} {} прямо сейчас", "{} {} {} снова",
            "{} {} {} опять", "Посмотрите, {} {} {}", "Кажется, {} {} {}",
            "Наверное, {} {} {}", "Возможно, {} {} {}", "{} {} {} в чате",
            "{} {} {} здесь", "Ничего себе, {} {} {}", "Ух ты, {} {} {}",
            "Вау, {} {} {}", "Ого, {} {} {}", "Вот это {} {} {}"
        ]

        chat_word = self.get_chat_word(chat_id)
        word1 = chat_word if chat_word else random.choice(self.words_db["nouns"])
        word2 = random.choice(self.words_db["adjectives"])
        word3 = random.choice(self.words_db["verbs"])

        return random.choice(patterns).format(word2, word1, word3)

    @loader.command()
    async def sglypa(self, message):
        """Включить/выключить режим или сгенерировать сглыпу - .sglypa on/off"""
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        
        if message.text:
            self.add_to_history(chat_id, message.text)

        if not args:
            sglypa_text = self.generate_sglypa(chat_id)
            await utils.answer(message, sglypa_text)
            return
            
        if args.lower() == "on":
            if self.active:
                await utils.answer(message, self.strings("already_on"))
            else:
                self.active = True
                await utils.answer(message, self.strings("on"))
                
        elif args.lower() == "off":
            if not self.active:
                await utils.answer(message, self.strings("already_off"))
            else:
                self.active = False
                await utils.answer(message, self.strings("off"))
                
        else:
            sglypa_text = self.generate_sglypa(chat_id)
            await utils.answer(message, sglypa_text)

    @loader.watcher()
    async def watcher(self, message):
        """Отслеживаем сообщения для ответов"""
        if not self.active:
            return
            
        chat_id = utils.get_chat_id(message)
        
        # Не отвечаем на свои сообщения, команды и пустые
        if not message.text or message.out or message.text.startswith('.'):
            return
            
        self.add_to_history(chat_id, message.text)
        
        # 35% шанс ответа
        if random.randint(1, 100) > 35:
            return
            
        try:
            sglypa_text = self.generate_sglypa(chat_id)
            await message.reply(sglypa_text)
        except Exception as e:
            logger.error(f"Ошибка: {e}")

    async def on_unload(self):
        """Очистка при выгрузке модуля"""
        self.chat_history.clear()
