import streamlit as st

import torch
from transformers import pipeline, set_seed
from transformers import AutoTokenizer

from PIL import (
    Image,
    ImageFont,
    ImageDraw
)
import requests

import os
import re
import random
import textwrap
from examples import EXAMPLES
import dummy
import meta
from utils import (
    remote_css,
    local_css,
    load_image_from_url,
    load_image_from_local,
    image_to_base64,
    pure_comma_separation
)


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
    directions = [textwrap.fill(item, 70).replace("\n", "\n   ") for item in directions]
    im_editable.text(
        (430, 520),
        "\n".join([f"{i + 1}. {item}" for i, item in enumerate(directions)]).strip(),
        (61, 61, 70),
        font=fonts["body"],
    )
    return bg_color


class TextGeneration:
    def __init__(self):
        self.debug = False
        self.dummy_outputs = dummy.recipes
        self.tokenizer = None
        self.generator = None
        self.api_ids = []
        self.api_keys = []
        self.api_test = 2
        self.task = "text2text-generation"
        self.model_name_or_path = "flax-community/t5-recipe-generation"
        self.color_frame = "#ffffff"
        self.main_frame = "asset/frame/recipe-bg.png"
        self.no_food = "asset/frame/no_food.png"
        self.logo_frame = "asset/frame/logo.png"
        self.chef_frames = {
            "scheherazade": "asset/frame/food-image-logo-bg-s.png",
            "giovanni": "asset/frame/food-image-logo-bg-g.png",
        }
        self.fonts = {
            "title": ImageFont.truetype("asset/fonts/Poppins-Bold.ttf", 70),
            "sub_title": ImageFont.truetype("asset/fonts/Poppins-Medium.ttf", 30),
            "body_bold": ImageFont.truetype("asset/fonts/Montserrat-Bold.ttf", 22),
            "body": ImageFont.truetype("asset/fonts/Montserrat-Regular.ttf", 18),

        }
        set_seed(42)

    def _skip_special_tokens_and_prettify(self, text):
        recipe_maps = {"<sep>": "--", "<section>": "\n"}
        recipe_map_pattern = "|".join(map(re.escape, recipe_maps.keys()))

        text = re.sub(
            recipe_map_pattern,
            lambda m: recipe_maps[m.group()],
            re.sub("|".join(self.tokenizer.all_special_tokens), "", text)
        )

        data = {"title": "", "ingredients": [], "directions": []}
        for section in text.split("\n"):
            section = section.strip()
            if section.startswith("title:"):
                data["title"] = " ".join(
                    [w.strip().capitalize() for w in section.replace("title:", "").strip().split() if w.strip()]
                )
            elif section.startswith("ingredients:"):
                data["ingredients"] = [s.strip() for s in section.replace("ingredients:", "").split('--')]
            elif section.startswith("directions:"):
                data["directions"] = [s.strip() for s in section.replace("directions:", "").split('--')]
            else:
                pass

        return data

    def load_pipeline(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        self.generator = pipeline(self.task, model=self.model_name_or_path, tokenizer=self.model_name_or_path)

    def load_api(self):
        app_ids = os.getenv("EDAMAM_APP_ID")
        app_ids = app_ids.split(",") if app_ids else []
        app_keys = os.getenv("EDAMAM_APP_KEY")
        app_keys = app_keys.split(",") if app_keys else []

        if len(app_ids) != len(app_keys):
            self.api_ids = []
            self.api_keys = []

        self.api_ids = app_ids
        self.api_keys = app_keys

    def load(self):
        self.load_api()
        if not self.debug:
            self.load_pipeline()

    def prepare_frame(self, recipe, chef_name):
        frame_path = self.chef_frames[chef_name.lower()]
        food_logo = generate_food_with_logo_image(frame_path, self.logo_frame, recipe["image"])
        frame = generate_recipe_image(
            recipe,
            self.main_frame,
            food_logo,
            self.fonts,
            bg_color="#ffffff"
        )
        return frame

    def generate(self, items, generation_kwargs):
        recipe = self.dummy_outputs[random.randint(0, len(self.dummy_outputs) - 1)]

        if not self.debug:
            generation_kwargs["num_return_sequences"] = 1
            # generation_kwargs["return_full_text"] = False
            generation_kwargs["return_tensors"] = True
            generation_kwargs["return_text"] = False

            generated_ids = self.generator(
                items,
                **generation_kwargs,
            )[0]["generated_token_ids"]
            recipe = self.tokenizer.decode(generated_ids, skip_special_tokens=False)
            recipe = self._skip_special_tokens_and_prettify(recipe)

        if self.api_ids and self.api_keys and len(self.api_ids) == len(self.api_keys):
            test = 0
            for i in range(len(self.api_keys)):
                if test > self.api_test:
                    recipe["image"] = None
                    break
                image = generate_cook_image(recipe["title"].lower(), self.api_ids[i], self.api_keys[i])
                test += 1
                if image:
                    recipe["image"] = image
                    break
        else:
            recipe["image"] = None

        return recipe

    def generate_frame(self, recipe, chef_name):
        return self.prepare_frame(recipe, chef_name)


@st.cache(allow_output_mutation=True)
def load_text_generator():
    generator = TextGeneration()
    generator.load()
    return generator


chef_top = {
    "max_length": 512,
    "min_length": 64,
    "no_repeat_ngram_size": 3,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95,
    "num_return_sequences": 1
}
chef_beam = {
    "max_length": 512,
    "min_length": 64,
    "no_repeat_ngram_size": 3,
    "early_stopping": True,
    "num_beams": 5,
    "length_penalty": 1.5,
    "num_return_sequences": 1
}


def main():
    st.set_page_config(
        page_title="Chef Transformer",
        page_icon="🍲",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    generator = load_text_generator()
    # if hasattr(st, "session_state"):
    #     if 'get_random_frame' not in st.session_state:
    #         st.session_state.get_random_frame = generator.frames[0]
    # else:
    #     get_random_frame = generator.frames[0]

    local_css("asset/css/style.css")

    col1, col2 = st.beta_columns([4, 3])
    with col2:
        st.image(load_image_from_local("asset/images/chef-transformer-transparent.png"), width=300)
        st.markdown(meta.SIDEBAR_INFO, unsafe_allow_html=True)

        with st.beta_expander("Where did this story start?"):
            st.markdown(meta.STORY, unsafe_allow_html=True)

    with col1:
        st.markdown(meta.HEADER_INFO, unsafe_allow_html=True)

        st.markdown(meta.CHEF_INFO, unsafe_allow_html=True)
        chef = st.selectbox("Choose your chef", index=0, options=["Chef Scheherazade", "Chef Giovanni"])

        prompts = list(EXAMPLES.keys()) + ["Custom"]
        prompt = st.selectbox(
            'Examples (select from this list)',
            prompts,
            # index=len(prompts) - 1,
            index=0
        )

        if prompt == "Custom":
            prompt_box = ""
        else:
            prompt_box = EXAMPLES[prompt]

        items = st.text_area(
            'Insert your ingredients here (separated by `,`): ',
            pure_comma_separation(prompt_box, return_list=False),
        )
        items = pure_comma_separation(items, return_list=False)
        entered_items = st.empty()
        recipe_button = st.button('Get Recipe!')

    st.markdown(
        "<hr />",
        unsafe_allow_html=True
    )
    if recipe_button:
        # if hasattr(st, "session_state"):
        #     st.session_state.get_random_frame = generator.frames[random.randint(0, len(generator.frames)) - 1]
        # else:
        #     get_random_frame = generator.frames[random.randint(0, len(generator.frames)) - 1]

        entered_items.markdown("**Generate recipe for:** " + items)
        with st.spinner("Generating recipe..."):

            if not isinstance(items, str) or not len(items) > 1:
                entered_items.markdown(
                    f"**{chef}** would like to know what ingredients do you like to use in "
                    f"your food? "
                )
            else:
                gen_kw = chef_top if chef == "Chef Scheherazade" else chef_beam
                generated_recipe = generator.generate(items, gen_kw)

                title = generated_recipe["title"]
                food_image = generated_recipe["image"]
                food_image = load_image_from_url(food_image, rgba_mode=True, default_image=generator.no_food)
                food_image = image_to_base64(food_image)
                ingredients = generated_recipe["ingredients"]
                directions = [textwrap.fill(item, 70).replace("\n", "\n   ") for item in
                              generated_recipe["directions"]]
                generated_recipe["by"] = chef

                r1, r2 = st.beta_columns([3, 5])

                with r1:
                    # st.write(st.session_state.get_random_frame)
                    # if hasattr(st, "session_state"):
                    #     recipe_post = generator.generate_frame(generated_recipe, st.session_state.get_random_frame)
                    # else:
                    #     recipe_post = generator.generate_frame(generated_recipe, get_random_frame)

                    recipe_post = generator.generate_frame(generated_recipe, chef.split()[-1])

                    st.image(
                        recipe_post,
                        # width=500,
                        caption="Save image and share on your social media",
                        use_column_width="auto",
                        output_format="PNG"
                    )

                with r2:
                    st.markdown(
                        " ".join([
                            "<div class='r-text-recipe'>",
                            "<div class='food-title'>",
                            f"<img src='{food_image}' />",
                            f"<h2>{title}</h2>",
                            "</div>",
                            '<div class="divider"><div class="divider-mask"></div></div>',
                            "<h3>Ingredients</h3>",
                            "<ul class='ingredients-list'>",
                            " ".join([f'<li>{item}</li>' for item in ingredients]),
                            "</ul>",
                            "<h3>Directions</h3>",
                            "<ol class='ingredients-list'>",
                            " ".join([f'<li>{item}</li>' for item in directions]),
                            "</ol>",
                            "</div>"
                        ]),
                        unsafe_allow_html=True
                    )


if __name__ == '__main__':
    main()
