# -*- coding: utf-8 -*-
# meta developer: @Rezoxss
# scope: hikka_only

from .. import loader, utils
import logging
import random
import re
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

@loader.tds
class SmartSglypaMod(loader.Module):
    """Умный модуль сглыпы с псевдо-нейросетевой логикой"""
    
    strings = {
        "name": "SmartSglypa",
        "on": "✅ Умный режим сглыпы включен! AI логика активирована",
        "off": "❌ Режим сглыпы выключен",
        "already_on": "⚠️ Режим уже включен",
        "already_off": "⚠️ Режим уже выключен",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "reply_chance",
                40,
                "Шанс ответа в %",
                validator=loader.validators.Integer(minimum=1, maximum=100)
            ),
            loader.ConfigValue(
                "ai_intelligence",
                80,
                "Уровень интеллекта AI",
                validator=loader.validators.Integer(minimum=1, maximum=100)
            )
        )
        self.active_chats = set()
        self.chat_history = defaultdict(list)
        self.markov_chains = defaultdict(dict)

    async def client_ready(self, client, db):
        self._client = client

    def add_to_history(self, chat_id, text):
        """Добавляем сообщение в историю и строим марковскую цепь"""
        if text and len(text) > 2:
            words = re.findall(r'\b[а-яё]{2,}\b', text.lower())
            for word in words:
                if word not in ['это', 'вот', 'как', 'что', 'там', 'здесь']:
                    self.chat_history[chat_id].append(word)
            
            # Строим простую марковскую цепь для AI
            if len(words) > 1:
                for i in range(len(words) - 1):
                    current_word = words[i]
                    next_word = words[i + 1]
                    if current_word not in self.markov_chains[chat_id]:
                        self.markov_chains[chat_id][current_word] = []
                    self.markov_chains[chat_id][current_word].append(next_word)

    def generate_ai_sglypa(self, chat_id):
        """Генерируем сглыпу с псевдо-AI логикой"""
        # Используем марковскую цепь если есть данные
        if (chat_id in self.markov_chains and self.markov_chains[chat_id] and 
            random.randint(1, 100) <= self.config["ai_intelligence"]):
            
            try:
                # Выбираем случайное стартовое слово
                current_word = random.choice(list(self.markov_chains[chat_id].keys()))
                result = [current_word]
                
                # Генерируем цепочку слов
                for _ in range(random.randint(2, 6)):
                    if (current_word in self.markov_chains[chat_id] and 
                        self.markov_chains[chat_id][current_word]):
                        next_word = random.choice(self.markov_chains[chat_id][current_word])
                        result.append(next_word)
                        current_word = next_word
                    else:
                        break
                
                # Добавляем префикс
                prefixes = [
                    "AI: ", "Нейросеть: ", "ГПТ: ", "Мозг: ", "🤖 ", "🧠 ",
                    "Вот что я думаю: ", "Мой анализ: ", "Генерирую: "
                ]
                
                return random.choice(prefixes) + " ".join(result).capitalize()
                
            except Exception as e:
                logger.error(f"Ошибка AI: {e}")
                return self.generate_fallback_sglypa(chat_id)
        else:
            return self.generate_fallback_sglypa(chat_id)

    def generate_fallback_sglypa(self, chat_id):
        """Классическая генерация сглыпы"""
        patterns = [
            "{} {} {}", "{} {} {} {}", "{} {} {} {} {}", 
            "{} {} {} {} {} {}", "{} {} {} {} {} {} {}",
            "блядь {} {}", "нахуй {} {}", "пиздец {} {}", "ёбаный {} {}",
            "заебись {} {}", "отъебись {} {}", "ебать {} {}", "хуярить {} {}",
            "а вот и {} {}", "и тут {} {}", "внезапно {} {}", "неожиданно {} {}",
            "как же {} {}", "ох уж эта {} {}", "что за {} {}", "эта {} {}",
            "моя {} {}", "твоя {} {}", "наша {} {}", "посмотрите {} {}",
            "кажется {} {}", "наверное {} {}", "возможно {} {}", "интересно {} {}"
        ]
        
        if chat_id in self.chat_history and self.chat_history[chat_id]:
            words = list(self.chat_history[chat_id])
        else:
            words = ["сглыпа", "пидор", "жопа", "хуй", "пизда", "еблан", "мудак"]
        
        pattern = random.choice(patterns)
        num_slots = pattern.count("{}")
        
        result = pattern
        for _ in range(num_slots):
            if words:
                word = random.choice(words)
                result = result.replace("{}", word, 1)
            else:
                result = result.replace("{}", "сглыпа", 1)
        
        # Добавляем AI метку если интеллект высокий
        if random.randint(1, 100) <= self.config["ai_intelligence"]:
            ai_tags = ["[AI]", "[GPT]", "[Нейросеть]", "[Мозг]", "🤖", "🧠"]
            result = f"{random.choice(ai_tags)} {result}"
        
        return result.capitalize()

    @loader.command()
    async def sglypa(self, message):
        """Сгенерировать сглыпу - .sglypa [on/off/status/clear]"""
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        
        if message.text:
            self.add_to_history(chat_id, message.text)

        if not args:
            sglypa_text = self.generate_ai_sglypa(chat_id)
            await utils.answer(message, sglypa_text)
            return
            
        if args.lower() == "on":
            if chat_id in self.active_chats:
                await utils.answer(message, self.strings("already_on"))
            else:
                self.active_chats.add(chat_id)
                await utils.answer(message, self.strings("on"))
                
        elif args.lower() == "off":
            if chat_id not in self.active_chats:
                await utils.answer(message, self.strings("already_off"))
            else:
                self.active_chats.discard(chat_id)
                await utils.answer(message, self.strings("off"))
                
        elif args.lower() == "status":
            # Статистика по чату
            chat_words = len(self.chat_history.get(chat_id, []))
            chat_chains = len(self.markov_chains.get(chat_id, {}))
            active_status = "✅ Включен" if chat_id in self.active_chats else "❌ Выключен"
            
            status_text = (
                f"📊 Статус сглыпы:\n"
                f"{active_status}\n"
                f"🗣️ Слов в истории: {chat_words}\n"
                f"🧠 AI цепочек: {chat_chains}\n"
                f"🎯 Шанс ответа: {self.config['reply_chance']}%\n"
                f"🤖 Умность AI: {self.config['ai_intelligence']}%"
            )
            await utils.answer(message, status_text)
            return
                
        elif args.lower() == "clear":
            if chat_id in self.chat_history:
                self.chat_history[chat_id].clear()
                self.markov_chains[chat_id].clear()
            await utils.answer(message, "🗑️ История и AI данные очищены")
            return
                
        else:
            sglypa_text = self.generate_ai_sglypa(chat_id)
            await utils.answer(message, sglypa_text)

    @loader.watcher()
    async def watcher(self, message):
        """Отслеживаем сообщения с AI ответами"""
        chat_id = utils.get_chat_id(message)
        
        if chat_id not in self.active_chats:
            return
            
        if not message.text or message.out or message.text.startswith('.'):
            return
            
        self.add_to_history(chat_id, message.text)
        
        # Реагируем на слово "сглыпа"
        if re.search(r'сглыпа', message.text, re.IGNORECASE):
            sglypa_text = self.generate_ai_sglypa(chat_id)
            await message.reply(sglypa_text)
            return
            
        # Обычный шанс ответа
        if random.randint(1, 100) <= self.config["reply_chance"]:
            sglypa_text = self.generate_ai_sglypa(chat_id)
            await message.reply(sglypa_text)

    async def on_unload(self):
        self.active_chats.clear()
        self.chat_history.clear()
        self.markov_chains.clear()