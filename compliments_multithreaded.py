import datetime
import random
import time
from threading import Thread

import requests
import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType

import compliments.configuration as configuration
from compliments.token_bot import token


def authorize():
    vk_session = vk_api.VkApi(token=token)
    return vk_session, vk_session.get_api()


def compliment(sex=0):
    sex = abs(sex - 1)
    req = requests.post('http://freegenerator.ru/compliment',
                        data={'type': 'compliment', 'sex': sex, 'long_val': 1}).json()
    return req['text']


def set_sleep_time(vk, member_id, nickname):
    seconds = random.randint(1, configuration.upper_seconds_bound + 1)
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=seconds)
    print(f"[{nickname}] Your compliment will be sent in {seconds} seconds, at {now + delta}")
    time.sleep(seconds)


def sending(vk, member_id):
    """
    Sends a message to user after waiting(sleeping)
    :param vk: vk_api.vk_api.VkApiMethod
    :param member_id: int
    :return: None
    """
    nickname = vk.users.get(user_ids=[member_id])[0]['first_name'] + ' ' + \
               vk.users.get(user_ids=[member_id])[0]['last_name']

    set_sleep_time(vk, member_id, nickname)

    try:
        vk.messages.send(
            user_id=member_id,
            random_id=get_random_id(),
            message=compliment(sex=vk.users.get(user_id=member_id, fields="sex")[0]['sex'])
        )
        print(f"[{nickname}] ok.")
    except vk_api.exceptions.ApiError:
        print(f"[{nickname}] I have no access to that user.")


def listening(none, vk_session):
    longpoll = VkLongPoll(vk_session)
    print("Im listening")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            print(f"I've got a message from {event.from_user}")


def start_threads():
    vk_session, vk = authorize()
    while True:
        members_id = vk.groups.getMembers(group_id=configuration.group_id)["items"]
        threads = [Thread(target=sending, args=(vk, i)) for i in members_id]
        threads.append(Thread(target=listening, args=(None, vk_session)))
        for i in range(len(threads)):
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()


if __name__ == '__main__':
    start_threads()
