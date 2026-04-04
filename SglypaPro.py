meta developer: @vzlonka1
from .. import loader, utils

@loader.tds
class AutoGiveTargetMod(loader.Module):
    """Авто-выдача /give 1 получателю подарка"""
    strings = {"name": "AutoGiveTarget"}

    async def client_ready(self, client, db):
        self.db = db
        self.active_chats = self.db.get("AutoGiveTarget", "chats", [])
        self.bot_id = 1520369962

    @loader.command()
    async def givechat(self, message):
        """/givechat - Включить/выключить авто-выдачу в чате"""
        cid = message.chat_id
        if cid in self.active_chats:
            self.active_chats.remove(cid)
            res = "выключен"
        else:
            self.active_chats.append(cid)
            res = "включен"
        
        self.db.set("AutoGiveTarget", "chats", self.active_chats)
        await message.edit(f"<b>[AutoGive]</b> Режим раздачи {res}!")

    @loader.watcher(only_messages=True)
    async def watcher(self, message):
        # Проверяем ID бота Мафии и включен ли чат
        if message.sender_id != self.bot_id or message.chat_id not in self.active_chats:
            return

        text = message.text
        # Ищем ключевую связку "подарил" и " к "
        if "подарил" in text and " к " in text:
            try:
                # Разбиваем строку по " к ", берем правую часть
                target = text.split(" к ")[1].strip()
                
                # Убираем восклицательный знак, если он есть в конце ника
                if target.endswith("!"):
                    target = target[:-1]
                
                # Если ник очень длинный или с пробелами (как в прошлом примере),
                # этот метод все равно его подцепит целиком.
                await message.respond(f"/give 1 {target}")
            except Exception:
                pass
