# -*- coding: utf-8 -*-
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, PostbackAction
import requests

import settings

line_bot_api = LineBotApi(settings.access_token)

# #check rich menu
# richmenus=line_bot_api.get_rich_menu_list()
# print(richmenus)

# #set default rich menu
# url=f'https://api.line.me/v2/bot/user/all/richmenu/{non_id}'
# headers = {
#     'Authorization': 'Bearer ' + settings.access_token
# }
# res=requests.post(url, headers=headers)
# print(res)


# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=False,
    name="normalrichmenu",
    chat_bar_text="メニューを開く・閉じる",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=834, height=843),
        action=PostbackAction(data="rich_on",text='配達免除')),

        RichMenuArea(
            bounds=RichMenuBounds(x=834, y=0, width=834, height=843),
            action=PostbackAction(data="rich_off",text='配達免除解除')),
        RichMenuArea(
            bounds=RichMenuBounds(x=1667, y=0, width=834, height=843),
            action=PostbackAction(data="rich_list",text='注文履歴'))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('richmenu.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'richmenu_id = "{rich_menu_id}"')

url = f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}'
headers = {
    'Authorization': 'Bearer ' + settings.access_token
}
requests.post(url, headers=headers)
