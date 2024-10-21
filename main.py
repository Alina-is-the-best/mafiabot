import telebot
import random

bot = telebot.TeleBot('7883139018:AAGaMHDoRfVT6K2V7FaGQwETVxrRlP2Wu2M')
user_dict = {}

# Словарь для хранения зарегистрированных пользователей и их кодов игр
registered_users = {0: {'group_title': 'haha', 'id': []}, 1: {'group_title': 'Проверка 2', 'group_id': -1002269387767, 'id': [1195384026], 'names': {1195384026: 'Ponyo'}}}
# роли игроков
roles = []
# костыль всех костылей, тут типо хранится айди президента, котором отравили сообщение с выбором карты, а значение - это айди сообщения
user_message_ids = {}


# первое взаимодействие с ботом
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет, я бот для игры в мафию! Используйте команду /register, чтобы зарегистрироваться для игры.")


# промежуточный этап запроса кода игры
@bot.message_handler(commands=['register'])
def register_user(message):
    msg = bot.reply_to(message, "Пожалуйста, введите номер игры для регистрации:")
    bot.register_next_step_handler(msg, process_game_code)


def process_game_code(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    game_code = message.text

    try:
        registered_users[int(game_code)]['id'].append(user_id)
        registered_users[int(game_code)]['names'][user_id] = user_name
        # Сохраняем пользователя и код игры в словаре
        bot.reply_to(message, f"{user_name}, вы успешно зарегистрированы на игру в группе {registered_users[int(game_code)]['group_title']}!")
    except Exception as e:
        bot.reply_to(message, f"{user_name}, такого номера игры не существует!")

    print(registered_users)



@bot.message_handler(func=lambda message: True)
def check_message(message):
    if 'играем' in message.text.lower():
        # блокировка добавлений новых участников, исключение из списка повторяющиеся id, проверка достаточности количества участников
        for game_code in registered_users:
            if registered_users[game_code]['group_title'] == message.chat.title:
                if len(set(registered_users[game_code]['id'])) > 0:
                    registered_users[game_code]['id'] = set(registered_users[game_code]['id'])
                    send_private_messages(message.chat.title)
                else:
                    bot.send_message(message.chat.id,
                                     f'У вас недостаточное количество игроков, игра будет неинтересной(. '
                                     f'Минимальное количество: '
                                     f'5, текущее количество: {len(set(registered_users[game_code]["id"]))}')

    if 'начать игру' in message.text.lower():
        # Получаем имя бота
        bot_username = bot.get_me().username

        # Создаем ссылку
        bot_link = f"https://t.me/{bot_username}"

        # Создаем встроенную клавиатуру
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton("Перейти к боту", url=bot_link)
        markup.add(button)
        # добавляем в словарь с регистрацией название группы и ее номер
        group_title = message.chat.title
        registered_users[max(registered_users) + 1] = {'group_title': group_title, 'group_id': message.chat.id, 'names': {}}
        registered_users[max(registered_users)]['id'] = []

        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id, f"Привет всем! Я - бот для игры в мафию. Уникальный кот вашей игры - {max(registered_users)}. "
                              f"\n Все пользователи, желающие сыграть, напишите мне в личные сообщения команду \register"
                                          f"\n Когда все желающие играть, будут зарегестрированы, напишите: играть, и мы начнем игру",
                         reply_markup=markup)


# отправка личных сообщений с ролью
def send_private_messages(chat_title):
    for game_code in registered_users:
        if registered_users[game_code]['group_title'] == chat_title:
            try:
                # вызов класса и присвоение ролей игрокам
                player_role = roles(registered_users[game_code]['id'])
                registered_users[game_code]['id'] = player_role.role_for_all()

                for user_id in registered_users[game_code]['id']:
                    if registered_users[game_code]['id'][user_id] == 'liberal':
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton("либерал",
                                                                     callback_data="либерал")
                        markup.add(button1)
                        # Отправляем сообщение с кнопками
                        bot.send_message(user_id, "Привет! Твоя роль: либерал", reply_markup=markup)
                    elif registered_users[game_code]['id'][user_id] == 'fascist':
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton("фашистик",
                                                                     callback_data="фашистик")
                        markup.add(button1)
                        # Отправляем сообщение с кнопками
                        bot.send_message(user_id, "Привет! Твоя роль: фашистик", reply_markup=markup)
                    elif registered_users[game_code]['id'][user_id] == 'gitler':
                        markup = telebot.types.InlineKeyboardMarkup()
                        button1 = telebot.types.InlineKeyboardButton("гитлер",
                                                                     callback_data="гитлер")
                        markup.add(button1)
                        # Отправляем сообщение с кнопками
                        bot.send_message(user_id, "Привет! Твоя роль: гитлер", reply_markup=markup)

                    # выбор первых президента и канцлера
                    registered_users[game_code] = first_raspred(registered_users[game_code])
                    print(registered_users[game_code]['och'])
                    president = registered_users[game_code]['och'][0]
                    chancellor = registered_users[game_code]['och'][len(registered_users[game_code]['och']) // 2]

                    # отправка сообщения в общую группу, нде идет разглашение того, кто является президентом и канцлером
                    bot.send_message(registered_users[game_code]['group_id'],
                                     f"Вот типо начали, your first president: "
                                     f"{registered_users[game_code]['names'][president]}, "
                                     f"your first chancellor: {registered_users[game_code]['names'][chancellor]} ")
                    # запуск основной игры
                    start_game(registered_users[game_code], president, chancellor)
            except Exception as e:
                print(f"Ошибка: {e}")


# вызов описания персонажа, следует написать описания всех персонажей

@bot.callback_query_handler(func=lambda call: call.data == "фашистик")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Ты тут злой', show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "либерал")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Борешься зо злом', show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "гитлер")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Ты тут вообще самый злой', show_alert=True)


@bot.callback_query_handler(func=lambda call: len(call.data.split()) == 2)
def callback_greet(call):
    user_id = call.message.chat.id

    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    bot.send_message(call.message.chat.id, f'Я передал канцлеру данные карты: {list(call.data.split())}')


def first_raspred(dict_of_group):
    ochered = list(dict_of_group['id'].keys())
    random.shuffle(ochered)
    dict_of_group['och'] = ochered
    return dict_of_group


def main():
    bot.polling(none_stop=True)


def start_game(dict_of_group, president, chancellor):
    coloda = Cards()
    cards_to_choose = coloda.card_on_board()
    # отправляю президенту карты, которые ему выпали, добавить кнопки
    # Создаем клавиатуру
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton(cards_to_choose[0], callback_data=cards_to_choose[1] + ' ' + cards_to_choose[2])
    btn2 = telebot.types.InlineKeyboardButton(cards_to_choose[1], callback_data=cards_to_choose[0] + ' ' + cards_to_choose[2])
    btn3 = telebot.types.InlineKeyboardButton(cards_to_choose[2], callback_data=cards_to_choose[0] + ' ' + cards_to_choose[1])

    # Добавляем кнопки в клавиатуру
    markup.add(btn1, btn2, btn3)

    # Отправляем сообщение с клавиатурой
    sent_message  = bot.send_message(president,
                    f"okay, mister president: you have cards: {cards_to_choose}"
                    f", выберите карту, от которой хотите избавиться", reply_markup=markup)

    # Сохраняем ID отправленного сообщения в памяти пользователя
    user_message_ids[president] = sent_message.message_id



class roles:
    def __init__(self, sps):
        self.count_of_membres = len(sps)
        self.players = list(sps)
        print(sps)
        self.players_roles = {}
        self.roles = []

    def roles_from_count(self):
        if self.count_of_membres == 5:
            self.roles = ['liberal', 'liberal', 'liberal', 'fascist', 'hitler']
        elif self.count_of_membres == 6:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'hitler']
        elif self.count_of_membres == 7:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'fascist', 'hitler']
        elif self.count_of_membres == 8:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'fascist', 'hitler']
        elif self.count_of_membres == 9:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'fascist', 'fascist', 'hitler']
        elif self.count_of_membres == 10:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'fascist', 'fascist',
                          'hitler']
        # test
        elif self.count_of_membres == 2:
            self.roles = ['fascist', 'liberal']
        elif self.count_of_membres == 1:
            self.roles = ['liberal']
        return self.roles

    def role_for_all(self):
        self.roles = self.roles_from_count()
        random.shuffle(self.roles)
        for i in range(self.count_of_membres):
            self.players_roles[self.players[i]] = self.roles[i]
        return self.players_roles


# Класс карточек законов
class Cards:
    def __init__(self):
        self.cards_in = ["fascist"] * 11 + ["liberal"] * 6     # карты в колоде
        self.cards_out = []     # сюда надо складывать карты, которые откинули игроки

    # выкладка закона на стол
    def card_on_board(self):
        if len(self.cards_in) < 3:
            self.cards_in = self.cards_out + self.cards_in
            self.cards_out = []
        card = [random.choice(self.cards_in)] # Рандомно выбираем первую карту
        self.cards_in.remove(card[0])  # Удаляем 1 карту из списка карт в колоде
        card = card + [random.choice(self.cards_in)] # Рандомно выбираем вторую карту закидываем обе карты в общий список
        self.cards_in.remove(card[1]) # Удаляем 2 карту из списка
        card = card + [random.choice(self.cards_in)]    # Рандомно выбираем третью карту закидываем три карты в общий список
        self.cards_in.remove(card[2])  # Удаляем 3 карту из списка
        return card


class CardsOnBoard:
    # два списка: либеральные карты на столе, фашистские карты на столе
    def __init__(self):
        self.onboard_liberal = []
        self.onboard_fascist = []

    def move(self, cards):
        player_choose = cards.card_on_board
        # сюда добавить что выбирает игрок что откидывает, что откидывается идет в cards.cards_out
        # остальное идет президенту тоже самое происходит с выбором президента
        if chosen_card == "liberal":
            self.onboard_liberal.append(chosen_card)
        else:
            self.onboard_fascist.append(chosen_card)


if __name__ == "__main__":
    main()