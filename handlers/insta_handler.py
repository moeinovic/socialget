from aiogram import Bot, Dispatcher, executor, types
from utils.config import (INSTA_SESSION, INSTAGRAM_POST_PATTERN, INSTAGRAM_PROFILE_PATTERN, INSTAGRAM_STORY_PATTERN)
from os import  remove
from instagrapi import Client
from numerize import numerize as num
from requests import Session
from wget import download
import traceback

async def download_post(message: types.Message):
    try:
        insta = Client()
        insta.login_by_sessionid(INSTA_SESSION)
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
                await message.reply_photo(image_url, caption=full_caption)
            elif media_type == 2:
                video_url = str(media_info["video_url"])
                thumbnail_url = str(media_info["thumbnail_url"])
                duration = int(media_info["video_duration"])
                size = int(Session().head(video_url).headers["Content-Length"])
                if size <= 20971520:
                    await message.reply_video(video_url, caption=full_caption)
                elif size > 20971520 and size <= 52428800:
                    status = "File size is too big please wait to download progress will be start"
                    status_message = await message.answer(status)
                    file = download(video_url)
                    await message.reply_video(file, caption=full_caption)
                    await status_message.delete()
                    remove(file)
                elif size >= 52428800:
                    await message.reply("File Size is bigger than 50MB!")
            elif media_type == 8:
                resources = media_info["resources"]
                media_group = types.MediaGroup()
                with Session as s:
                    for resource in resources:
                        if resource["media_type"] == 1:
                            image_url = str(resource["thumbnail_url"])
                            media_group.append(types.InputMediaPhoto(types.InputFile(download(image_url))))
                        elif resource["media_type"] == 2:
                            video_url = resource["video_url"]
                            media_group.attach_video(video_url)
                    if len(media_group.media) == len(resources):
                        await message.reply_media_group(media_group)
                                
    except Exception as e:
        print(traceback.format_exc())


def insta_register(dp: Dispatcher):
    dp.register_message_handler(download_post, regexp=INSTAGRAM_POST_PATTERN)