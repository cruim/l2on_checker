import requests
from bs4 import BeautifulSoup
import api
from config import API_TOKEN


def cron_scheduller():
    tasks = api.Scheduller.query.filter_by(is_active=True).all()
    for task in tasks:
        request_response_processing(task=task)
        api.close_dispose_connection()


def request_response_processing(task):
    staff = api.get_staff(task.staff_id)
    url = api.build_l2on_url(id=staff.l2on_id, task=task)
    req = requests.get(url=url[0], headers=url[1])
    soup = BeautifulSoup(req.text)
    for tr in soup.find_all('tr'):
        date = tr.find_all('span')
        date = date[1] if date and len(date) > 1 else False
        if date and date.text and "минут" in date.text:
            price = tr.find('td', {"class": "right"}).text.replace(" ", "")
            if int(price) <= task.price:
                user = api.get_user(task.user_id)
                api.update_scheduller_is_active(task)
                send_message(chat_id=user.telegram_id, text=' '.join([staff.name, date.text, price]))
    return False


def send_message(chat_id, text):
    requests.get(url="https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}".format(API_TOKEN, chat_id, text))