import datetime
import random
import time
from threading import Thread

import configuration
import requests
import vk_api
from vk_api.utils import get_random_id

# ========boring background==================
token = configuration.token
print(token)
threads = []
vk_session = vk_api.VkApi(token=token)


# ===========================================


def compliment():
    req = requests.post('http://freegenerator.ru/compliment',
                        data={'type': 'compliment', 'sex': 0, 'long_val': 1}).json()
    return req['text']



def sending(user):
    '''
    Sends a message to user after waiting(sleeping)
    :param user: string. Key of dictionary configuration.users_id
    :return: None
    '''
    print("[{}] Starting".format(user))
    seconds = random.randint(1, configuration.upper_seconds_bound + 1)
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=seconds)
    print("[{}] Your compliment will be sent at {}, in {} seconds".format(user, now + delta, seconds))
    time.sleep(seconds)

    vk = vk_session.get_api()
    # listening(vk)

    vk.messages.send(
        user_id=configuration.users_id[user],
        attachment=None,  # todo: you can attach pictures
        random_id=get_random_id(),
        message=compliment()
    )
    print('[{}] ok'.format(user))


def main():
    while True:
        threads = [Thread(target=sending, args=(i,)) for i in configuration.users_id.keys()]
        for i in range(len(configuration.users_id)):
            threads[i].start()
        for i in range(len(configuration.users_id)):
            threads[i].join()


if __name__ == '__main__':
    main()
