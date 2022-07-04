import os
import uuid
import textwrap
import requests

from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/createimage', methods=['GET'])
def createimage():
    UID = uuid.uuid1()
    title = request.args['title']
    artist = request.args['artist']
    genre = request.args['genre']
    type = request.args['type']
    cover = request.args['cover']
    inputfile = f'input_{UID}.png'
    response = requests.get(cover)
    open(inputfile, "wb").write(response.content)

    outputfile = f'output_{UID}.png'
    create_image(title, artist, genre, type, inputfile, outputfile)
    os.remove(inputfile)
    return send_file(outputfile)

def create_image(title: str, artist: str, genre: str, type: str, inputfile: str,
                       outputfile: str):
    artist_font = ImageFont.truetype('resources/fonts/Inter-Medium.ttf', 60)
    title_font = ImageFont.truetype('resources/fonts/Inter-Medium.ttf', 90)
    info_font = ImageFont.truetype('resources/fonts/Inter-Medium.ttf', 35)
    cover = Image.open(inputfile)
    background = Image.open('resources/images/bg_new_either.png')
    small_cover = cover.resize((650, 650), Image.ANTIALIAS)
    round_corner = circle_corner(small_cover, 35)
    background.paste(round_corner, (670, 170), round_corner)
    draw_title = ImageDraw.Draw(background)

    artisty = 220
    for line in textwrap.wrap(artist, width=15):
        draw_title.text((60, artisty),
                        line,
                        font=artist_font,
                        fill=('#DDEBF3'))
        artisty += artist_font.getsize(line)[1]

    titley = artisty + 20
    for line in textwrap.wrap(title, width=10):
        draw_title.text((60, titley),
                        line,
                        font=title_font,
                        fill=("#FFFFFF"))
        titley += title_font.getsize(line)[1]

    draw_title.text((274, 728),
                        type,
                        font=info_font,
                        fill=("#EBEEF0"))

    draw_title.text((177, 783),
                    genre,
                    font=info_font,
                    fill=("#EBEEF0"))
    background.save(outputfile)
    pass

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


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=1337)
