import re
from utils.utils import replace_regex
# from .utils import replace_regex

DEFAULT_MAP_DICT = {
    " c ": " c. ",
    ", chopped": " (chopped)",
    ", crumbled": " (crumbled)",
    ", thawed": " (thawed)",
    ", melted": " (melted)",
}


def ingredient(text, map_dict):
    if len(map_dict) > 0:
        map_dict.update(**DEFAULT_MAP_DICT)
    else:
        map_dict = DEFAULT_MAP_DICT

    text = replace_regex(text, map_dict)
    text = re.sub(r"(\d)\s(\d\/\d)", r" \1+\2 ", text)
    text = " ".join([word.strip() for word in text.split() if word.strip()])
    return text


def ingredients(text_list, item_list, without_mapping=False):
    map_dict = {
        item: f'<span class="text-bold">{item}</span>' for item in list(map(lambda x: x.lower().strip(), item_list))
    }
    text_list = list(map(lambda x: x.lower(), text_list))

    output = []
    for text in text_list:
        map_dict = map_dict if not without_mapping else {}
        text = ingredient(text, map_dict)
        output.append(text)

    return output


def directions(text_list):
    text_list = list(map(lambda x: x.lower().capitalize(), text_list))

    return text_list
