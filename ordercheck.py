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
users = '&'.join(users)

headers = {'accept': 'application/json'}
url = f'https://platform.coi.kyushu-u.ac.jp/lineapp/api/order/{date}/{users}'

res = requests.get(url, headers=headers)
orders = res.json()

if len(orders) == 0:
    exit()

for order in orders:
    user = s.query(Users).filter_by(id=order['user_id']).first()
    user.name = order['user_name']
    s.add(Orders(date=order['date'], user_id=order['user_id'], type='order',
                 menu=f'{order["meal_name"]} {size_list[order["size"]]}', price=order['price']))

orders = pd.DataFrame.from_dict(orders)
user_df = user_df[user_df['option'] == 0]
users = user_df['id'].tolist()
flag = orders['user_id'].isin(users)
member = orders[flag]
non_member = orders[[not i for i in flag]]
if len(member) == 0:
    member = orders

# decide delivery
query = 'select user_id, sum(price) as price from orders where collected = 0 group by user_id'
total_df = pd.read_sql(query, db_engine)
total_df['price'] -= total_df['price'].min()
p = []
for i, row in member.iterrows():
    p.append(int(total_df[total_df['user_id'] == row['user_id']]['price']))
np.random.seed(int(now.timestamp()))
deli = np.random.choice(member.to_dict(orient='records'), p=np.array(p) / sum(p))

total = orders['price'].sum()
s.add(Orders(date=deli['date'], user_id=deli['user_id'], type='delivery', menu='配達', price=int(-1 * total)))
s.add(Orders(date=deli['date'], user_id=deli['user_id'], type='bonus', menu='ボーナス',
             price=int(-1 * exemption_price * len(non_member))))
for i, row in non_member.iterrows():
    s.add(Orders(date=row['date'], user_id=row['user_id'], type='exemption', menu='配達免除', price=int(exemption_price)))
s.commit()

message = f'明日の配達は{deli["user_name"]}です'
tmp = ''
meal_grouped = orders.groupby('meal_name', sort=False)
for meal_name, meal_group in meal_grouped:
    message += f'\n\n{meal_name}'
    tmp += f'\n\n{meal_name}'
    meal_group = meal_group.sort_values('size')
    size_grouped = meal_group.groupby('size', sort=False)
    for size, size_group in size_grouped:
        size_group = size_group.sort_values('timestamp')
        membertext = '\n      '.join(size_group["user_name"].tolist())
        message += f'\n{size_list[size]}  {membertext}'
        tmp += f'\n{size_list[size]} {len(size_group)}個'
message += '\n\nーーーーーーーーーーーーーー'
message += tmp
message += f'\n\n合計  {total}円'

for i, row in orders.iterrows():
    line_bot_api.push_message(row['user_id'], TextSendMessage(text=message))
