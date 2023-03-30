import telebot
import time
import requests
from bs4 import BeautifulSoup

token = ""  # Insert the token from the Telegram Bot
id_channel = "@" # Insert the number of the group where you want to repost after @.
bot = telebot.TeleBot(token)
URL = "https://vk.com/wall-%number%?own=1" # Insert the number of the VK group from where you want to repost instead of %number%

@bot.message_handler(content_types=["text"])
def command(message):
    if message.text == "Старт":
        back_post_id = 0
        while True:
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            post_text = parser(soup,back_post_id)
            back_post_id = post_text[1]

            if post_text[0] != None:
                bot.send_message(id_channel, post_text[0])
                time.sleep(3600)
            else:
                time.sleep(3600)
    else:
        bot.send_message(message.from_user.id,
                         "Я тебя не понимаю. Напиши Старт")


def parser(soup,back_post_id):
    posts = soup.find_all("div", class_="wall_item post--withRedesign")
    post1 = posts[0]
    post1_id = find_id(post1)
    post2 = posts[1]
    post2_id = find_id(post2)

    if post1_id > post2_id:
        result = postprocess(post1, back_post_id, post1_id)
    else:
        result = postprocess(post2, back_post_id, post2_id)
    return result[0], result[1]


def find_id(postitem):
    post_idtag = postitem.find("a", class_="post__anchor anchor")
    post_id = int(str(post_idtag['name']).replace("post-%number%_", "")) #Insert the number of the VK group from where you want to repost instead of %number%
    return post_id

def postprocess(postitem, back_post_id, post_id):

    if post_id > back_post_id:
        # Выводим текст постаа
        text_post = postitem.find("div", class_="pi_text").text.strip()
        text_to_print = text_post
        # Перенос ссылки на новую строку при наличии
        PostLink = str(text_post).find("http")
        if PostLink != -1:
            text_to_print = str(text_post).replace("http", "\n http")
        # Проверяю, что наличие поля - "Показать полностью" для длинного текста. Если коротки текст - ничего не делаем. Если длинный - поле удаляем.
        PostMore = str(postitem).find("PostTextMore__content")
        if PostMore != -1:
            text_to_del = postitem.find(
                "span", class_="PostTextMore__content").text.strip()
            text_to_print = str(text_post).replace(text_to_del, "")
        return text_to_print, post_id
    else:
        return None, back_post_id


bot.polling()
