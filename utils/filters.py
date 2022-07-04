from aiogram.utils.callback_data import CallbackData

async def callback(data: CallbackData):
    return data.data.startswith("dlt_")