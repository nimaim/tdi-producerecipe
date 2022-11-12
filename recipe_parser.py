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
    pass
    # test_recipe = RecipeItem(test)
