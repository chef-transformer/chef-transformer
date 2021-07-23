import base64
import json
from io import BytesIO
from PIL import Image
import requests
import re


def load_image_from_local(image_path, image_resize=None):
    image = Image.open(image_path)

    if isinstance(image_resize, tuple):
        image = image.resize(image_resize)
    return image


def load_image_from_url(image_url, rgba_mode=False, image_resize=None, default_image=None):
    try:
        image = Image.open(requests.get(image_url, stream=True).raw)

        if rgba_mode:
            image = image.convert("RGBA")

        if isinstance(image_resize, tuple):
            image = image.resize(image_resize)

    except Exception as e:
        image = None
        if default_image:
            image = load_image_from_local(default_image, image_resize=image_resize)

    return image


def load_text(text_path):
    text = ''
    with open(text_path) as f:
        text = f.read()

    return text


def load_json(json_path):
    jdata = ''
    with open(json_path) as f:
        jdata = json.load(f)

    return jdata


def image_to_base64(image_array):
    buffered = BytesIO()
    image_array.save(buffered, format="PNG")
    image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64, {image_b64}"


def unique_list(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def pure_comma_separation(list_str, return_list=True):
    r = unique_list([item.strip() for item in list_str.lower().split(",") if item.strip()])
    if return_list:
        return r
    return ", ".join(r)


def replace_regex(text, map_dict):
    pattern = "|".join(map(re.escape, map_dict.keys()))
    return re.sub(pattern, lambda m: map_dict[m.group()], str(text))
