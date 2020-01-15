from app import db, Scheduller, UserLog, Staff, ErrorLog, User


def delele_scheduller_task(id):
    return Scheduller.query.filter_by(id=id).delete()

def get_user_id(telegram_id):
    return User.query.filter_by(telegram_id=telegram_id).first().id

def add_user_log(telegram_id, state):
    user_id = get_user_id(telegram_id=telegram_id)
    user_log = UserLog(user_id=user_id, state=state)
    db.session.add(user_log)
    db.session.commit()
    db.session.close()

def get_last_user_log(telegram_id):
    user_id = get_user_id(telegram_id=telegram_id)
    log = UserLog.query.filter_by(user_id=user_id).order_by(UserLog.id.desc()).first()
    return log

def update_user_log_user_message(user_log ,message):
    user_log.user_message = message
    db.session.commit()
    db.session.close()

def create_staff_scheduller_task(user_id, staff_id, price):
    task = Scheduller(user_id=user_id, staff_id=staff_id, price=price)
    db.session.add(task)
    db.session.commit()
    db.session.close()

def get_staff_scheduller_list(user_id):
    staff_list = db.session.query(Scheduller.staff_id, Staff.name).join(Staff, Staff.id == Scheduller.staff_id).\
        filter_by(Scheduller.user_id == user_id).all()
    return staff_list

def get_items_matching_user_search(name):
    result = tuple(db.session.query(Staff.name, Staff.l2on_id).filter(Staff.name.ilike('%{}%'.format(name))).limit(30).all())
    db.session.close()
    result = dict((y, x) for x, y in result)
    return result

def create_error_log(error_location, error_message, user_id):
    error = ErrorLog(error_location=error_location, error_message=error_message, user_id=user_id)
    db.session.add(error)
    db.session.commit()
    db.session.close()

def send_message_to_user(user_id, text):
    pass

# Поиск предмета
def generate_search_query_keyboard(user_id, text):
    pass

def generate_main_keyboard():
    return {'item_list': 'Список отслеживаемых предметоф', 'search_item': 'Поиск предмета', 'telegram_id': 'Telegram ID'}

def user_message_processing(telegram_id, message):
    last_user_log = get_last_user_log(telegram_id)
    if message in ('main_menu', 'start', '/start'):
        add_user_log(telegram_id=telegram_id, state='main_menu')
        return generate_main_keyboard()
    elif message == 'item_list':
        add_user_log(telegram_id=telegram_id, state='item_list')
        return get_staff_scheduller_list(telegram_id)
    elif message == 'search_item':
        add_user_log(telegram_id=telegram_id, state='search_item')
        return 'Введите название предмета.'
    elif message == 'telegram_id':
        add_user_log(telegram_id=telegram_id, state='telegram_id')
        return 'Ваш telegram_id ' + str(telegram_id)
    else:
        if last_user_log.state == 'search_item' and last_user_log.message:
            add_user_log(telegram_id=telegram_id, state='pick_item')
            update_user_log_user_message(user_log=get_last_user_log(telegram_id), message=message)
            return 'Введите цену.'
        elif last_user_log.state == 'search_item':
            update_user_log_user_message(user_log=last_user_log, message=message)
            return get_items_matching_user_search(message)
        else:
            return False