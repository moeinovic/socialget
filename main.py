from aiogram import Bot, Dispatcher, executor, types
from handlers.callbacks import twetter_register_callbacks
from handlers.messages import twetter_register_commands
from utils.config import (API_TOKEN, INSTA_SESSION)

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

twetter_register_callbacks(dp)
twetter_register_commands(dp)

executor.start_polling(dp, skip_updates=True)
