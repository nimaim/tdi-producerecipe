from dataclasses import dataclass, field
import re

@dataclass
class RecipeItem:
    """Class for keeping track of a recipe item on a specific website."""
    r: dict
    name: str = field(default=None, init=False)
    description: str = field(default=None, init=False)
    author: str = field(default=None, init=False)
    image: str = field(default=None, init=False)
    servings: str = field(default=None, init=False)
    ingredients: str = field(default=None, init=False)
    instructions: str = field(default=None, init=False)
    nutrition: str = field(default=None, init=False)

    def fill_values(self) -> bool:
        ### Type 1

        # TODO: FIX
        if isinstance(self.r, list):
            return False

        if '@graph' not in self.r.keys():
            try:
                self.name = self.r['name']
                self.description = self.r['description']
                self.author = self.r['author']['name']
                self.image = self.r['image']

                for ingredient in self.r['recipeIngredient']:
                    fixed_ingredient = re.sub(r'\s+', ' ', ingredient.strip())
                    self.ingredients = fixed_ingredient

                for step in self.r['recipeInstructions']:
                    fixed_step = re.sub(r'\s+', ' ', step.strip())
                    self.instructions = fixed_step

                return True
            except:
                return False


        else:
            try:
                for d in self.r['@graph']:  # dict
                    if 'Recipe' in d['@type']:  # list
                        self.name = d['name']
                        self.description = d['description']
                        self.author = d['author']['name']
                        self.image = d['image'][0]
                        print(d['name'])
                        print(d['description'])
                        print(d['author']['name'])
                        print(d['image'][0])
                        self.servings = d['recipeYield'][0]
                        print(d['recipeYield'][0], 'servings')
                        self.servings = d['recipeIngredient']
                        print(*d['recipeIngredient'], sep='\n')

                        for step in d['recipeInstructions']:
                            if 'text' in step.keys():
                                if not self.instructions:
                                    self.instructions = step['text']
                                else:
                                    self.instructions += '\n' + step['text'] + '\n'
                                print(step['text'])

                        self.nutrition = d['nutrition']

                        return True
            except:
                return False

                    # for n in d['nutrition']:
                    #     if '@' not in n:
                    #         if not self.nutrition:
                    #             self.nutrition = f'{n}: {d["nutrition"][n]}'
                    #         else:
                    #             self.nutrition += '\n' + f'{n}: {d["nutrition"][n]}'
                    #         print(f'{n}: {d["nutrition"][n]}')


if __name__ == '__main__':
    test = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Organization",
            "@id": "https://minimalistbaker.com/#organization",
            "name": "Minimalist Baker",
            "url": "https://minimalistbaker.com/",
            "sameAs": [
                "https://instagram.com/minimalistbaker/",
                "https://www.pinterest.com/minimalistbaker/",
                "https://www.youtube.com/c/Minimalistbaker",
                "https://www.facebook.com/MinimalistBaker",
                "https://twitter.com/minimalistbaker"
            ],
            "logo": {
                "@type": "ImageObject",
                "inLanguage": "en-US",
                "@id": "https://minimalistbaker.com/#/schema/logo/image/",
                "url": "https://minimalistbaker.com/wp-content/uploads/2015/04/logo@2x.png",
                "contentUrl": "https://minimalistbaker.com/wp-content/uploads/2015/04/logo@2x.png",
                "width": 660,
                "height": 226,
                "caption": "Minimalist Baker"
            },
            "image": {
                "@id": "https://minimalistbaker.com/#/schema/logo/image/"
            }
        },
        {
            "@type": "WebSite",
            "@id": "https://minimalistbaker.com/#website",
            "url": "https://minimalistbaker.com/",
            "name": "Minimalist Baker",
            "description": "Simple Food, Simply Delicious",
            "publisher": {
                "@id": "https://minimalistbaker.com/#organization"
            },
            "potentialAction": [
                {
                    "@type": "SearchAction",
                    "target": {
                        "@type": "EntryPoint",
                        "urlTemplate": "https://minimalistbaker.com/?s={search_term_string}"
                    },
                    "query-input": "required name=search_term_string"
                }
            ],
            "inLanguage": "en-US"
        },
        {
            "@type": "ImageObject",
            "inLanguage": "en-US",
            "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#primaryimage",
            "url": "https://minimalistbaker.com/wp-content/uploads/2017/02/CREAMY-Roasted-Red-Pepper-Tomato-Soup-Simple-ingredients-BIG-flavor-vegan-glutenfree-plantbased-soup-minimalistbaker-tomato.jpg",
            "contentUrl": "https://minimalistbaker.com/wp-content/uploads/2017/02/CREAMY-Roasted-Red-Pepper-Tomato-Soup-Simple-ingredients-BIG-flavor-vegan-glutenfree-plantbased-soup-minimalistbaker-tomato.jpg",
            "width": 1456,
            "height": 2184,
            "caption": "A bowl of Creamy Vegan Roasted Red Pepper Tomato Soup with a coconut milk swirl"
        },
        {
            "@type": "WebPage",
            "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#webpage",
            "url": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/",
            "name": "Creamy Roasted Red Pepper Tomato Soup | Minimalist Baker Recipes",
            "isPartOf": {
                "@id": "https://minimalistbaker.com/#website"
            },
            "primaryImageOfPage": {
                "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#primaryimage"
            },
            "datePublished": "2017-04-01T12:00:10+00:00",
            "dateModified": "2022-01-24T13:08:58+00:00",
            "description": "Incredibly creamy roasted red pepper and tomato soup! Savory, flavorful, and ready in just 30 minutes. The perfect side to sandwiches, salads, and more!",
            "breadcrumb": {
                "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#breadcrumb"
            },
            "inLanguage": "en-US",
            "potentialAction": [
                {
                    "@type": "ReadAction",
                    "target": [
                        "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/"
                    ]
                }
            ]
        },
        {
            "@type": "BreadcrumbList",
            "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://minimalistbaker.com/"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Creamy Roasted Red Pepper Tomato Soup"
                }
            ]
        },
        {
            "@type": "Article",
            "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#article",
            "isPartOf": {
                "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#webpage"
            },
            "author": {
                "@id": "https://minimalistbaker.com/#/schema/person/ed5ce1b1862e6237956babab32d2dc56"
            },
            "headline": "Creamy Roasted Red Pepper Tomato Soup",
            "datePublished": "2017-04-01T12:00:10+00:00",
            "dateModified": "2022-01-24T13:08:58+00:00",
            "wordCount": 720,
            "commentCount": 245,
            "publisher": {
                "@id": "https://minimalistbaker.com/#organization"
            },
            "image": {
                "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#primaryimage"
            },
            "thumbnailUrl": "https://minimalistbaker.com/wp-content/uploads/2017/02/CREAMY-Roasted-Red-Pepper-Tomato-Soup-Simple-ingredients-BIG-flavor-vegan-glutenfree-plantbased-soup-minimalistbaker-tomato.jpg",
            "keywords": [
                "basil",
                "bell peppers",
                "coconut",
                "coconut milk",
                "coconut sugar",
                "dill",
                "garlic",
                "red pepper",
                "soup",
                "tomato paste",
                "tomatoes"
            ],
            "articleSection": [
                "10 ingredients or less",
                "30 minutes or less",
                "Appetizer",
                "Dairy-Free",
                "Dinner",
                "Egg-Free",
                "Fall",
                "Gluten Free",
                "Grain-Free",
                "Lunch",
                "Nut-Free",
                "Oil-Free",
                "Recipes",
                "Refined Sugar-Free",
                "Savory",
                "Sides",
                "Soup",
                "Soy-Free",
                "Spring",
                "Summer",
                "Vegan",
                "Vegetarian",
                "Winter"
            ],
            "inLanguage": "en-US",
            "potentialAction": [
                {
                    "@type": "CommentAction",
                    "name": "Comment",
                    "target": [
                        "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#respond"
                    ]
                }
            ]
        },
        {
            "@type": "Person",
            "@id": "https://minimalistbaker.com/#/schema/person/ed5ce1b1862e6237956babab32d2dc56",
            "name": "Dana @ Minimalist Baker",
            "image": {
                "@type": "ImageObject",
                "inLanguage": "en-US",
                "@id": "https://minimalistbaker.com/#/schema/person/image/",
                "url": "https://secure.gravatar.com/avatar/83d23696ef5f7da8f411d78630a49041?s=96&d=mm&r=g",
                "contentUrl": "https://secure.gravatar.com/avatar/83d23696ef5f7da8f411d78630a49041?s=96&d=mm&r=g",
                "caption": "Dana @ Minimalist Baker"
            },
            "description": "Hi, I'm Dana! I am a food stylist, photographer, creator of the Food Photography School, and author of the 31 Meals Cookbook and Everyday Cooking. Find me on Twitter, Instagram, and Pinterest."
        },
        {
            "@context": "http://schema.org/",
            "@type": "Recipe",
            "name": "Creamy Roasted Red Pepper Tomato Soup",
            "author": {
                "@type": "Person",
                "name": "Minimalist Baker"
            },
            "description": "Creamy roasted red pepper tomato soup made in 30 minutes! Savory, flavorful, and so easy to make. The perfect side to sandwiches, salads, and more!",
            "datePublished": "2017-04-01T05:00:10+00:00",
            "image": [
                "https://minimalistbaker.com/wp-content/uploads/2017/02/Creamy-Red-Pepper-Tomato-Soup-image-SQUARE.jpg"
            ],
            "video": {
                "name": "Creamy Roasted Red Pepper Tomato Soup | Minimalist Baker Recipes",
                "description": "Creamy roasted red pepper tomato soup made in 30 minutes! Savory, flavorful, and so easy to make. The perfect side to sandwiches, salads, and more!\n\nFull Recipe: https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/\n \nFOLLOW US!\nBlog: http://minimalistbaker.com/\nInstagram: https://instagram.com/minimalistbaker/\nTwitter: https://twitter.com/minimalistbaker\nFacebook: https://www.facebook.com/MinimalistBaker",
                "uploadDate": "2022-01-23T09:00:08+00:00",
                "duration": "PT50S",
                "thumbnailUrl": "https://i.ytimg.com/vi/FGt8JSXNwx4/hqdefault.jpg",
                "contentUrl": "https://www.youtube.com/watch?v=FGt8JSXNwx4",
                "embedUrl": "https://www.youtube.com/embed/FGt8JSXNwx4?feature=oembed",
                "@type": "VideoObject"
            },
            "recipeYield": [
                "4"
            ],
            "prepTime": "PT5M",
            "cookTime": "PT25M",
            "totalTime": "PT30M",
            "recipeIngredient": [
                "2 large red bell peppers  ((left whole))",
                "1 28-ounce can crushed or peeled tomatoes in juices",
                "1 6-ounce can tomato paste",
                "1 cup water  ((sub up to half with extra coconut milk for creamier soup))",
                "1 14-ounce can light coconut milk  ((use full fat for creamier soup))",
                "1 1/2 Tbsp dried dill ((or sub 3 Tbsp (5 g) minced fresh dill per 1 1/2 Tbsp dried))",
                "1 Tbsp garlic powder",
                "1 tsp dried basil  ((or sub 2 tsp minced fresh basil per 1 tsp dried))",
                "1/2 tsp each sea salt and black pepper",
                "3-4 Tbsp coconut sugar  ((or stevia to taste))",
                "1 pinch red pepper flake ((optional // for heat))",
                "Croutons",
                "Sliced tomatoes",
                "Fresh dill",
                "Full-fat coconut milk",
                "Crispy baked chickpeas",
                "Nutritional yeast or Vegan Parmesan Cheese",
                "Black pepper"
            ],
            "recipeInstructions": [
                {
                    "@type": "HowToStep",
                    "text": "Roast red peppers in a 500 degree F (260 C) oven (on a foil-lined baking sheet) or over an open flame on a grill or gas stovetop until tender and charred on all sides - about 10-15 minutes in the oven, or 5 minutes over an open flame. Then wrap in foil to steam for a few minutes.",
                    "name": "Roast red peppers in a 500 degree F (260 C) oven (on a foil-lined baking sheet) or over an open flame on a grill or gas stovetop until tender and charred on all sides - about 10-15 minutes in the oven, or 5 minutes over an open flame. Then wrap in foil to steam for a few minutes.",
                    "url": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#wprm-recipe-34860-step-0-0"
                },
                {
                    "@type": "HowToStep",
                    "text": "In the meantime, add remaining soup ingredients to large pot and bring to a simmer. Then unwrap red peppers, let cool to the touch, and remove charred outer skin seeds and stems. Add to soup (see photo).",
                    "name": "In the meantime, add remaining soup ingredients to large pot and bring to a simmer. Then unwrap red peppers, let cool to the touch, and remove charred outer skin seeds and stems. Add to soup (see photo).",
                    "url": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#wprm-recipe-34860-step-0-1"
                },
                {
                    "@type": "HowToStep",
                    "text": "Transfer to blender or use immersion blender to pur\u00e9e soup. Then transfer back to saucepan/pot and bring to a simmer over medium-low heat. Taste and adjust seasonings as needed, adding more coconut sugar or stevia to sweeten, red pepper flake for heat, basil or dill for earthiness, garlic powder for overall flavor, or salt for saltiness. I added a bit more of each. Go for big flavor!",
                    "name": "Transfer to blender or use immersion blender to pur\u00e9e soup. Then transfer back to saucepan/pot and bring to a simmer over medium-low heat. Taste and adjust seasonings as needed, adding more coconut sugar or stevia to sweeten, red pepper flake for heat, basil or dill for earthiness, garlic powder for overall flavor, or salt for saltiness. I added a bit more of each. Go for big flavor!",
                    "url": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#wprm-recipe-34860-step-0-2"
                },
                {
                    "@type": "HowToStep",
                    "text": "Let simmer on low for at least 10 more minutes. The longer it simmers, the deeper the flavor develops.",
                    "name": "Let simmer on low for at least 10 more minutes. The longer it simmers, the deeper the flavor develops.",
                    "url": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#wprm-recipe-34860-step-0-3"
                },
                {
                    "@type": "HowToStep",
                    "text": "Serve as is or top with desired toppings, such as croutons, fresh dill or basil, tomatoes,&nbsp;crispy baked chickpeas, nutritional yeast or Vegan Parmesan Cheese, and/or black pepper.",
                    "name": "Serve as is or top with desired toppings, such as croutons, fresh dill or basil, tomatoes,&nbsp;crispy baked chickpeas, nutritional yeast or Vegan Parmesan Cheese, and/or black pepper.",
                    "url": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#wprm-recipe-34860-step-0-4"
                },
                {
                    "@type": "HowToStep",
                    "text": "Leftovers will keep covered in the refrigerator for 4-5 days or the freezer for 1 month.",
                    "name": "Leftovers will keep covered in the refrigerator for 4-5 days or the freezer for 1 month.",
                    "url": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#wprm-recipe-34860-step-0-5"
                }
            ],
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.89",
                "ratingCount": "102"
            },
            "recipeCategory": [
                "Side",
                "Soup"
            ],
            "recipeCuisine": [
                "Gluten-Free",
                "Vegan"
            ],
            "keywords": "tomato soup",
            "nutrition": {
                "@type": "NutritionInformation",
                "servingSize": "1 serving",
                "calories": "161 kcal",
                "carbohydrateContent": "35.5 g",
                "proteinContent": "7.1 g",
                "fatContent": "0.4 g",
                "sodiumContent": "715 mg",
                "fiberContent": "8.8 g",
                "sugarContent": "25 g"
            },
            "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#recipe",
            "isPartOf": {
                "@id": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#article"
            },
            "mainEntityOfPage": "https://minimalistbaker.com/creamy-roasted-red-pepper-tomato-soup/#webpage"
        }
    ]
}
    test_recipe = RecipeItem(test)