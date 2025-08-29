# -*- coding: utf-8 -*-
# meta developer: @Rezoxss
# scope: hikka_only

from .. import loader, utils
import logging
import random
import re
import asyncio
from collections import defaultdict
import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Tokenizer

logger = logging.getLogger(__name__)

@loader.tds
class NeuralSglypaMod(loader.Module):
    """Нейросетевой модуль сглыпы с PyTorch и GPT"""
    
    strings = {
        "name": "NeuralSglypa",
        "on": "✅ Нейросетевой режим сглыпы включен! GPT модель активирована",
        "off": "❌ Режим сглыпы выключен",
        "already_on": "⚠️ Режим уже включен",
        "already_off": "⚠️ Режим уже выключен",
        "model_loading": "🔄 Загружаю нейросетевую модель...",
        "model_ready": "✅ GPT модель готова к генерации!",
        "model_error": "❌ Ошибка загрузки модели"
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
                "use_neural",
                True,
                "Использовать нейросеть",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "temperature",
                0.9,
                "Температура генерации",
                validator=loader.validators.Float(minimum=0.1, maximum=2.0)
            )
        )
        self.active_chats = set()
        self.chat_history = defaultdict(list)
        self.model = None
        self.tokenizer = None
        self.model_loaded = False

    async def client_ready(self, client, db):
        self._client = client
        # Загружаем модель в фоне
        asyncio.create_task(self.load_model())

    async def load_model(self):
        """Загружаем нейросетевую модель"""
        try:
            logger.info(self.strings["model_loading"])
            self.tokenizer = GPT2Tokenizer.from_pretrained('sberbank-ai/rugpt3small_based_on_gpt2')
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = GPT2LMHeadModel.from_pretrained('sberbank-ai/rugpt3small_based_on_gpt2')
            self.model_loaded = True
            logger.info(self.strings["model_ready"])
        except Exception as e:
            logger.error(f"{self.strings['model_error']}: {e}")
            self.model_loaded = False

    def add_to_history(self, chat_id, text):
        """Добавляем сообщение в историю"""
        if text and len(text) > 2:
            words = re.findall(r'\b[а-яё]{2,}\b', text.lower())
            for word in words:
                if word not in ['это', 'вот', 'как', 'что', 'там', 'здесь']:
                    self.chat_history[chat_id].append(word)

    def generate_neural_sglypa(self, chat_id):
        """Генерируем сглыпу через нейросеть"""
        if not self.model_loaded:
            return self.generate_fallback_sglypa(chat_id)
        
        try:
            # Берем контекст из истории чата
            context_words = []
            if chat_id in self.chat_history and self.chat_history[chat_id]:
                context_words = random.sample(self.chat_history[chat_id], 
                                           min(5, len(self.chat_history[chat_id])))
            
            # Создаем промпт для нейросети
            prompt = "Сглыпа: " + " ".join(context_words) + " "
            
            # Токенизируем
            inputs = self.tokenizer.encode(prompt, return_tensors='pt', max_length=50, truncation=True)
            
            # Генерируем текст
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=random.randint(20, 50),
                    num_return_sequences=1,
                    temperature=self.config["temperature"],
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    top_k=50,
                    top_p=0.9,
                    repetition_penalty=1.2
                )
            
            # Декодируем результат
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Извлекаем только сгенерированную часть
            result = generated_text.replace(prompt, "").strip()
            
            # Чистим результат
            result = re.sub(r'[^а-яёА-ЯЁ\s]', '', result)
            result = ' '.join(result.split()[:random.randint(3, 8)])
            
            return result.capitalize()
            
        except Exception as e:
            logger.error(f"Ошибка нейросети: {e}")
            return self.generate_fallback_sglypa(chat_id)

    def generate_fallback_sglypa(self, chat_id):
        """Резервная генерация если нейросеть не работает"""
        patterns = [
            "{} {} {}", "{} {} {} {}", "{} {} {} {} {}", 
            "блядь {} {}", "нахуй {} {}", "пиздец {} {}",
            "ёбаный {} {}", "заебись {} {}", "отъебись {} {}",
            "а вот и {} {}", "и тут {} {}", "внезапно {} {}"
        ]
        
        if chat_id in self.chat_history and self.chat_history[chat_id]:
            words = list(self.chat_history[chat_id])
        else:
            words = ["сглыпа", "пидор", "жопа", "хуй", "пизда", "еблан"]
        
        pattern = random.choice(patterns)
        num_slots = pattern.count("{}")
        
        result = pattern
        for _ in range(num_slots):
            if words:
                word = random.choice(words)
                result = result.replace("{}", word, 1)
            else:
                result = result.replace("{}", "сглыпа", 1)
        
        return result.capitalize()

    @loader.command()
    async def sglypa(self, message):
        """Сгенерировать сглыпу через нейросеть - .sglypa [on/off]"""
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        
        if message.text:
            self.add_to_history(chat_id, message.text)

        if not args:
            if self.config["use_neural"] and self.model_loaded:
                sglypa_text = self.generate_neural_sglypa(chat_id)
            else:
                sglypa_text = self.generate_fallback_sglypa(chat_id)
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
            status = "✅ Модель загружена" if self.model_loaded else "❌ Модель не загружена"
            await utils.answer(message, f"Статус нейросети: {status}")
                
        else:
            if self.config["use_neural"] and self.model_loaded:
                sglypa_text = self.generate_neural_sglypa(chat_id)
            else:
                sglypa_text = self.generate_fallback_sglypa(chat_id)
            await utils.answer(message, sglypa_text)

    @loader.watcher()
    async def watcher(self, message):
        """Отслеживаем сообщения с нейросетевыми ответами"""
        chat_id = utils.get_chat_id(message)
        
        if chat_id not in self.active_chats:
            return
            
        if not message.text or message.out or message.text.startswith('.'):
            return
            
        self.add_to_history(chat_id, message.text)
        
        # Реагируем на слово "сглыпа"
        if re.search(r'сглыпа', message.text, re.IGNORECASE):
            if self.config["use_neural"] and self.model_loaded:
                sglypa_text = self.generate_neural_sglypa(chat_id)
            else:
                sglypa_text = self.generate_fallback_sglypa(chat_id)
            await message.reply(sglypa_text)
            return
            
        # Обычный шанс ответа
        if random.randint(1, 100) <= self.config["reply_chance"]:
            if self.config["use_neural"] and self.model_loaded:
                sglypa_text = self.generate_neural_sglypa(chat_id)
            else:
                sglypa_text = self.generate_fallback_sglypa(chat_id)
            await message.reply(sglypa_text)

    async def on_unload(self):
        """Выгрузка модели"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        self.active_chats.clear()
        self.chat_history.clear()