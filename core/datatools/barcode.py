import tempfile
import os.path
import barcode
from barcode.writer import ImageWriter
from django.conf import settings


def create_jpg(number: int, filename: str = None, tmp_dir: str = None, write_text: bool = True,
               module_height=15.0, text_distance=5.0, image_format='jpeg'):
    """
        text - текст, который нужно закодировать
        filename - название файла, которое быдет установлено сгенерированной jpg-картинке с кодом
    """
    if not filename:
        filename = str(number)

    # временный каталог для генерации промежуточных файлов
    if not tmp_dir:
        if not os.path.exists(settings.DIR_FOR_TMP_FILES):
            os.makedirs(settings.DIR_FOR_TMP_FILES)
        tmp_dir = tempfile.mkdtemp(dir=settings.DIR_FOR_TMP_FILES)

    # сгенерируем название для врменного файла
    tmp_jpg_path = tempfile.mktemp(dir=tmp_dir, prefix=filename)

    writer = ImageWriter()
    writer.format = image_format

    Code128 = barcode.get_barcode_class('code128')
    ean = Code128(str(number), writer=writer)

    options = {
        # 'module_width': 0.15,
        'module_height': module_height,
        # 'quiet_zone': 6.5,
        # 'font_size': 7,
        'text_distance': text_distance,
        # 'background': 'white',
        # 'foreground': 'black',
        'write_text': write_text,
        # 'text': '',
    }
    bar_code_path = ean.save(tmp_jpg_path, options)

    return bar_code_path
