import os

from django.template import Library
from django.conf import settings
import Image
import ImageOps

FORMAT = 'JPEG'
EXTENSION = 'jpg'
QUALITY = 90


def resized_path(fname, size, method):
    "Get the path for the resized image."
    dir, name = os.path.split(fname)
    image_name, ext = os.path.splitext(name)
    return os.path.join(dir, '%s_%s_%s.%s' %
                        (image_name, method, size, EXTENSION))


def resize(relative_path, size, method):
    image_file = os.path.join(settings.MEDIA_ROOT, relative_path)
    relative_resized_path = resized_path(relative_path, size, method)
    resized_file = os.path.join(settings.MEDIA_ROOT, relative_resized_path)
    relative_url = os.path.join(settings.MEDIA_URL, relative_resized_path)
    if os.path.exists(resized_file):
        return relative_url

    image = Image.open(image_file)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Parse size string 'WIDTHxHEIGHT'
    width, height = [int(i) for i in size.split('x')]

    # use PIL methods to edit images
    if method == 'scale':
        image.thumbnail((width, height), Image.ANTIALIAS)
        image.save(resized_file, FORMAT, quality=QUALITY)
    elif method == 'crop':
        ImageOps.fit(image, (width, height), Image.ANTIALIAS).save(
            resized_file, FORMAT, quality=QUALITY)

    return relative_url


def scale(relative_path, size):
    return resize(relative_path, size, 'scale')


def crop(relative_path, size):
    return resize(relative_path, size, 'crop')


register = Library()
register.filter('scale', scale)
register.filter('crop', crop)
