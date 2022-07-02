import logging
from pprint import pp, pprint
from re import search
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BadRequest
from time import time
from numerize import numerize as num
from requests import Session
from twittic import TwitterAPI
from twittic.exceptions import (Forbidden, NotFound, ContentError)
from wget import download
from config import lele as msg

API_TOKEN = '5227234241:AAGyRM4oqaWjyPLzLmm3s7tq0NrZtvKpGPY'
PROXY_URL = 'socks5://127.0.0.1:7890'
INSTA_SESSION = "51209710385%3AGrtJvXtvzFwHDK%3A11"
INSTAGRAM_POST_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/(?:p|tv|reel)\\/([^/?#&]+)).*$"
INSTAGRAM_STORY_URL_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/stories\\/([^/?#&]+)).*$"
INSTAGRAM_PROFILE_URL_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/([^/?#&]+)).*$"
TWITTER_TWEET_PATTERN_WITH_ONE_ESCAPE = "^(https?:\/\/(?:www\.)?(?:mobile\.)?twitter\.com(?:\/(?!.*\.\.)(?!.*\\.$)[^\W][\w.]{1,30})?\/status(es)?\/([\d+]{16,19}))"
proxy = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
Cli = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(Cli)

"""@dp.message_handler(regexp=INSTAGRAM_POST_PATTERN)
async def download_post(message: types.Message):
    try:
        media_info = insta.media_info(
            insta.media_pk_from_url(
                message.text)).dict()
        media_type = media_info['media_type']
        caption = media_info['caption_text']
        media_type = media_info['media_type']
        comment_count = media_info['comment_count']
        like_count = media_info['like_count']
        user_info = media_info['user']
        full_caption = "{}\n 💬 {} 👍 {} | <a href='https://www.instagram.com/{}'>👤{}</a>".format(
            caption,
            num.numerize(comment_count),
            num.numerize(like_count),
            user_info["username"],
            user_info['full_name'])
        if media_type in [1, 2]:
            if media_type == 1:
                image_url = media_info["thumbnail_url"]
                await Cli.send_photo(message.chat.id, image_url, caption=full_caption, reply_to_message_id=message.message_id)
            elif media_type == 2:
                video_url = str(media_info["video_url"])
                size = int(head(video_url).headers["Content-Length"])
                if size >= 20971519:
                    status = "File size is too big please wait to download progress will be start"
                    status_message = await message.answer(status)
                    file = download(video_url)
                    await Cli.send_video(message.chat.id, types.InputFile(file), caption=full_caption, reply_to_message_id=message.message_id)
                    await status_message.delete()
                else:
                    await Cli.send_video(message.chat.id, video_url, caption=full_caption, reply_to_message_id=message.message_id)

    except Exception as e:
        logging.error(e)"""

#twitter post downloader by twitterapi
@dp.message_handler(regexp=TWITTER_TWEET_PATTERN_WITH_ONE_ESCAPE)
async def download_tweet(message: types.Message):
    try:
        tweet_url = message.text
        status_id = search(TWITTER_TWEET_PATTERN_WITH_ONE_ESCAPE, tweet_url).group(3)
        tweet = TwitterAPI()
        tweet_info = tweet.get_status(status_id)
        tweet_text = tweet_info['full_text']
        favorite_count = tweet_info['favorite_count']
        retweet_count = tweet_info['retweet_count']
        reply_count = tweet_info['reply_count']
        static_string = "❤️{} |🔁 {} |💬 {}".format(
            num.numerize(favorite_count),
            num.numerize(retweet_count),
            num.numerize(reply_count)
            )
        userinfo_string = "👤{} | <a href='https://twitter.com/{}'>@{}</a>".format(
            tweet_info['user']['name'],
            tweet_info['user']['user_name'],
            tweet_info['user']['user_name']
        )
        caption = "{}\n{}\n{}".format(tweet_text, static_string, userinfo_string)
        has_media = tweet_info['has_media']
        media_count = tweet_info['media_count']
        if has_media:
            if media_count == 1:
                media_type = tweet_info['medias'][0]['type']
                if media_type == "photo":
                    image_url = tweet_info['medias'][0]['url']
                    await Cli.send_photo(message.chat.id, image_url, caption=caption, reply_to_message_id=message.message_id)
                elif media_type == "video" or media_type == "animated_gif":
                    video_url = tweet_info['medias'][0]['urls'][0]["url"]
                    qualityies = types.InlineKeyboardMarkup()
                    for media in tweet_info['medias'][0]["urls"]:
                        resolution = media['resolution']
                        callback = f"dl_{status_id}_{resolution}"
                        size = tweet.convert_size(int(Session().head(media['url']).headers["Content-Length"]))
                        inline_text = f"{resolution} - {size}"
                        qualityies.add(types.InlineKeyboardButton(text=inline_text, callback_data=callback))
                    qualityies.add(types.InlineKeyboardButton(text="SocialGetBot", callback_data=message.from_user.id))
                    message = await message.reply("Select the video quality", reply_markup=qualityies)
            elif media_count > 1:
                media_group = types.MediaGroup()
                for i, media in enumerate(tweet_info['medias']):
                    media_type = media['type']
                    image_url = media['url']
                    if i == 0:
                        media_group.attach_photo(image_url, caption=caption)
                        continue
                    media_group.attach_photo(image_url)

                await Cli.send_media_group(message.chat.id, media_group, reply_to_message_id=message.message_id)
        else:
            await message.reply(msg["notmediafound"])
    except ContentError:
        await message.reply("bro nigga")
        print(msg)
    except NotFound:
        await message.reply(msg["notfound"])
    except Forbidden:
        await message.reply(msg["forbidden"])
    except Exception as e:
        await message.reply(msg["unknown"])
    finally:
        return

@dp.callback_query_handler()
async def handler(data: types.CallbackQuery):
    try:
        user_id = data.from_user.id
        _, sid, res = data.data.split("_")
        message = data.message
        if hasattr(message, "reply_to_message"):
            try:
                cli_id = message.reply_to_message.from_user.id
            except AttributeError:
                cli_id = message.reply_markup.inline_keyboard[-1].callback_data
            if cli_id == user_id:
                bro = await message.edit_text(f"Downloading {res}\n please don't delete the link message")
                api = TwitterAPI()
                tweet_info = api.get_status(sid)
                if tweet_info["has_media"] and tweet_info["media_count"] == 1:
                    media_type = tweet_info["medias"][0]["type"]
                    if media_type == "video":
                        for url in tweet_info["medias"][0]["urls"]:
                            if url["resolution"] == res:
                                tweet_text = tweet_info['full_text']
                                favorite_count = tweet_info['favorite_count']
                                retweet_count = tweet_info['retweet_count']
                                reply_count = tweet_info['reply_count']
                                static_string = "❤️{} |🔁 {} |💬 {}".format(
                                    num.numerize(favorite_count),
                                    num.numerize(retweet_count),
                                    num.numerize(reply_count)
                                    )
                                userinfo_string = "👤{} | <a href='https://twitter.com/{}'>@{}</a>".format(
                                    tweet_info['user']['name'],
                                    tweet_info['user']['user_name'],
                                    tweet_info['user']['user_name']
                                )
                                caption = "{}\n{}\n{}".format(tweet_text, static_string, userinfo_string)
                                try:
                                    await Cli.send_video(message.chat.id, url["url"], thumb=tweet_info["medias"][0]["thumbnail_url"], reply_to_message_id=message.reply_to_message.message_id, caption=caption)
                                    await message.delete()
                                except BadRequest:
                                    mention = f"<a href='tg://user?id={message.from_user.id}'>@{data.from_user.full_name}</a>"
                                    caption = f"{caption} \n {mention}"
                                    await Cli.send_video(message.chat.id, url["url"], thumb=tweet_info["medias"][0]["thumbnail_url"], caption=caption)
                                break
                        
                else:
                    await bro.edit_text(msg["notmediafound"])
            else:
                await data.answer(msg["permission"], show_alert=True)
    except NotFound:
        await data.answer(text=msg["fetch"])
    except Forbidden:
        await data.answer(text=msg["forbidden"])
    except Exception as e:
        await data.answer(text=msg["unknown"])
    finally:
        return       
executor.start_polling(dp, skip_updates=True)
