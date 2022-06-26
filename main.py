import os
import logging
import textwrap

from dotenv import load_dotenv
from states import UploadState
from aiogram.utils import executor
from aiogram.types import InputFile
from aiogram import Bot, types, filters
from PIL import Image, ImageDraw, ImageFont
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv('.env')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get('BOT_TOKEN'), parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(filters.Command("create"))
async def process_create_command(message: types.Message):
    await message.reply(
        "Отправьте нужное изображение и в описание "
        "укажите наименование релиза и имя исполнителя через |\n\n"
        "<b>Например:</b> <code>Снова я напиваюсь|ИванЗоло2004</code>"
        "\n\nДля отмены используйте /cancel")
    await UploadState.uploading_photo.set()


@dp.message_handler(filters.CommandStart())
async def process_start_command(message: types.Message):
    await message.reply(
        "Привет. Используй команду /create и я сделаю изображение для поста"
    )


@dp.message_handler(filters.Command("cancel"), state="*")
async def process_cancel_command(message: types.Message, state: FSMContext):
    if not await state.get_state():
        return await message.reply("Нечего отменять...")
    else:
        await state.finish()
        return await message.reply("Успешно!")


@dp.message_handler(content_types=types.ContentTypes.PHOTO,
                    state=UploadState.uploading_photo)
async def process_photo_mmr(message: types.Message, state: FSMContext):
    input_img = 'input_' + str(message.chat.id) + '.png'
    output_img = 'output_' + str(message.chat.id) + '.png'

    await message.photo[-1].download(destination_file=input_img)

    separator = "|"
    arguments = message.caption
    if not arguments:
        return await message.reply(
            "Отправьте нужное изображение и в описание "
            "укажите наименование релиза и имя исполнителя через |\n\n"
            "<b>Например:</b> <code>Снова я напиваюсь|ИванЗоло2004</code>"
            "\n\nДля отмены используйте /cancel")
    args = arguments.split(separator)

    if len(args) < 2:
        os.remove(input_img)
        return await message.reply("Вы пропустили один аргумент")
    else:
        if os.path.isfile(input_img):
            await create_image(args[0], args[1], input_img, output_img)
            await message.reply("Отправляю изображение: " + args[1] + " - " +
                                args[0])
            await types.ChatActions.upload_document(1)
            await message.answer_document(InputFile(output_img))
        else:
            await message.reply(
                "Изображение обложки не найдено! Попробуйте отправить его заново"
            )
    os.remove(output_img)
    os.remove(input_img)
    await state.finish()


async def create_image(title: str, artist: str, inputfile: str,
                       outputfile: str):
    title_font = ImageFont.truetype('resources/fonts/SFPRODISPLAYREGULAR.ttf', 96)
    artist_font = ImageFont.truetype('resources/fonts/SFPRODISPLAYBOLD.ttf', 128)
    cover = Image.open(inputfile)
    background = Image.open('resources/images/background.png')
    small_cover = cover.resize((1020, 1020), Image.ANTIALIAS)
    round_corner = circle_corner(small_cover, 35)
    background.paste(round_corner, (1377, 210), round_corner)
    draw_title = ImageDraw.Draw(background)

    artisty = 375
    for line in textwrap.wrap(artist, width=15):
        draw_title.text((216, artisty),
                        line,
                        font=artist_font,
                        fill=('#000000'))
        artisty += artist_font.getsize(line)[1]

    titley = artisty + 50
    for line in textwrap.wrap(title, width=25):
        draw_title.text((216, titley),
                        line,
                        font=title_font,
                        fill=("#000000"))
        titley += title_font.getsize(line)[1]
    background.save(outputfile)


def circle_corner(img: Image.Image, radius: int):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    img = img.convert("RGBA")
    w, h = img.size

    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)),
                (w - radius, h - radius))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))

    img.putalpha(alpha)
    return img

def text_wrap(text,font,writing,max_width,max_height):
    lines = [[]]
    words = text.split()
    for word in words:
        lines[-1].append(word)
        (w,h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)
        if w > max_width:
            lines.append([lines[-1].pop()])
            (w,h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)
            if h > max_height:
                lines.pop()
                lines[-1][-1] += '...'
                while writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]),font=font)[0] > max_width:
                    lines[-1].pop()
                    if lines[-1]:
                        lines[-1][-1] += '...'
                    else:
                        lines[-1].append('...')
                break
    return '\n'.join([' '.join(line) for line in lines])

if __name__ == '__main__':
    executor.start_polling(dp)
