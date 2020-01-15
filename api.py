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

def get_last_user_log_state(telegram_id):
    user_id = get_user_id(telegram_id=telegram_id)
    return UserLog.query.filter_by(user_id=user_id).order_by(UserLog.id.desc()).first().state

def create_staff_scheduller_task(user_id, staff_id, price):
    task = Scheduller(user_id=user_id, staff_id=staff_id, price=price)
    db.session.add(task)
    db.session.commit()

def get_staff_scheduller_list(user_id):
    staff_list = db.session.query(Scheduller.staff_id, Staff.name).join(Staff, Staff.id == Scheduller.staff_id).\
        filter_by(Scheduller.user_id == user_id).all()
    return staff_list

def get_items_matching_user_search(name):
    return db.session.query(Staff.name, Staff.l2on_id).filter(Staff.name.ilike('%{}%'.format(name))).all()

def create_error_log(error_location, error_message, user_id):
    error = ErrorLog(error_location=error_location, error_message=error_message, user_id=user_id)
    db.session.add(error)
    db.session.commit()

def send_message_to_user(user_id, text):
    pass

# Поиск предмета
def generate_search_query_keyboard(user_id, text):
    pass

def generate_main_keyboard():
    return {'item_list': 'Список отслеживаемых предметоф', 'search_item': 'Поиск предмета', 'telegram_id': 'Telegram ID'}

def user_message_processing(telegram_id, message):
    last_user_log_state = get_last_user_log_state(telegram_id)
    if message in ('main_menu', 'start', '/start'):
        add_user_log(telegram_id=telegram_id, state='main_menu')
        return generate_main_keyboard()
    elif message == 'item_list':
        add_user_log(telegram_id=telegram_id, state='item_list')
        return get_staff_scheduller_list(telegram_id)
    elif message == 'search_item':
        add_user_log(telegram_id=telegram_id, state='search_item')


# ('item_lis', 'search_item', 'pick_item', 'set_price', 'delete_item',"
#                         "'telegram_id', 'pick_price', 'main_menu')"