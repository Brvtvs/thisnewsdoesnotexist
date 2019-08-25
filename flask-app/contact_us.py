import datetime
import json
import os

import requests

from config import telegram_bot_token, telegram_bot_chatid

storage_file = "contact_us_forms.json"


def on_submission(form):
    print("Got contact-us form submission: %s" % json.dumps(form))

    try:
        file = storage_file
        if os.path.exists(file):
            with open(file, 'rt') as json_file:
                json_data = json.load(json_file)
        else:
            json_data = {}

        if 'forms' not in json_data:
            json_data['forms'] = []

        json_data['forms'].append({'when': datetime.datetime.now(), 'form': form})

        with open(file, 'wt') as json_file:
            json.dump(json_data, json_file, sort_keys=True, default=str)

    except Exception as e:
        print("Failed to write contact-us form submission to json.")
        print(e)

    # telegram functionality based on this guide: https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e
    telegram_msg = '*New contact-us form submitted.*\n\n'
    for k, v in form.items():
        telegram_msg += "*" + k + ":* " + v + "\n\n"
    telegram_msg = telegram_msg.replace("_", "-")

    send_text = 'https://api.telegram.org/bot' + telegram_bot_token + '/sendMessage?chat_id=' + telegram_bot_chatid + '&parse_mode=Markdown&text=' + telegram_msg
    response = requests.get(send_text)
    if response.status_code != 200:
        print("Failed to send the contact-us form submission as a telegram message. Got this response:")
        print(response)
