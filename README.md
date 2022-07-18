---
title: Chef Transformer
emoji: 🍲
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.1.0
app_file: app.py
pinned: false
---

# Chef Transformer (T5) 
> This is part of the [Flax/Jax Community Week](https://discuss.huggingface.co/t/recipe-generation-model/7475), organized by [HuggingFace](https://huggingface.co/) and TPU usage sponsored by Google.

Want to give it a try? Then what's the wait, head over to the demo [here](https://share.streamlit.io/chef-transformer/chef-transformer/main/app.py).


## Team Members
- Mehrdad Farahani ([m3hrdadfi](https://huggingface.co/m3hrdadfi))
- Kartik Godawat ([dk-crazydiv](https://huggingface.co/dk-crazydiv))
- Haswanth Aekula ([hassiahk](https://huggingface.co/hassiahk))
- Deepak Pandian ([rays2pix](https://huggingface.co/rays2pix))
- Nicholas Broad ([nbroad](https://huggingface.co/nbroad))

## Dataset

[RecipeNLG: A Cooking Recipes Dataset for Semi-Structured Text Generation](https://recipenlg.cs.put.poznan.pl/). This dataset contains **2,231,142** cooking recipes (>2 millions) with size of **2.14 GB**. It's processed in more careful way.

### Example

```json
{
    "NER": [
        "oyster crackers",
        "salad dressing",
        "lemon pepper",
        "dill weed",
        "garlic powder",
        "salad oil"
    ],
    "directions": [
        "Combine salad dressing mix and oil.",
        "Add dill weed, garlic powder and lemon pepper.",
        "Pour over crackers; stir to coat.",
        "Place in warm oven.",
        "Use very low temperature for 15 to 20 minutes."
    ],
    "ingredients": [
        "12 to 16 oz. plain oyster crackers",
        "1 pkg. Hidden Valley Ranch salad dressing mix",
        "1/4 tsp. lemon pepper",
        "1/2 to 1 tsp. dill weed",
        "1/4 tsp. garlic powder",
        "3/4 to 1 c. salad oil"
    ],
    "link": "www.cookbooks.com/Recipe-Details.aspx?id=648947",
    "source": "Gathered",
    "title": "Hidden Valley Ranch Oyster Crackers"
}
```

## How To Use

```bash
# Installing requirements
pip install transformers
```

```python
from transformers import FlaxAutoModelForSeq2SeqLM
from transformers import AutoTokenizer

MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH, use_fast=True)
model = FlaxAutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

prefix = "items: "
# generation_kwargs = {
#     "max_length": 512,
#     "min_length": 64,
#     "no_repeat_ngram_size": 3,
#     "early_stopping": True,
#     "num_beams": 5,
#     "length_penalty": 1.5,
# }
generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "no_repeat_ngram_size": 3,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95
}


special_tokens = tokenizer.all_special_tokens
tokens_map = {
    "<sep>": "--",
    "<section>": "\n"
}
def skip_special_tokens(text, special_tokens):
    for token in special_tokens:
        text = text.replace(token, "")

    return text

def target_postprocessing(texts, special_tokens):
    if not isinstance(texts, list):
        texts = [texts]
    
    new_texts = []
    for text in texts:
        text = skip_special_tokens(text, special_tokens)

        for k, v in tokens_map.items():
            text = text.replace(k, v)

        new_texts.append(text)

    return new_texts

def generation_function(texts):
    _inputs = texts if isinstance(texts, list) else [texts]
    inputs = [prefix + inp for inp in _inputs]
    inputs = tokenizer(
        inputs, 
        max_length=256, 
        padding="max_length", 
        truncation=True, 
        return_tensors="jax"
    )

    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask

    output_ids = model.generate(
        input_ids=input_ids, 
        attention_mask=attention_mask,
        **generation_kwargs
    )
    generated = output_ids.sequences
    generated_recipe = target_postprocessing(
        tokenizer.batch_decode(generated, skip_special_tokens=False),
        special_tokens
    )
    return generated_recipe
```

```python
items = [
    "macaroni, butter, salt, bacon, milk, flour, pepper, cream corn",
    "provolone cheese, bacon, bread, ginger"
]
generated = generation_function(items)
for text in generated:
    sections = text.split("\n")
    for section in sections:
        section = section.strip()
        if section.startswith("title:"):
            section = section.replace("title:", "")
            headline = "TITLE"
        elif section.startswith("ingredients:"):
            section = section.replace("ingredients:", "")
            headline = "INGREDIENTS"
        elif section.startswith("directions:"):
            section = section.replace("directions:", "")
            headline = "DIRECTIONS"
        
        if headline == "TITLE":
            print(f"[{headline}]: {section.strip().capitalize()}")
        else:
            section_info = [f"  - {i+1}: {info.strip().capitalize()}" for i, info in enumerate(section.split("--"))]
            print(f"[{headline}]:")
            print("\n".join(section_info))

    print("-" * 130)
```

Output:
```text
[TITLE]: Macaroni and corn
[INGREDIENTS]:
  - 1: 2 c. macaroni
  - 2: 2 tbsp. butter
  - 3: 1 tsp. salt
  - 4: 4 slices bacon
  - 5: 2 c. milk
  - 6: 2 tbsp. flour
  - 7: 1/4 tsp. pepper
  - 8: 1 can cream corn
[DIRECTIONS]:
  - 1: Cook macaroni in boiling salted water until tender.
  - 2: Drain.
  - 3: Melt butter in saucepan.
  - 4: Blend in flour, salt and pepper.
  - 5: Add milk all at once.
  - 6: Cook and stir until thickened and bubbly.
  - 7: Stir in corn and bacon.
  - 8: Pour over macaroni and mix well.
--------------------------------------------------------------------------------------------------------------------------------
[TITLE]: Grilled provolone and bacon sandwich
[INGREDIENTS]:
  - 1: 2 slices provolone cheese
  - 2: 2 slices bacon
  - 3: 2 slices sourdough bread
  - 4: 2 slices pickled ginger
[DIRECTIONS]:
  - 1: Place a slice of provolone cheese on one slice of bread.
  - 2: Top with a slice of bacon.
  - 3: Top with a slice of pickled ginger.
  - 4: Top with the other slice of bread.
  - 5: Heat a skillet over medium heat.
  - 6: Place the sandwich in the skillet and cook until the cheese is melted and the bread is golden brown.
--------------------------------------------------------------------------------------------------------------------------------
```

## Evaluation
...

### Result
Since the test set is not available, we will evaluate the model based on a shared test set. This test set consists of 5% of the whole test (*= 5,000 records*), 
and we will generate five recipes for each input(*= 25,000 records*). 
The following table summarizes the scores obtained by the **Chef Transformer** and **RecipeNLG** as our baseline.

|                                       Model                                      |    COSIM   |     WER    |   ROUGE-2  |    BLEU    |    GLEU    |   METEOR   |
|:--------------------------------------------------------------------------------:|:----------:|:----------:|:----------:|:----------:|:----------:|:----------:|
|                [RecipeNLG](https://huggingface.co/mbien/recipenlg)               |   0.5723   |   1.2125   |   0.1354   |   0.1164   |   0.1503   |   0.2309   |
| [Chef Transformer](https://huggingface.co/flax-community/t5-recipe-generation) * | **0.7282** | **0.7613** | **0.2470** | **0.3245** | **0.2624** | **0.4150** |

*From the 5 generated recipes corresponding to each NER (food items), only the highest score was taken into account in the WER, COSIM, and ROUGE metrics. At the same time, BLEU, GLEU, Meteor were designed to have many possible references.*

## Streamlit demo

```bash
streamlit run app.py
```

## Looking to contribute?
Then follow the steps mentioned in this [contributing guide](CONTRIBUTING.md) and you are good to go.

## Copyright

Special thanks to those who provided these fantastic materials.
- [Anatomy](https://www.flaticon.com/free-icon)
- [Chef Hat](https://www.vecteezy.com/members/jellyfishwater)
- [Moira Nazzari](https://pixabay.com/photos/food-dessert-cake-eggs-butter-3048440/)
- [Instagram Post](https://www.freepik.com/free-psd/recipes-ad-social-media-post-template_11520617.htm)
