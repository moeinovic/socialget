from aiogram import types, Dispatcher
from twittic import TwitterAPI
from twittic.exceptions import NotFound, Forbidden
from aiogram.utils.exceptions import BadRequest
from numerize import numerize as num
from requests import Session
from wget import download
from utils.exceptions import errors
from os import remove
from utils.filters import callback
import traceback
from asyncio import to_thread

async def twitter_video_dl(data: types.CallbackQuery):
    Cli = data.bot

    try:
        user_id = data.from_user.id
        _, sid, res = data.data.split("_")
        message = data.message

        if message.reply_to_message is not None:
            cli_id = message.reply_to_message.from_user.id
        else:
            cli_id = message.reply_markup.inline_keyboard[-1].callback_data

        if cli_id != user_id:
            await data.answer(errors["permission"], show_alert=True)
            return

        bro = await message.edit_text(f"Downloading {res}\n please don't delete the link message")
        api = TwitterAPI()

        try:
            tweet_info = api.get_status(sid)
            media = tweet_info.get("medias", [])

            if media and media[0].get("type") == "video":
                video_url = next((url["url"] for url in media[0]["urls"] if url["resolution"] == res), None)

                if video_url:
                    size = int(await to_thread(Session().head, video_url).headers["Content-Length"])

                    if size >= 20971520:
                        video_path = await to_thread(download, video_url)
                        video = types.InputFile(video_path)
                        dl = True
                    else:
                        video = video_url
                        dl = False

                    tweet_text = tweet_info.get('full_text', '')
                    favorite_count = tweet_info.get('favorite_count', 0)
                    retweet_count = tweet_info.get('retweet_count', 0)
                    reply_count = tweet_info.get('reply_count', 0)

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
                        await Cli.send_video(
                            message.chat.id,
                            video,
                            thumb=media[0].get("thumbnail_url", ''),
                            reply_to_message_id=message.reply_to_message.message_id,
                            caption=caption
                        )
                        await message.delete()
                    except BadRequest:
                        mention = f"<a href='tg://user?id={message.from_user.id}'>@{data.from_user.full_name}</a>"
                        caption = f"{caption} \n {mention}"
                        await Cli.send_video(
                            message.chat.id,
                            video,
                            thumb=media[0].get("thumbnail_url", ''),
                            caption=caption
                        )

                    if dl:
                        remove(video_path)

        except NotFound:
            await data.answer(errors["fetch"])
        except Forbidden:
            await data.answer(errors["forbidden"])
        except Exception as e:
            await data.answer(errors.get(str(e), errors["unknown"]))
            await Cli.send_message(chat_id=356520246, text=traceback.format_exc())

async def twetter_register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(twitter_video_dl, callback)
