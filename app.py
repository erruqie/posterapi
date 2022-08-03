import quopri
import qrcode
import base64
import textwrap
import requests

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/make_poster', methods=['GET'])
def createimage():
    title = request.args['title']
    artist = request.args['artist']
    genre = request.args['genre']
    type = request.args['type']
    cover = request.args['cover']
    response = requests.get(cover)
    inputfile = BytesIO(response.content)
    return send_file(create_image(title, artist, genre, type, inputfile), mimetype='image/png')

@app.route('/resize', methods=['GET'])
def resizeimage():
    w = int(request.args['w'])
    h = int(request.args['h'])
    cover = request.args['image']
    response = requests.get(cover)
    inputfile = BytesIO(response.content)
    image = Image.open(inputfile)
    resized_image = image.resize((w, h), Image.ANTIALIAS)
    img_io = BytesIO()
    rgb_im = resized_image.convert('RGB')
    rgb_im.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/make_qr', methods=['GET'])
def makeqr():
    url = request.args['url']
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    img = qr.make_image(fill_color=(107, 114, 128))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return send_file(buffered, mimetype='image/png')
    

def create_image(title: str, artist: str, genre: str, type: str, inputfile):
    artist_font = ImageFont.truetype('resources/fonts/Inter-Medium.ttf', 60)
    title_font = ImageFont.truetype('resources/fonts/Inter-Medium.ttf', 90)
    info_font = ImageFont.truetype('resources/fonts/Inter-Medium.ttf', 35)
    cover = Image.open(inputfile)
    background = Image.open('resources/images/VK_post.png')
    small_cover = cover.resize((750, 750), Image.ANTIALIAS)
    round_corner = circle_corner(small_cover, 35)
    background.paste(round_corner, (1080, 165), round_corner)
    draw_title = ImageDraw.Draw(background)

    artisty = 256
    for line in textwrap.wrap(artist, width=20):
        draw_title.text((100, artisty),
                        line,
                        font=artist_font,
                        fill=('#DDEBF3'))
        artisty += artist_font.getsize(line)[1]

    titley = artisty + 10
    for line in textwrap.wrap(title, width=15):
        draw_title.text((97, titley),
                        line,
                        font=title_font,
                        fill=("#FFFFFF"))
        titley += title_font.getsize(line)[1]

    draw_title.text((346, 871), # 730
                        type,
                        font=info_font,
                        fill=("#EBEEF0"))

    draw_title.text((237, 926), # 786
                        genre,
                        font=info_font,
                        fill=("#EBEEF0"))
    img_io = BytesIO()
    background.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

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
