from app import db, Scheduller, UserLog, Staff


def delele_scheduller_task(id):
    return Scheduller.query.filter_by(id=id).delete()

def add_user_log(user_id, state):
    user_log = UserLog(user_id=user_id, state=state)
    db.session.add(user_log)
    db.session.commit()

def get_last_user_log_state(user_id):
    return UserLog.query.filter_by(user_id=user_id).order_by(id.desc()).first

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

def send_message_to_user(user_id, text):
    pass

def generate_search_query_keyboard(user_id, text):
    pass

def generate_main_keyboard(user_id):
    pass

def user_message_processing(user_id, message):
    last_user_log_state = get_last_user_log_state(user_id)
    if message in ('main_menu', 'start', '/start'):
        return generate_main_keyboard(user_id)
    elif message == 'item_list':
        add_user_log(user_id=user_id, state='item_list')
        return get_staff_scheduller_list(user_id)
    elif message == 'search_item':
        add_user_log(user_id=user_id, state='search_item')


# ('item_lis', 'search_item', 'pick_item', 'set_price', 'delete_item',"
#                         "'telegram_id', 'pick_price', 'main_menu')"