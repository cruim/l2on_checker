from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import requests
from bs4 import BeautifulSoup
import api
from config import API_TOKEN, SCHEDULLER_PORT


def update_scheduller_is_active():
    api.update_scheduller_is_active()
    return api.close_dispose_connection()


def cron_scheduller():
    tasks = api.Scheduller.query.filter_by(is_active=True).all()
    for task in tasks:
        request_response_processing(task=task)
    return api.close_dispose_connection()


def request_response_processing(task):
    staff = api.get_staff(task.staff_id)
    url = api.build_l2on_url(id=staff.l2on_id, task=task)
    req = requests.get(url=url[0], headers=url[1])
    soup = BeautifulSoup(req.text)
    for tr in soup.find_all('tr'):
        try:
            date = tr.find_all('span')
            if len(date) and 'bs4' in str(type(date[0])) and ('минут' in date[0].text or 'минут' in date[1].text):
                price = tr.find_all('td', {"class": "right"})[0].text.replace(' ', '')
                if int(price) <= task.price:
                    user = api.get_user(task.user_id)
                    send_message(chat_id=user.telegram_id, text=' '.join([staff.name, format(int(price), ',').replace(',', ' ')]))
                    api.update_scheduller_is_active(task)
                    break
        except:
            continue
    return api.close_dispose_connection()


def send_message(chat_id, text):
    requests.get(url="https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}".format(API_TOKEN, chat_id, text))


app = Flask(__name__)


if __name__ == "__main__":
    app.run(port=SCHEDULLER_PORT, debug=True)