import telebot
import random #drt
from threading import Timer

bot = telebot.TeleBot('7883139018:AAGaMHDoRfVT6K2V7FaGQwETVxrRlP2Wu2M')
user_dict = {}

# Словарь для хранения зарегистрированных пользователей и их кодов игр
registered_users = {0: {'group_title': 'haha', 'id': []},
                    1: {'group_title': 'Проверка 2', 'group_id': -1002269387767, 'id': [1195384026],
                        'names': {1195384026: 'Ponyo'}}}
# роли игроков
roles = []
# костыль всех костылей, тут типо хранится айди президента, котором отравили сообщение с выбором карты,
# а значение - это айди сообщения
user_message_ids = {}


# первое взаимодействие с ботом
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет, я бот для игры в мафию! Используйте команду "
                          "/register, чтобы зарегистрироваться для игры.")


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
        bot.reply_to(message,
                     f"{user_name}, вы успешно зарегистрированы на игру в группе {registered_users[int(game_code)]['group_title']}!")
    except Exception as e:
        bot.reply_to(message, f"{user_name}, такого номера игры не существует!")

    print(registered_users)


@bot.message_handler(func=lambda message: True)
def check_message(message):
    if 'играем' in message.text.lower():
        # блокировка добавлений новых участников, исключение из списка повторяющиеся id, 
        # проверка достаточности количества участников
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
        registered_users[max(registered_users) + 1] = {'group_title': group_title, 'group_id': message.chat.id,
                                                       'names': {}}
        registered_users[max(registered_users)]['id'] = []

        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id,
                         f"Привет всем! Я - бот для игры в мафию. Уникальный кот вашей игры - {max(registered_users)}. "
                         f"\n Все пользователи, желающие сыграть, напишите мне в личные сообщения команду \register"
                         f"\n Когда все желающие играть, будут зарегестрированы, напишите: играть, и мы начнем игру",
                         reply_markup=markup)


# отправка личных сообщений с ролью
def send_private_messages(chat_title):
    for game_code in registered_users:
        if registered_users[game_code]['group_title'] == chat_title:
            try:
                # вызов класса и присвоение ролей игрокам
                player_role = role_for_everyone(registered_users[game_code]['id'])
                registered_users[game_code]['id'] = player_role.role_for_all()

                for user_id in registered_users[game_code]['id']:
                    print(user_id, registered_users[game_code]['id'][user_id])
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
                        # отправка ролей всех игроков
                        for i in registered_users[game_code]['id']:
                            print(i)
                            bot.send_message(user_id,
                                             f"{registered_users[game_code]['names'][i]}: {registered_users[game_code]['id'][i]}")

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

                # отправка сообщения в общую группу, нде идет разглашение того, кто является президентом и канцлером
                bot.send_message(registered_users[game_code]['group_id'],
                                 f"Вот типо начали, your first president: "
                                 f"{registered_users[game_code]['names'][president]}")
                # запуск основной игры
                start_game(registered_users[game_code], president)
            except Exception as e:
                print(f"Ошибка: {e}")


# нажата кнопка, я фашист, но что это
@bot.callback_query_handler(func=lambda call: call.data == "фашистик")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Ты тут злой', show_alert=True)


# нажата кнопка, я либерал, но что это
@bot.callback_query_handler(func=lambda call: call.data == "либерал")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Борешься зо злом', show_alert=True)


# нажата кнопка, я гитлер, но что это
@bot.callback_query_handler(func=lambda call: call.data == "гитлер")
def callback_greet(call):
    bot.answer_callback_query(
        call.id,
        text='Ты тут вообще самый злой', show_alert=True)


# нажата кнопка проверки игрока
@bot.callback_query_handler(func=lambda call: call.data[:2] == 'di')
def callback_greet(call):
    global waiting_for_answer, check_player

    user_id = call.message.chat.id
    check_player = int(call.data[2:])
    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    waiting_for_answer = 0


# нажата кнопка ликвидации игрока
@bot.callback_query_handler(func=lambda call: call.data[:2] == 'ki')
def callback_greet(call):
    global waiting_for_answer, kill_player

    user_id = call.message.chat.id
    kill_player = int(call.data[2:])
    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    waiting_for_answer = 0


# нажата кнопка выбора игрока канцлером
@bot.callback_query_handler(func=lambda call: call.data[:2] == 'id')
def callback_greet(call):
    global waiting_for_answer, chancellor

    user_id = call.message.chat.id
    chancellor = int(call.data[2:])
    print('idk')
    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    bot.send_message(call.message.chat.id, f'Вашим канцлерром будет назначен: {chancellor}')
    waiting_for_answer = 0


# нажата кнопка выбора карты канцлером
@bot.callback_query_handler(func=lambda call: call.data in ['fascist', "liberal"])
def callback_greet(call):
    global waiting_for_answer

    user_id = call.message.chat.id

    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    bot.send_message(call.message.chat.id, f'You chose: {call.data}')
    waiting_for_answer = call.data


# нажата кнопка выбора карты для исключения президентом
@bot.callback_query_handler(func=lambda call: len(call.data.split()) == 2)
def callback_greet(call):
    global waiting_for_answer, cards_to_choose_2
    user_id = call.message.chat.id

    # Удаляем предыдущее сообщение с кнопками
    if user_id in user_message_ids:
        bot.delete_message(user_id, user_message_ids[user_id])
        del user_message_ids[user_id]

    bot.send_message(call.message.chat.id, f'Я передал канцлеру данные карты: {list(call.data.split())}')
    waiting_for_answer = 0
    cards_to_choose_2 = call.data.split()


def first_raspred(dict_of_group):
    ochered = list(dict_of_group['id'].keys())
    random.shuffle(ochered)
    dict_of_group['och'] = ochered
    return dict_of_group


def main():
    bot.polling(none_stop=True)


def start_game(dict_of_group, president):
    global waiting_for_answer, cards_to_choose_2, chancellor, answer
    coloda = Cards()
    pole = CardsOnBoard()
    while True:
        answer = 0
        dict_of_group['rejection'] = 0
        # избрание президента и канцлера
        while answer == 0 and dict_of_group['rejection'] < 3:
            dict_of_group['rejection'] += 1
            # выбор президента
            president = dict_of_group['och'][0]
            dict_of_group['och'].append(dict_of_group['och'][0])
            dict_of_group['och'] = dict_of_group['och'][1:]

            # выбор канцлера президентом
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            kostl = []
            for i in dict_of_group['och']:
                kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i], callback_data='id' + str(i)))

            markup.add(*kostl)

            waiting_for_answer = 1
            sent_message = bot.send_message(president,
                                            f"okay, mister president, you can choose the chancellor",
                                            reply_markup=markup)

            # Сохраняем ID отправленного сообщения в памяти пользователя
            user_message_ids[president] = sent_message.message_id

            while waiting_for_answer == 1:
                pass

            waiting_for_answer = 1
            send_poll(dict_of_group['group_id'], f"President: {dict_of_group['names'][president]}, "
                                                 f"Chancellor: {dict_of_group['names'][chancellor]}")
            while waiting_for_answer == 1:
                pass

        # счетчик отказов на ноль
        dict_of_group['rejection'] = 0
        print('here')

        cards_to_choose = coloda.card_on_board()
        # отправляю президенту карты, которые ему выпали, добавить кнопки
        # Создаем клавиатуру
        print('here2')
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = telebot.types.InlineKeyboardButton(cards_to_choose[0],
                                                  callback_data=cards_to_choose[1] + ' ' + cards_to_choose[2])
        btn2 = telebot.types.InlineKeyboardButton(cards_to_choose[1],
                                                  callback_data=cards_to_choose[0] + ' ' + cards_to_choose[2])
        btn3 = telebot.types.InlineKeyboardButton(cards_to_choose[2],
                                                  callback_data=cards_to_choose[0] + ' ' + cards_to_choose[1])
        print('here')

        # Добавляем кнопки в клавиатуру
        markup.add(btn1, btn2, btn3)

        # Отправляем сообщение с клавиатурой
        waiting_for_answer = 1
        sent_message = bot.send_message(president,
                                        f"okay, mister president: you have cards: {cards_to_choose}"
                                        f", выберите карту, от которой хотите избавиться", reply_markup=markup)

        # Сохраняем ID отправленного сообщения в памяти пользователя
        user_message_ids[president] = sent_message.message_id

        # останавливаю работу программы до его ответа
        while waiting_for_answer:
            pass
        print('мы вышли из кабалы')

        # теперь к канцлеру

        # Создаем клавиатуру
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = telebot.types.InlineKeyboardButton(cards_to_choose_2[0],
                                                  callback_data=cards_to_choose_2[0])
        btn2 = telebot.types.InlineKeyboardButton(cards_to_choose_2[1],
                                                  callback_data=cards_to_choose_2[1])

        # Добавляем кнопки в клавиатуру
        markup.add(btn1, btn2)

        # Отправляем сообщение с клавиатурой
        waiting_for_answer = 1
        print('мы почти попали обратно')
        sent_message = bot.send_message(chancellor,
                                        f"okay, mister chancellor: you have cards: {cards_to_choose_2}"
                                        f", выберите одну", reply_markup=markup)

        # Сохраняем ID отправленного сообщения в памяти пользователя
        user_message_ids[chancellor] = sent_message.message_id

        # останавливаю работу программы до его ответа
        while waiting_for_answer == 1:
            pass

        dict_of_group['last_card'] = waiting_for_answer

        # поставить карту на поле
        pole.add(waiting_for_answer)

        onboard_liberal, onboard_fascist = pole.check()
        print(onboard_liberal, onboard_fascist)

        # выполнение особого протокола в зависимости от количества карт на столе
        if onboard_fascist > 3 and dict_of_group['id'][president] == 'gitler':
            win(dict_of_group, 'fascist')
            dict_of_group = {}

        elif onboard_fascist == 2:
            proverka_igroka(dict_of_group, president)

        elif onboard_fascist == 3:
            dict_of_group = vibor(dict_of_group, president)

        elif onboard_fascist == 4 or onboard_fascist == 5:
            died = liquidation(dict_of_group, president)
            print(died)
            if died == 'gitler':
                win(dict_of_group, 'liberal')
                dict_of_group = {}

        elif onboard_fascist == 6:
            win(dict_of_group, 'fascist')
            dict_of_group = {}

        elif onboard_liberal == 5:
            win(dict_of_group, 'liberal')
            dict_of_group = {}



def win(dict_of_group, who: str):
    bot.send_message(dict_of_group['group_id'], f"{who} won")


def proverka_igroka(dict_of_group, president):
    global check_player, waiting_for_answer
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    kostl = []
    for i in dict_of_group['och']:
        kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i], callback_data='di' + str(i)))

    markup.add(*kostl)
    waiting_for_answer = 1
    sent_message = bot.send_message(president,
                                    f"okay, mister president, you can check one player's role", reply_markup=markup)

    # Сохраняем ID отправленного сообщения в памяти пользователя
    user_message_ids[president] = sent_message.message_id

    while waiting_for_answer == 1:
        pass

    bot.send_message(president, f"Player {dict_of_group['names'][check_player]} is {dict_of_group['id'][check_player]}")


def vibor(dict_of_group, president):
    global check_player, waiting_for_answer
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    kostl = []
    for i in dict_of_group['och']:
        kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i], callback_data='di' + str(i)))

    markup.add(*kostl)
    waiting_for_answer = 1
    sent_message = bot.send_message(president,
                                    f"okay, mister president, you can choose next president", reply_markup=markup)

    # Сохраняем ID отправленного сообщения в памяти пользователя
    user_message_ids[president] = sent_message.message_id

    while waiting_for_answer == 1:
        pass

    bot.send_message(president, f"Player {dict_of_group['names'][check_player]} is new president")
    ind = dict_of_group['och'].index(check_player)
    dict_of_group['och'] = dict_of_group['och'][ind:] + dict_of_group['och'][:ind]
    return dict_of_group


def liquidation(dict_of_group, president):
    global kill_player, waiting_for_answer
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    kostl = []
    for i in dict_of_group['och']:
        kostl.append(telebot.types.InlineKeyboardButton(dict_of_group['names'][i], callback_data='ki' + str(i)))

    markup.add(*kostl)
    waiting_for_answer = 1
    sent_message = bot.send_message(president,
                                    f"okay, mister president, you can kill one player", reply_markup=markup)

    # Сохраняем ID отправленного сообщения в памяти пользователя
    user_message_ids[president] = sent_message.message_id

    while waiting_for_answer == 1:
        pass

    bot.send_message(president, f"Player {dict_of_group['names'][kill_player]} was killed")
    died = dict_of_group['id'][kill_player]

    # удаление убитого из всех списков
    del dict_of_group['names'][kill_player]
    del dict_of_group['id'][kill_player]
    dict_of_group['och'].remove(kill_player)
    print(dict_of_group)

    bot.send_message(kill_player, f"You was killed")

    return died


# Функция для отправки опроса
def send_poll(GROUP_ID, stroka):
    poll_message = bot.send_poll(
        chat_id=GROUP_ID,
        question=stroka + ", Вы согласны?",
        options=["Да", "Нет"],
        is_anonymous=False
    )

    # Запускаем таймер для сбора результатов через 30 секунд
    Timer(5.0, collect_poll_results, [poll_message.chat.id, poll_message.message_id]).start()


# Функция для получения результатов опроса
def collect_poll_results(chat_id, message_id):
    global answer, waiting_for_answer
    poll_results = bot.stop_poll(chat_id, message_id)

    # Подготовка и отправка результатов
    if poll_results.options[0].voter_count > poll_results.options[1].voter_count:
        results_text = f'President and chancellor chosen'
        answer = 1
    else:
        results_text = f'('
        answer = 0

    bot.send_message(chat_id, results_text)
    waiting_for_answer = 0


class role_for_everyone:
    def __init__(self, sps: list):
        self.count_of_players = len(sps)
        self.players = list(sps)
        print(sps)
        self.players_roles = {}
        self.roles = []

    def roles_from_count(self):
        if self.count_of_players == 5:
            self.roles = ['liberal', 'liberal', 'liberal', 'fascist', 'hitler']
        elif self.count_of_players == 6:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'hitler']
        elif self.count_of_players == 7:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'fascist', 'hitler']
        elif self.count_of_players == 8:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'fascist', 'hitler']
        elif self.count_of_players == 9:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'fascist', 'fascist',
                          'fascist', 'hitler']
        elif self.count_of_players == 10:
            self.roles = ['liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'liberal', 'fascist',
                          'fascist', 'fascist', 'hitler']
        # test
        elif self.count_of_players == 2:
            self.roles = ['fascist', 'liberal']
        elif self.count_of_players == 1:
            self.roles = ['liberal']
        return self.roles

    def role_for_all(self):
        self.roles = self.roles_from_count()
        random.shuffle(self.roles)
        for i in range(self.count_of_players):
            self.players_roles[self.players[i]] = self.roles[i]
        print(self.players_roles)
        return self.players_roles


# Класс карточек законов
class Cards:
    def __init__(self):
        self.cards_in = ["fascist"] * 11 + ["liberal"] * 6  # карты в колоде
        self.cards_out = []  # сюда надо складывать карты, которые откинули игроки

    # выкладка закона на стол
    def card_on_board(self):
        if len(self.cards_in) < 3:
            print(self.cards_out, self.cards_in)
            self.cards_in = self.cards_out + self.cards_in
            self.cards_out = []
            print(self.cards_out, self.cards_in)
        card = [random.choice(self.cards_in)]  # Рандомно выбираем первую карту
        self.cards_out.append(card[0])
        self.cards_in.remove(card[0])  # Удаляем 1 карту из списка карт в колоде
        card = card + [random.choice(self.cards_in)]  # Рандомно выбираем 2 карту закидываем обе карты в общий список
        self.cards_out.append(card[1])
        self.cards_in.remove(card[1])  # Удаляем 2 карту из списка
        card = card + [random.choice(self.cards_in)]  # Рандомно выбираем 3 карту закидываем три карты в общий список
        self.cards_out.append(card[2])
        self.cards_in.remove(card[2])  # Удаляем 3 карту из списка
        return card


class CardsOnBoard:
    # два списка: либеральные карты на столе, фашистские карты на столе
    def __init__(self):
        self.onboard_liberal = 0
        self.onboard_fascist = 0

    def add(self, card):
        if card == 'fascist':
            self.onboard_fascist += 1
        else:
            self.onboard_liberal += 1

    def check(self):
        return self.onboard_liberal, self.onboard_fascist


if __name__ == "__main__":
    main()
