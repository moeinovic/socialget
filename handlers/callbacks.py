from aiogram import types, Dispatcher
from twittic import TwitterAPI
from twittic.exceptions import NotFound, Forbidden
from aiogram.utils.exceptions import BadRequest
import numerize as num
from requests import Session
from wget import download
from utils import errors
from os import remove
import traceback

async def twitter_video_dl(data: types.CallbackQuery):
    Cli = data.bot
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
                                video_url = url["url"]
                                size = int(Session().head(video_url).headers["Content-Length"])
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
                                if size >= 20971520:
                                    video_path = download(video_url)
                                    video = types.InputFile(video_path)
                                    dl = True
                                else:
                                    video = video_url
                                    dl = False
                                try:
                                    await Cli.send_video(message.chat.id, video, thumb=tweet_info["medias"][0]["thumbnail_url"], reply_to_message_id=message.reply_to_message.message_id, caption=caption)
                                    await message.delete()
                                except BadRequest:
                                    mention = f"<a href='tg://user?id={message.from_user.id}'>@{data.from_user.full_name}</a>"
                                    caption = f"{caption} \n {mention}"
                                    await Cli.send_video(message.chat.id, video, thumb=tweet_info["medias"][0]["thumbnail_url"], caption=caption)
                                if dl:
                                    remove(video_path)
                                break
                                
                else:
                    await bro.edit_text(errors["notmediafound"])
            else:
                await data.answer(errors["permission"], show_alert=True)
    except NotFound:
        await data.answer(errors["fetch"])
    except Forbidden:
        await data.answer(errors["forbidden"])
    except Exception as e:
        await data.answer(errors["unknown"])
        await Cli.send_message(chat_id=356520246, text=traceback.format_exc())
    finally:
        return       

def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(twitter_video_dl)