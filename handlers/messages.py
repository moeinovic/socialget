import logging
import traceback
from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BadRequest
from twittic import TwitterAPI
from twittic.exceptions import NotFound, Forbidden, ContentError, TooManyRequests
from requests import Session
from wget import download
from os import remove
from numerize import numerize as num
from re import search
from utils.exceptions import errors
from utils.config import TWITTER_PATTERN

async def tweet_fetch(message: types.Message):
    try:
        Cli = message.bot
        tweet_url = message.text
        status_id = search(TWITTER_PATTERN, tweet_url).group(3)
        tweet = TwitterAPI()
        tweet_info = tweet.get_status(status_id)
        tweet_text = tweet_info['full_text']
        favorite_count, retweet_count, reply_count = map(
            tweet_info.get, ['favorite_count', 'retweet_count', 'reply_count'])
        static_string = "❤️{} |🔁 {} |💬 {}".format(
            num.numerize(favorite_count), num.numerize(retweet_count), num.numerize(reply_count))
        user_info = tweet_info['user']
        userinfo_string = "👤{} | <a href='https://twitter.com/{}'>@{}</a>".format(
            user_info['name'], user_info['user_name'], user_info['user_name'])
        caption = "{}\n{}\n{}".format(tweet_text, static_string, userinfo_string)
        has_media, media_count, medias = map(
            tweet_info.get, ['has_media', 'media_count', 'medias'])

        if has_media:
            if media_count == 1:
                media = medias[0]
                media_type = media['type']
                if media_type in ["photo", "video", "animated_gif"]:
                    await handle_single_media(
                        Cli, message, media, status_id, caption)
            elif media_count > 1:
                await handle_multiple_media(Cli, message, medias, caption)
        else:
            await message.reply(errors["notmediafound"])

    except ContentError:
        await message.reply(errors["videoerror"])
    except NotFound:
        await message.reply(errors["notfound"])
    except Forbidden:
        await message.reply(errors["forbidden"])
    except TooManyRequests:
        await message.reply(errors["toomany"])
    except Exception as e:
        logging.error(e)
        await message.reply(errors["unknown"])
        print(traceback.format_exc())
    finally:
        return

async def handle_single_media(Cli, message, media, status_id, caption):
    media_type = media['type']
    if media_type == "photo":
        image_url = media['url']
        await Cli.send_photo(message.chat.id, image_url, caption=caption, reply_to_message_id=message.message_id)
    elif media_type in ["video", "animated_gif"]:
        await handle_video(message, media, status_id, caption)

async def handle_video(message, media, status_id, caption):
    video_urls = media['urls']
    qualityies = types.InlineKeyboardMarkup()
    for url in video_urls:
        resolution = url['resolution']
        callback = f"dlt_{status_id}_{resolution}"
        size = tweet.convert_size(int(Session().head(url['url']).headers["Content-Length"]))
        inline_text = f"{resolution} - {size}"
        qualityies.add(types.InlineKeyboardButton(
            text=inline_text, callback_data=callback))
    qualityies.add(types.InlineKeyboardButton(
        text="SocialGetBot", callback_data=message.from_user.id))
    await message.reply("Select the video quality", reply_markup=qualityies)

async def handle_multiple_media(Cli, message, medias, caption):
    media_group = types.MediaGroup()
    for i, media in enumerate(medias):
        media_type = media['type']
        image_url = media['url']
        if i == 0:
            media_group.attach_photo(image_url, caption=caption)
            continue
        media_group.attach_photo(image_url)
    await Cli.send_media_group(message.chat.id, media_group, reply_to_message_id=message.message_id)

def twetter_register_commands(dp: Dispatcher):
    dp.register_message_handler(tweet_fetch, regexp=TWITTER_PATTERN)
