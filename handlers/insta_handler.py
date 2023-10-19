from aiogram import types, Dispatcher
from utils.config import (INSTA_SESSION, INSTAGRAM_POST_PATTERN, INSTAGRAM_STORY_PATTERN)
from instagrapi import Client
from numerize import numerize as num
from requests import Session
from wget import download
import traceback
from os import remove

async def download_post(message: types.Message):
    try:
        start = await message.reply("Downloading...")
        insta = Client()
        insta.login_by_sessionid(INSTA_SESSION)

        media_info = insta.media_info(insta.media_pk_from_url(message.text)).dict()
        media_type = media_info['media_type']
        caption = media_info['caption_text']
        comment_count, like_count = map(media_info.get, ['comment_count', 'like_count'])
        user_info = media_info['user']

        full_caption = "{}\n 💬 {} 👍 {} | <a href='https://www.instagram.com/{}'>👤{}</a>".format(
            caption, num.numerize(comment_count), num.numerize(like_count),
            user_info["username"], user_info['full_name']
        )

        if media_type in {1, 2}:
            if media_type == 1:
                image_url = media_info["thumbnail_url"]
                await send_media(start, message, image_url, full_caption)
            elif media_type == 2:
                video_url = str(media_info["video_url"])
                await handle_video(start, message, video_url, full_caption)

        elif media_type == 8:
            resources = media_info["resources"]
            media_group = types.MediaGroup()

            for resource in resources:
                if resource["media_type"] == 1:
                    image_url = str(resource["thumbnail_url"])
                    media_group.attach_photo(image_url, caption=full_caption)
                elif resource["media_type"] == 2:
                    video_url = resource["video_url"]
                    media_group.attach_video(video_url, caption=full_caption)

            await send_media(start, message, media_group=media_group)

    except Exception:
        await handle_error(start)

async def download_story(message: types.Message):
    try:
        start = await message.reply("Downloading...")
        insta = Client()
        insta.login_by_sessionid(INSTA_SESSION)

        story_pk = insta.story_pk_from_url(message.text)
        story_info = insta.story_info(story_pk).dict()
        media_type = story_info["media_type"]
        user_info = story_info["user"]

        full_caption = "<a href='https://www.instagram.com/{}'>👤{}</a>".format(
            user_info["username"], user_info['full_name']
        )

        if media_type in {1, 2}:
            if media_type == 1:
                image_url = str(story_info["thumbnail_url"])
                await send_media(start, message, image_url, full_caption)
            elif media_type == 2:
                video_url = str(story_info["video_url"])
                await send_media(start, message, video_url, full_caption)

    except Exception:
        await handle_error(start)
        await message.reply_text(traceback.format_exc())

async def send_media(start, message, media_url=None, caption=None, media_group=None):
    try:
        if media_group:
            await message.reply_media_group(media_group)
        elif media_url:
            await message.reply_photo(media_url, caption=caption) if media_url.endswith('.jpg') else await message.reply_video(media_url, caption=caption)
    finally:
        await start.delete()

async def handle_video(start, message, video_url, full_caption):
    size = int(await Session().head(video_url).headers["Content-Length"])
    if size <= 20971520:
        await send_media(start, message, video_url, full_caption)
    elif size > 20971520 and size <= 52428800:
        await send_big_video(start, message, video_url, full_caption)
    elif size >= 52428800:
        await start.edit_text("File Size is bigger than 50MB!")

async def send_big_video(start, message, video_url, full_caption):
    try:
        status = "File size is too big please wait to download progress will be start"
        await start.edit_text(status)
        file = download(video_url)
        await send_media(start, message, file, full_caption)
    finally:
        remove(file)

async def handle_error(start):
    await start.edit_text("Something went wrong!")

def insta_register(dp: Dispatcher):
    dp.regiCertainly! Here's an optimized version of your code:

```python
from aiogram import types, Dispatcher
from utils.config import (INSTA_SESSION, INSTAGRAM_POST_PATTERN, INSTAGRAM_STORY_PATTERN)
from instagrapi import Client
from numerize import numerize as num
from requests import Session
from wget import download
import traceback
from os import remove

async def download_post(message: types.Message):
    try:
        start = await message.reply("Downloading...")
        insta = Client()
        insta.login_by_sessionid(INSTA_SESSION)

        media_info = insta.media_info(insta.media_pk_from_url(message.text)).dict()
        media_type = media_info['media_type']
        caption = media_info['caption_text']
        comment_count, like_count = map(media_info.get, ['comment_count', 'like_count'])
        user_info = media_info['user']

        full_caption = "{}\n 💬 {} 👍 {} | <a href='https://www.instagram.com/{}'>👤{}</a>".format(
            caption, num.numerize(comment_count), num.numerize(like_count),
            user_info["username"], user_info['full_name']
        )

        if media_type in {1, 2}:
            if media_type == 1:
                image_url = media_info["thumbnail_url"]
                await send_media(start, message, image_url, full_caption)
            elif media_type == 2:
                video_url = str(media_info["video_url"])
                await handle_video(start, message, video_url, full_caption)

        elif media_type == 8:
            resources = media_info["resources"]
            media_group = types.MediaGroup()

            for resource in resources:
                if resource["media_type"] == 1:
                    image_url = str(resource["thumbnail_url"])
                    media_group.attach_photo(image_url, caption=full_caption)
                elif resource["media_type"] == 2:
                    video_url = resource["video_url"]
                    media_group.attach_video(video_url, caption=full_caption)

            await send_media(start, message, media_group=media_group)

    except Exception:
        await handle_error(start)

async def download_story(message: types.Message):
    try:
        start = await message.reply("Downloading...")
        insta = Client()
        insta.login_by_sessionid(INSTA_SESSION)

        story_pk = insta.story_pk_from_url(message.text)
        story_info = insta.story_info(story_pk).dict()
        media_type = story_info["media_type"]
        user_info = story_info["user"]

        full_caption = "<a href='https://www.instagram.com/{}'>👤{}</a>".format(
            user_info["username"], user_info['full_name']
        )

        if media_type in {1, 2}:
            if media_type == 1:
                image_url = str(story_info["thumbnail_url"])
                await send_media(start, message, image_url, full_caption)
            elif media_type == 2:
                video_url = str(story_info["video_url"])
                await send_media(start, message, video_url, full_caption)

    except Exception:
        await handle_error(start)
        await message.reply_text(traceback.format_exc())

async def send_media(start, message, media_url=None, caption=None, media_group=None):
    try:
        if media_group:
            await message.reply_media_group(media_group)
        elif media_url:
            await message.reply_photo(media_url, caption=caption) if media_url.endswith('.jpg') else await message.reply_video(media_url, caption=caption)
    finally:
        await start.delete()

async def handle_video(start, message, video_url, full_caption):
    size = int(await Session().head(video_url).headers["Content-Length"])
    if size <= 20971520:
        await send_media(start, message, video_url, full_caption)
    elif size > 20971520 and size <= 52428800:
        await send_big_video(start, message, video_url, full_caption)
    elif size >= 52428800:
        await start.edit_text("File Size is bigger than 50MB!")

async def send_big_video(start, message, video_url, full_caption):
    try:
        status = "File size is too big please wait to download progress will be start"
        await start.edit_text(status)
        file = download(video_url)
        await send_media(start, message, file, full_caption)
    finally:
        remove(file)

async def handle_error(start):
    await start.edit_text("Something went wrong!")

def insta_register(dp: Dispatcher):
    dp.register_message_handler(download_post, regexp=INSTAGRAM_POST_PATTERN)
    dp.register_message_handler(download_story, regexp=INSTAGRAM_STORY_PATTERN)
