from PIL import (
    Image,
    ImageDraw
)
import textwrap
from utils.utils import load_image_from_url
from utils.ext import (
    ingredients as ext_ingredients,
    directions as ext_directions
)


# from .utils import load_image_from_url
# from .ext import (
#     ingredients as ext_ingredients,
#     directions as ext_directions
# )


def generate_food_with_logo_image(bg_path, logo_path, food_url, no_food="asset/frame/no_food.png"):
    bg = Image.open(bg_path)
    width, height = bg.size

    logo = Image.open(logo_path)
    logo_width, logo_height, logo_ratio, logo_rb, logo_mb = logo.size + (3, -20, 45)
    logo_width, logo_height = (logo_width // logo_ratio, logo_height // logo_ratio)
    logo = logo.resize((logo_width, logo_height))

    food = load_image_from_url(food_url, rgba_mode=True, default_image=no_food)

    food_width, food_height = (300, 300)
    food = food.resize((food_width, food_height))

    bg.paste(food, (0, 0), food)
    bg.paste(logo, (width - logo_width - logo_rb, height - logo_height - logo_mb), logo)

    return bg


def generate_recipe_image(
        recipe_data,
        bg_path,
        food_logo_ia,
        fonts,
        bg_color="#ffffff"
):
    bg = Image.open(bg_path)
    bg.paste(food_logo_ia, (50, 50), food_logo_ia)
    bg_color = Image.new("RGBA", bg.size, bg_color)
    bg_color.paste(bg, mask=bg)

    im_editable = ImageDraw.Draw(bg_color)
    im_editable.text(
        (418, 30),
        textwrap.fill(recipe_data["title"], 15).replace(" \n", "\n"),
        (61, 61, 70),
        font=fonts["title"],
    )

    im_editable.text(
        (100, 450),
        "Ingredients",
        (61, 61, 70),
        font=fonts["body_bold"],
    )
    ingredients = recipe_data["ingredients"]
    ingredients = ext_ingredients(ingredients, [], without_mapping=True)
    ingredients = [textwrap.fill(item, 30).replace("\n", "\n   ") for item in ingredients]

    im_editable.text(
        (50, 520),
        "\n".join([f"- {item}" for item in ingredients]),
        (61, 61, 70),
        font=fonts["body"],
    )

    im_editable.text(
        (700, 450),
        "Directions",
        (61, 61, 70),
        font=fonts["body_bold"],
    )

    directions = recipe_data["directions"]
    directions = ext_directions(directions)
    directions = [textwrap.fill(item, 70).replace("\n", "\n    ").capitalize() for item in directions]

    im_editable.text(
        (430, 520),
        "\n".join([f"{i + 1}. {item}" for i, item in enumerate(directions)]).strip(),
        (61, 61, 70),
        font=fonts["body"],
    )
    return bg_color
