import requests
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse

def download_image(url, max_size_mb=15):
    """
    Скачивает изображение по URL и проверяет, что это действительно изображение.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Failed to download image")
    content_type = response.headers.get('Content-Type', '')
    if not content_type.startswith('image'):
        raise ValueError("Content is not an image")
    content_length = response.headers.get('Content-Length', None)
    if not content_length:
        raise ValueError("Content has no length")
    if not content_length.isnumeric():
        raise ValueError("Content length is not a number")
    try:
        content_length = int(content_length)
    except ValueError:
        raise ValueError("Content length is not an integer")
    if content_length > max_size_mb * 1024 * 1024:
        raise ValueError("Content is larger than max size")
    
    return response.content

def is_valid_url(url):
    """
    Проверяет, является ли строка допустимым URL.
    """
    parsed_url = urlparse(url)
    return all([parsed_url.scheme, parsed_url.netloc])

def process_image(pill_image, width):
    """
    Изменяет размер изображения до заданной ширины, сохраняя пропорции.
    """
    aspect_ratio = pill_image.height / pill_image.width
    new_height = int(width * aspect_ratio)
    resized_img = pill_image.resize((width, new_height), Image.LANCZOS)
    return resized_img

def png_to_jpg(pill_png_image, quality=85):
    """
    Конвертирует PNG в JPG с заданным качеством.
    """
    jpg_image = pill_png_image.convert('RGB')
    jpg_bytes = BytesIO()
    jpg_image.save(jpg_bytes, format='JPEG', quality=quality)
    jpg_bytes.seek(0)
    return jpg_bytes



if __name__ == '__main__':
    import time

    start = time.time()
    url = 'https://i.pinimg.com/originals/39/8e/4d/398e4de5e3bce9d7d9d5b9983c4d3edf.jpg'
    image_bytes = download_image(url)
    print(f'Время скачивания: {time.time() - start} секунд')

    start_process = time.time()
    with Image.open(BytesIO(image_bytes)) as img:
        # img.verify()
        sizes = [236, 474, 736]
        resized_img = process_image(img, sizes[2])
        print(f'Время изменения размера: {time.time() - start_process} секунд')

        start_jpg = time.time()
        to_jpg = png_to_jpg(resized_img, 80)
        print(f'Время конвертации: {time.time() - start_jpg} секунд')

        print(f'Время обработки: {time.time() - start_process} секунд')
        with open('test.jpg', 'wb') as f:
             f.write(to_jpg.getvalue())
    
    print(f'Время обработки с сохранением: {time.time() - start_process} секунд')
    print(f'Общее время: {time.time() - start} секунд')

