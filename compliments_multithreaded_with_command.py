import datetime
import random
import time

import requests
import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from concurrent.futures import ThreadPoolExecutor, as_completed

import bot_compliments.configuration as configuration
from bot_compliments.token_bot import token


def authorize():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    return vk_session, vk


def get_compliment(sex=0):
    """
    sex 0 - male
    sex 1 - female
    """
    sex = abs(sex - 1)
    req = requests.post('http://freegenerator.ru/compliment',
                        data={'type': 'compliment', 'sex': sex, 'long_val': 1}).json()
    return req['text']


def set_sleep_time(nickname: str) -> None:
    seconds = random.randint(1, configuration.upper_seconds_bound + 1)
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=seconds)
    print(f"[{nickname}] Your compliment will be sent in {seconds} seconds, at {now + delta}")
    time.sleep(seconds)


def sending(vk: vk_api.vk_api.VkApiMethod, member_id: int, sleep: bool = True) -> None:
    """
    Sends a message to user

    sleep == True:
        after waiting(sleeping)
    sleep == False:
        right now
    """
    nickname = vk.users.get(user_ids=[member_id])[0]['first_name'] + ' ' + \
               vk.users.get(user_ids=[member_id])[0]['last_name']

    if sleep:
        set_sleep_time(nickname)

    try:
        vk.messages.send(
            user_id=member_id,
            random_id=get_random_id(),
            message=get_compliment(sex=vk.users.get(user_id=member_id, fields="sex")[0]['sex'])
        )
        print(f"[{nickname}] ok.")
    except vk_api.exceptions.ApiError:
        print(f"[{nickname}] I have no access to that user.")


def listening(_, vk, vk_session):
    longpoll = VkLongPoll(vk_session)
    print("I'm listening")

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    user_info = vk.users.get(user_ids=event.user_id)[0]
                    message_content: str = event.message
                    print(f"\n[{user_info['first_name']} {user_info['last_name']}] I've got a message: "
                          f"\"{message_content}\"")
                    if message_content in ("!комплимент", "!Комплимент", "!compliment", "!Compliment"):
                        sending(vk, user_info["id"], sleep=False)
                        print('\n')
        except Exception as ex:
            print("[!]Exception ", repr(ex))
            continue


def start_threads():
    vk_session, vk = authorize()
    while True:
        members_id = vk.groups.getMembers(group_id=configuration.group_id)["items"]
        with ThreadPoolExecutor() as pool:
            results = [pool.submit(sending, vk, i) for i in members_id] + \
                      [pool.submit(listening, None, vk, vk_session)]

            for future in as_completed(results):
                future.result()


if __name__ == '__main__':
    start_threads()
