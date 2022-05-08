from aiogram.dispatcher.filters.state import State, StatesGroup


class UploadState(StatesGroup):
    uploading_photo = State()