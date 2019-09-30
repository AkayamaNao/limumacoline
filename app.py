# -*- coding: utf-8 -*-
from flask import request, abort, Blueprint, Flask
from sqlalchemy import create_engine, func
import pandas as pd
from logging import DEBUG, INFO, Formatter
from logging.config import dictConfig
from sqlalchemy.orm import sessionmaker
import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent, PostbackEvent

import settings
from models import *

dictConfig({
    'version': 1,  # ?
    'formatters': {
        'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'},
        'myformatter': {'format': '%(asctime)s %(levelname)8s %(filename)s:L%(lineno)d: %(message)s'},
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            # 'formatter': 'default'
            'formatter': 'myformatter'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'myformatter',
            'maxBytes': 1024 * 1024,
            'backupCount': 10,
        },
    },
    'root': {
        'level': 'DEBUG',
        # 'handlers': ['wsgi', 'file'],
        'handlers': ['file'],
    },
})

app = Flask(__name__)
app.logger.setLevel(DEBUG)

app.secret_key = 'fjeioav;djb;'
app.config['JSON_AS_ASCII'] = settings.JSON_AS_ASCII
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.SWAGGER_UI_DOC_EXPANSION
app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
app.config['UPLOADED_CONTENT_DIR'] = settings.UPLOADED_CONTENT_DIR

with app.app_context():
    db.init_app(app)
    # db.drop_all()  # Remove on release
    db.create_all()

db_engine = create_engine(settings.db_info, pool_pre_ping=True)
line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)
size_list = ['小盛', '並盛', '大盛']

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + settings.access_token
}
reply_url = 'https://api.line.me/v2/bot/message/reply'

def dateseparate(date):  # date=20190911
    yobi = ["月", "火", "水", "木", "金", "土", "日"]
    date = datetime.datetime.strptime(str(date), '%Y%m%d')
    year = int(date.strftime('%Y'))
    month = int(date.strftime('%m'))
    day = int(date.strftime('%d'))
    week = date.weekday()
    return {'year': year, 'month': month, 'day': day, 'week': yobi[week]}


def date2str(date):
    ds = dateseparate(date)
    return f'{ds["month"]:2d}月{ds["day"]:2d}日({ds["week"]}) '



# for run check
@app.route('/')
def index():
    return 'Hello World!'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # current_app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    Session = sessionmaker(bind=db_engine)
    s = Session()
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    user = s.query(Users).filter_by(id=user_id).first()
    if user:
        user.option = 0
    else:
        user = Users(id=user_id, name=profile.display_name, option=0)
        s.add(user)
    s.commit()
    # print(profile.user_id, profile.display_name, profile.picture_url, profile.status_message)
    # app.logger.info(f'User add {profile.user_id}.')

    message = f'使い方はノートをご覧ください'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))


@handler.add(UnfollowEvent)
def handle_follow(event):
    Session = sessionmaker(bind=db_engine)
    s = Session()
    user_id = event.source.user_id
    user = s.query(Users).filter_by(id=user_id).first()
    if user:
        user.option = -1
    s.commit()
    # app.logger.info(f'User delete {event.source.user_id}.')


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    Session = sessionmaker(bind=db_engine)
    s = Session()
    user_id = event.source.user_id
    text = event.message.text
    # current_app.logger.info(f'user_id:{user_id} text:{text}')
    if text == 'aaa':
        message = text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))


@handler.add(PostbackEvent)
def postback(event):
    Session = sessionmaker(bind=db_engine)
    s = Session()

    data = event.postback.data
    user_id = event.source.user_id

    if data == 'rich_on':
        user = s.query(Users).filter_by(id=user_id).first()
        user.option = 1
        s.commit()
        message = '配達免除になりました'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    elif data == 'rich_off':
        user = s.query(Users).filter_by(id=user_id).first()
        user.option = 0
        s.commit()
        message = '配達免除を解除しました'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    elif data == 'rich_list':
        query = f'select date, menu, price from orders where user_id=\'{user_id}\' and collected=0'
        df = pd.read_sql(query, db_engine)
        if len(df)>0:
            message = ''
            for i, row in df.iterrows():
                message += f'{date2str(row["date"])}  {row["menu"]} {row["price"]}円\n'
            message += f'\n合計  {df["price"].sum()}円'
        else:
            message='現在表示できる注文履歴はありません'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=settings.DEBUG)
