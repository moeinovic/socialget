import logging 
import traceback

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BadRequest
from twittic import TwitterAPI
from twittic.exceptions import NotFound, Forbidden, ContentError

from requests import Session
from wget import download
from os import remove

from numerize import numerize as num
from re import search

from utils.exceptions import errors
from utils.config import (TWITTER_PATTERN)

async def tweet_fetch(message: types.Message):
    try:
        Cli = message.bot
        tweet_url = message.text
        status_id = search(TWITTER_PATTERN, tweet_url).group(3)
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
                    with Session().head(video_url) as s:
                        if s.status_code == 403:
                            raise ContentError("Video")
                    
                    qualityies = types.InlineKeyboardMarkup()
                    for media in tweet_info['medias'][0]["urls"]:
                        resolution = media['resolution']
                        callback = f"dlt_{status_id}_{resolution}"
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
            await message.reply(errors["notmediafound"])
    except ContentError:
        await message.reply(errors["videoerror"])
    except NotFound:
        await message.reply(errors["notfound"])
    except Forbidden:
        await message.reply(errors["forbidden"])
    except Exception as e:
        logging.error(e)
        await message.reply(errors["unknown"])
        await message.bot.send_message("@moeinovich", traceback.format_exc())
    finally:
        return

def twetter_register_commands(dp: Dispatcher):
    dp.register_message_handler(tweet_fetch, regexp=TWITTER_PATTERN)