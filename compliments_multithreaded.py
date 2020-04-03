import datetime
import random
import time
from threading import Thread

import requests
import vk_api
from vk_api.utils import get_random_id

import tell_me_sth_good.configuration as configuration
from tell_me_sth_good.token_bot import token, group_id


def authorize():
    vk_session = vk_api.VkApi(token=token)
    return vk_session.get_api()


def compliment(sex=0):
    sex = abs(sex - 1)
    req = requests.post('http://freegenerator.ru/compliment',
                        data={'type': 'compliment', 'sex': sex, 'long_val': 1}).json()
    return req['text']


def set_sleep_time(vk, member_id, nickname):
    print(f"[{nickname}] Starting")

    seconds = random.randint(1, configuration.upper_seconds_bound + 1)
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=seconds)
    print(f"[{nickname}] \
    Your compliment will be sent in {seconds} seconds, at {now + delta}")
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
    vk.messages.send(
        user_id=member_id,
        random_id=get_random_id(),
        message=compliment(sex=vk.users.get(user_id=member_id, fields="sex")[0]['sex'])
    )
    print(f"[{nickname}] ok.")


def start_threads():
    vk = authorize()
    members_id = vk.groups.getMembers(group_id=group_id)["items"]
    while True:
        threads = [Thread(target=sending, args=(vk, i)) for i in members_id]
        for i in range(len(members_id)):
            threads[i].start()
        for i in range(len(members_id)):
            threads[i].join()


def main():
    start_threads()


if __name__ == '__main__':
    main()
