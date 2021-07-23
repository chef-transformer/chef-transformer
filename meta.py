HEADER_INFO = """""".strip()
SIDEBAR_INFO = """
<div class="contributors font-body text-bold">
<a class="contributor comma" href="https://huggingface.co/m3hrdadfi">Mehrdad Farahani</a>
<a class="contributor comma" href="https://huggingface.co/dk-crazydiv">Kartik Godawat</a>
<a class="contributor comma" href="https://huggingface.co/hassiahk">Haswanth Aekula</a>
<a class="contributor comma" href="https://huggingface.co/rays2pix">Deepak Pandian</a>
<a class="contributor comma" href="https://huggingface.co/nbroad">Nicholas Broad</a>
</div>
"""
CHEF_INFO = """
<h2 class="font-title">Welcome to our lovely restaurant! </h2>
<p class="strong font-body">
<span class="d-block extra-info">(We are at your service with two of the best chefs in the world: Chef Scheherazade, 
Chef Giovanni. Scheherazade is known for being more creative whereas Giovanni is more meticulous.)</span>
</p>
""".strip()
PROMPT_BOX = "Add custom ingredients here (separated by `,`): "
STORY = """
<div class="story-box font-body">
<p>
Hello everyone 👋, I am <strong>Chef Transformer</strong>, 
the owner of this restaurant. I was made by a group of <a href="https://huggingface.co/flax-community/t5-recipe-generation#team-members">NLP Engineers</a> to train my two prodigy recipe creators: <strong>Chef Scheherazade</strong> and <strong>Chef Giovanni</strong>. 
Both of my students participated in my rigorous culinary program, <a href="https://huggingface.co/flax-community/t5-recipe-generation">T5 fine-tuning</a>, 
to learn how to prepare exquisite cuisines from a wide variety of ingredients. 
I've never been more proud of my students -- both can produce exceptional dishes but I regard Scheherazade as being <em>creative</em> while Giovanni is <em>meticulous</em>. 
If you give each of them the same ingredients, they'll usually come up with something different. <br /><br />
At the start of the program the chefs read cookbooks containing thousands of recipes of varying difficulties and from cultures all over the world. 
The NLP engineers helped guide the learning process so that the chefs could actually learn which ingredients work well together rather than just memorize recipes. 
I trained my chefs by asking them to generate a title, a list of ingredients (including amounts!), and a list of directions after giving them just a simple list of food items. 
</p>

<pre>[Inputs]
    {food items*: separated by comma}
     
[Targets]
    title: {TITLE} &lt;section>
    ingredients: {INGREDIENTS: separated by &lt;sep>} &lt;section>
    directions: {DIRECTIONS: separated by &lt;sep>}.
</pre>

<p>
  <em>In the cookbooks (a.k.a <a href="https://huggingface.co/datasets/recipe_nlg">dataset</a>), the food items were referred to as NER. </em>
</p>
<p>
In the span of a week, my chefs went from spitting out nonsense to creating masterpieces. 
Their learning rate was exceptionally high and each batch of recipes was better than the last. <br />
In their final exam, they achieved <a href="https://huggingface.co/flax-community/t5-recipe-generation#evaluation">high scores</a> 💯 in a 
standardized industry test and established this restaurant 🍲. Please tell your friends and family about us! 
We create each recipe with a smile on our faces 🤗 Everyone at the restaurant is grateful for the generous support of 
HuggingFace and Google for hosting Flax Community week. 
</p>

</div>
""".strip()