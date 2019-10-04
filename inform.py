# -*- coding: utf-8 -*-
import requests
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from linebot import LineBotApi, WebhookHandler
import pandas as pd
import datetime
import numpy as np
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent, PostbackEvent

import settings
from models import *

db_engine = create_engine(settings.db_info, pool_pre_ping=True)
line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)
size_list = ['小盛', '並盛', '大盛']
exemption_price = 50

Session = sessionmaker(bind=db_engine)
s = Session()

now = datetime.datetime.now()
date = now + datetime.timedelta(days=1)
date = date.strftime('%Y%m%d')

query = 'select * from users where option != -1'
user_df = pd.read_sql(query, db_engine)
users = user_df['id'].tolist()

headers = {'accept': 'application/json'}
url = f'https://platform.coi.kyushu-u.ac.jp/lineapp/api/menu/{date}'

res = requests.get(url, headers=headers)
menu = res.json()

if len(menu) > 0:
    message = '明日のメニューは\n'
    menunames = []
    for row in menu:
        menunames.append(row['name'])
    message += ','.join(menunames)
    message += '\nです。\n\nご注文はこちらから\nhttp://nav.cx/4VQZMbx'

    for id in users:
        line_bot_api.push_message(id, TextSendMessage(text=message))
