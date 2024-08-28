# Pipisters
from turtle import width
from config import Config
from flask import Flask, redirect, render_template, request, url_for, abort, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from PIL import Image as ImagePillow
from sqlalchemy.orm import sessionmaker


from utils.db import choose_random_records, is_mobile
from utils.utils import download_image, png_to_jpg, process_image

SIZES = [236, 474, 736]

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор
    urlOriginal = db.Column(db.String(200), nullable=False)  # Оригинальное изображение
    widthOrig = db.Column(db.Integer, nullable=False)  # Ширина оригинального изображения
    heightOrig = db.Column(db.Integer, nullable=False)  # Высота оригинального изображения
    img236jpg = db.Column(db.LargeBinary, nullable=False)  # Бинарные данные для изображения 236
    img474jpg = db.Column(db.LargeBinary, nullable=False)  # Бинарные данные для изображения 474
    img736jpg = db.Column(db.LargeBinary, nullable=False)  # Бинарные данные для изображения 736

with app.app_context():
    db.create_all() 


def calculate_gap_height(width, original_width, original_height):
    margin_bottom = 20

    scale = width / original_width
    relative_height = original_height * scale
    gap_height = int(relative_height + margin_bottom + 1)  # Приведение к целому числу
    if gap_height > 495:
        gap_height = 495
    return gap_height

def calculate_gap_pin_height(width, original_width, original_height):
    margin_bottom = 20
    scale = width / original_width
    relative_height = original_height * scale
    gap_height = int(relative_height + margin_bottom + 1)  # Приведение к целому числу
    return gap_height

# Регистрация функции как фильтра
app.jinja_env.filters['calculate_gap_height'] = calculate_gap_height
app.jinja_env.filters['calculate_gap_pin_height'] = calculate_gap_pin_height

@app.route('/main')
def main():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    img_url = request.form.get('img_url')
    if not img_url:
        return redirect(url_for('index'))
    # Проверка url по базе
    image = Image.query.filter_by(urlOriginal=img_url).first()
    if image:
        print('Image already exists')
        return redirect(url_for('index'))
    try: 
        jpg_img = []
        image_bytes = download_image(img_url)
        width, height = 0, 0
        # Преобразование изображения
        with ImagePillow.open(BytesIO(image_bytes)) as img:
            width, height = img.size
            for size in SIZES:
                resized_img = process_image(img, size)
                to_jpg = png_to_jpg(resized_img, app.config['JPG_QUALITY'])
                jpg_img.append(to_jpg.getvalue())
        # Добавьте и сохраните в базу данных
        new_image  = Image(
            urlOriginal=img_url,
            widthOrig=width,
            heightOrig=height,
            img236jpg=jpg_img[0],
            img474jpg=jpg_img[1],
            img736jpg=jpg_img[2]
        )
        db.session.add(new_image)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        print(e)
        return redirect(url_for('index'))

@app.route('/pinimg/<size>/<int:image_id>.jpg')
def get_image(size, image_id):
    # Проверьте, что размер является допустимым
    if size not in ['236x', '474x', '736x']:
        abort(404)

    # Найдите изображение в базе данных по id
    image = Image.query.get(image_id)
    if not image:
        abort(404)

    # Выберите соответствующее изображение в зависимости от размера
    if size == '236x':
        img_data = image.img236jpg
    elif size == '474x':
        img_data = image.img474jpg
    elif size == '736x':
        img_data = image.img736jpg
    else:
        abort(404)

    # Если изображение не найдено в базе данных
    if img_data is None:
        abort(404)

    # Отправьте изображение в ответ
    return send_file(BytesIO(img_data), mimetype='image/jpeg')

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    with app.app_context():
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db.engine)
        session = SessionLocal()
        try:
            result = choose_random_records(session, Image, app.config['COUNT_IMAGES'])
            base_image_width = app.config['MOBILE_SIZE_PIXELS'] if is_mobile(user_agent) else app.config['BASE_SIZE_PIXELS']
            return render_template('main.html', images=result, width=base_image_width, is_mobile=is_mobile(user_agent))
        finally:
            session.close()
    return redirect(url_for('index'))

@app.route('/back', methods=['GET'])
def go_back():
    referer = request.headers.get('Referer')
    print('Referer:', referer)
    if referer:
        return redirect(referer)
    else:
        # Если заголовок Referer не найден, перенаправляем на главную страницу
        return redirect('/')


@app.route('/pin/<int:image_id>')
def pin(image_id):
    user_agent = request.headers.get('User-Agent')
    image = Image.query.get(image_id)
    if not image:
        abort(404)
    # Похожие изображения 
    with app.app_context():
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db.engine)
        session = SessionLocal()
        try:
            result = choose_random_records(session, Image, app.config['COUNT_IMAGES'])
            base_image_width = app.config['MOBILE_SIZE_PIXELS'] if is_mobile(user_agent) else app.config['BASE_SIZE_PIXELS']
            return render_template('pin.html', image=image, images=result, width=base_image_width, is_mobile=is_mobile(user_agent))
        finally:
            session.close()
    abort(500)

if __name__ == '__main__':
    app.run(debug=True)
