import random
import requests


def generate_cook_image(query, app_id, app_key):
    api_url = f"https://api.edamam.com/api/recipes/v2?type=public&q={query}&app_id={app_id}&app_key={app_key}&field=image"

    try:
        r = requests.get(api_url)
        if r.status_code != 200:
            return None

        rj = r.json()
        if "hits" not in rj or not len(rj["hits"]) > 0:
            return None

        data = rj["hits"]
        data = data[random.randint(1, min(5, len(data) - 1))] if len(data) > 1 else data[0]

        if "recipe" not in data or "image" not in data["recipe"]:
            return None

        image = data["recipe"]["image"]
        return image
    except Exception as e:
        return None
