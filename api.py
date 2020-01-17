from app import db, Scheduller, UserLog, Staff, ErrorLog, User, GameServer


def update_scheduller_is_active(scheduller_id):
    result = Scheduller.query.filter_by(id=scheduller_id).first()
    result.is_active = not result.is_active
    db.session.add(result)
    db.session.commit()
    db.session.close()

def check_access(telegram_id):
    return True if User.query.filter_by(telegram_id=telegram_id).first() else False

def check_schduller_limit(telegram_id):
    user_id = get_user_id(telegram_id=telegram_id)
    current_count = db.session.query(Scheduller.id).filter_by(user_id=user_id).count()
    return True if current_count < 15 else False

def get_staff_name_by_id(id):
    return Staff.query.filter_by(id=id).first().name

def check_message_in_scheduller_list(message, telegram_id):
    user_id = get_user_id(telegram_id=telegram_id)
    return Scheduller.query.filter_by(staff_id=message, user_id=user_id).first()

def get_staff_id_based_on_l2on_id(l2on_id):
    return Staff.query.filter_by(l2on_id=l2on_id).first().id

def delele_scheduller_task(staff_id, telegram_id):
    user_id = get_user_id(telegram_id=telegram_id)
    Scheduller.query.filter_by(staff_id=staff_id, user_id=user_id).delete()
    db.session.commit()
    db.session.close()

def get_user_id(telegram_id):
    return User.query.filter_by(telegram_id=telegram_id).first().id

def add_user_log(telegram_id, state):
    user_id = get_user_id(telegram_id=telegram_id)
    user_log = UserLog(user_id=user_id, state=state)
    db.session.add(user_log)
    db.session.commit()
    db.session.close()

def get_last_user_log(telegram_id, state=False):
    user_id = get_user_id(telegram_id=telegram_id)
    if state:
        log = UserLog.query.filter_by(user_id=user_id, state=state).order_by(UserLog.id.desc()).first()
    else:
        log = UserLog.query.filter_by(user_id=user_id).order_by(UserLog.id.desc()).first()
    return log

def update_user_log_user_message(user_log ,message):
    user_log.user_message = message
    db.session.commit()
    db.session.close()

def create_staff_scheduller_task(user_id, staff_id, price, game_server_id):
    task = Scheduller(user_id=user_id, staff_id=staff_id, price=price, game_server_id=game_server_id)
    db.session.add(task)
    db.session.commit()
    db.session.close()

def get_staff_scheduller_list(telegram_id):
    user_id = get_user_id(telegram_id)
    staff_list = tuple(db.session.query(Scheduller.staff_id, db.func.concat(Staff.name, ' ', Scheduller.price)).
                       join(Staff, Staff.id == Scheduller.staff_id).filter(Scheduller.user_id == user_id).all())
    staff_list = dict((x, y) for x, y in staff_list)
    staff_list['/start'] = 'Главное меню'
    return staff_list

def get_items_matching_user_search(name):
    result = tuple(db.session.query(Staff.name, Staff.l2on_id).filter(Staff.name.ilike('%{}%'.format(name))).limit(30).all())
    result = dict((y, x) for x, y in result)
    result['/start'] = 'Главное меню'
    return result

def get_game_server_keyboard():
    result = db.session.query(GameServer.name, GameServer.l2on_id).all()
    result = dict((y, x) for x, y in result)
    result['/start'] = 'Главное меню'
    return result

def create_error_log(error_location, error_message, user_id):
    error = ErrorLog(error_location=error_location, error_message=error_message, user_id=user_id)
    db.session.add(error)
    db.session.commit()
    db.session.close()

def generate_main_keyboard():
    return {'item_list': 'Список отслеживаемых предметов', 'search_item': 'Поиск предмета', 'telegram_id': 'Telegram ID'}

def generate_staff_item_keyboard():
    return {'delete_item': 'Удалить', '/start': 'Главное меню'}

# TODO: Refactor this
def user_message_processing(telegram_id, message):
    last_user_log = get_last_user_log(telegram_id)
    if message in ('main_menu', 'start', '/start'):
        add_user_log(telegram_id=telegram_id, state='main_menu')
        return generate_main_keyboard(), 'Главное меню.'
    elif message == 'item_list':
        add_user_log(telegram_id=telegram_id, state='item_list')
        return get_staff_scheduller_list(telegram_id), 'Список предметов.'
    elif message == 'search_item':
        add_user_log(telegram_id=telegram_id, state='search_item')
        return 'Введите название предмета.'
    elif message == 'telegram_id':
        add_user_log(telegram_id=telegram_id, state='telegram_id')
        return 'Ваш telegram_id ' + str(telegram_id)
    else:
        if last_user_log.state == 'search_item' and last_user_log.user_message:
            add_user_log(telegram_id=telegram_id, state='pick_item')
            update_user_log_user_message(user_log=get_last_user_log(telegram_id), message=message)
            return 'Введите цену.'
        elif last_user_log.state == 'search_item':
            if check_schduller_limit(telegram_id=telegram_id):
                update_user_log_user_message(user_log=last_user_log, message=message)
                return get_items_matching_user_search(message), 'Результат поиска.'
            else:
                return 'Превышен лимит отслеживаемых предметов.'
        elif last_user_log.state == 'pick_item' and last_user_log.user_message and str(message).isdigit():
            staff_id = get_staff_id_based_on_l2on_id(l2on_id=last_user_log.user_message)
            create_staff_scheduller_task(user_id=get_user_id(telegram_id=telegram_id), staff_id=staff_id, price=message, game_server_id=message)
            return 'Предмет добавлен список.'
        elif last_user_log.state == 'pick_item':
            if last_user_log.user_message and str(message).isdigit():
                add_user_log(telegram_id=telegram_id, state='set_price')
                update_user_log_user_message(user_log=get_last_user_log(telegram_id), message=message)
                return get_game_server_keyboard(), 'Выберите сервер.'
            else:
                return 'Введите целое число.'
        elif last_user_log.state == 'item_list' and str(message).isdigit() and check_message_in_scheduller_list(message=message, telegram_id=telegram_id):
            update_user_log_user_message(user_log=get_last_user_log(telegram_id), message=message)
            return generate_staff_item_keyboard(), get_staff_name_by_id(message)
        elif last_user_log.state == 'item_list' and get_last_user_log(telegram_id=telegram_id).user_message and message == 'delete_item':
            delele_scheduller_task(staff_id=get_last_user_log(telegram_id=telegram_id).user_message, telegram_id=telegram_id)
            add_user_log(telegram_id=telegram_id, state='delete_item')
            return 'Предмет был удален из списка отслеживаемых.'
        else:
            return False