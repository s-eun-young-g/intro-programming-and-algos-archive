"""
6.101 Lab:
Recipes
"""

import pickle
import sys

# import typing # optional import
# import pprint # optional import

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary mapping each atomic food name to its cost.

    Initialize an empty dictionary costs.
    Iterate over each entry in recipes_db.
    If the entry is of type "atomic", extract the food name and its cost.
    Add the food name and cost to the costs dictionary.
    Return the costs dictionary.

    Arguments:
    Recipes databse

    Returns:
    A dictionary with food names as keys and their costs as values of all
    atomic food items in the database
    """
    # initialize costs dictionary
    costs = {}
    for entry in recipes_db:
        if entry[0] == "atomic":  # if item is atomic, add
            costs[entry[1]] = entry[2]

    return costs


def compound_ingredient_possibilities(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary that maps each compound food name to a
    list of all the ingredient lists associated with that name.

    Initialize an empty dictionary possibilities.
    Iterate over each entry in recipes_db.
    If the entry is of type "compound", extract the food name and its ingredient list.
    Add the ingredient list to the possibilities dictionary under the corresponding food name.
    Return the possibilities dictionary.


    Arguments:
    Recipes database

    Returns:
    A dictionary with food names as keys and a list of lists containing ingredients
    as tuples of (food name, quantity) as values. Example:
    {chili: [[(cornbread, 3), (beans, 10), (tomato, 1)], [(meat, 4), (peppers, 5)]]}
    """
    possibilities = {}
    for entry in recipes_db:
        if entry[0] == "compound":
            food_name = entry[1]
            ingredient_list = entry[2]  # list of tuples (ingredient_name, quantity)
            if food_name not in possibilities:
                possibilities[food_name] = []
            possibilities[food_name].append(ingredient_list)
    return possibilities


def lowest_cost(recipes_db, food_name, forbidden_items=None):
    """
    Given a recipes database and the name of a food (str), return the lowest
    cost of a full recipe for the given food item or None if there is no way
    to make the food_item.

    Arguments:
    Recipes databse
    Name of a food for which the cost of the lowest recipe is to be found
    Optionally: forbidden items—foods to explicitly exclude when looking through
    recipes

    Returns:
    Cost of the lowest-cost recipe variation for the input food
    """
    # initialize forbidden items as a set (if they exist)
    if forbidden_items is None:
        forbidden_items = set()
    else:
        forbidden_items = set(forbidden_items)

    atomic_costs = get_atomic_excluding_forbidden(forbidden_items, recipes_db)

    compound_possibilities = get_compound_excluding_forbidden(
        forbidden_items, recipes_db
    )

    completed = {}  # memoization

    def recursive_helper(food):
        # edge case: check if food is forbidden
        if food in forbidden_items:
            completed[food] = None
            return None
        # base case 1: food has been computed already
        if food in completed:
            return completed[food]
        # base case 2: food is atomic
        if food in atomic_costs:
            cost = atomic_costs[food]
            completed[food] = cost
            return cost
        # recursive case: food is compound
        elif food in compound_possibilities:
            min_cost = None
            for variant_recipe in compound_possibilities[food]:
                total_cost = 0
                check = True  # make sure all items exist
                for ingredient, quantity in variant_recipe:
                    # check if ingredient exists in the database
                    if (
                        ingredient not in atomic_costs
                        and ingredient not in compound_possibilities
                    ):
                        check = False
                        break
                    # recursive call - recursively compute cost of each ingredient
                    # in potentially nested recipes
                    ingredient_cost = recursive_helper(ingredient)
                    if ingredient_cost is None:
                        check = False
                        break
                    total_cost += ingredient_cost * quantity
                if check and (min_cost is None or total_cost < min_cost):
                    min_cost = total_cost
            completed[food] = min_cost
            return min_cost
        else:
            # food item is not in the database
            completed[food] = None
            return None

    return recursive_helper(food_name)


def scaled_recipe(recipe_dict, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.

    Arguments:
    Recipe dictionary
    n: number to scale entire recipe by

    Returns:
    A new, scaled recipe dictionary (does not modify input)
    """
    scaled = {}
    for ingredient in recipe_dict:
        scaled[ingredient] = recipe_dict[ingredient] * n
    return scaled


def add_recipes(recipe_dicts):
    """
    Given a list of recipe dictionaries that map food items to quantities,
    return a new dictionary that maps each ingredient name
    to the sum of its quantities across the given recipe dictionaries.

    For example,
        add_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}

    Arguments:
    A list of recipe dictionaries

    Returns:
    A single recipe dictionary that has combined all input recipes
    (including adding same ingredients in different recipes together)
    """
    added_recipes = {}
    for recipe in recipe_dicts:  # iterate through recipes in list
        for item in recipe:
            if item not in added_recipes:  # create entry for each food item
                added_recipes[item] = recipe[item]
            else:
                added_recipes[item] += recipe[item]  # update quantity
    return added_recipes


def cheapest_flat_recipe(recipes_db, food_name, forbidden_items=None):
    """
    Given a recipes database and the name of a food (str), return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.

    Arguments:
    Recipe database
    Name of food for which function should find cheapest recipe variation
    Optionally: forbidden foods to be excluded when looking through recipes

    Returns:
    The recipe dictionary for the cheapest recipe for input food
    """
    # initialize forbidden items (if they exist)
    if forbidden_items is None:
        forbidden_items = set()
    else:
        forbidden_items = set(forbidden_items)

    atomic_costs = get_atomic_excluding_forbidden(forbidden_items, recipes_db)

    compound_possibilities = get_compound_excluding_forbidden(
        forbidden_items, recipes_db
    )

    completed = {}

    # helper function that calculates the cost of a flat recipe
    def recipe_cost(variant_recipe):
        total_cost = 0
        for ingredient, quantity in variant_recipe.items():
            if ingredient in atomic_costs:
                total_cost += atomic_costs[ingredient] * quantity
            else:
                # if ingredient is not atomic
                return None
        return total_cost

    # recursive helper function
    def recursive_helper(food):
        # edge case: check if the food itself is forbidden
        if food in forbidden_items:
            completed[food] = None
            return None
        # base case 1: food is already in completed
        if food in completed:
            return completed[food]
        # base case 2: food is atomic
        if food in atomic_costs:
            recipe = {food: 1}
            completed[food] = recipe
            return recipe
        # recursive case: food is compound
        elif food in compound_possibilities:
            min_cost = None
            min_recipe = None
            for variant_recipe in compound_possibilities[food]:
                total_recipe = {}
                check = True  # check for edge cases
                for ingredient, quantity in variant_recipe:
                    # recursive call yippee
                    # recursively get cheapest recipe for cheapest recipe for each
                    # potentially nested ingredient in the recipe
                    ingredient_recipe = recursive_helper(ingredient)
                    if ingredient_recipe is None:
                        check = False
                        break
                    # scale recipe
                    scaled_ingredient_recipe = scaled_recipe(
                        ingredient_recipe, quantity
                    )
                    # get full recipe
                    total_recipe = add_recipes([total_recipe, scaled_ingredient_recipe])
                if check:
                    # obtain cost of current complete recipe
                    total_cost = recipe_cost(total_recipe)
                    if total_cost is not None and (
                        min_cost is None or total_cost < min_cost
                    ):
                        min_cost = total_cost  # check if current recipe has min cost
                        min_recipe = total_recipe
            completed[food] = min_recipe
            return min_recipe
        else:
            # food item is not in the database or is forbidden
            completed[food] = None
            return None

    return recursive_helper(food_name)


def combine_recipes(nested_recipes):
    """
    Given a list of lists of recipe dictionaries, where each inner list
    represents all the recipes for a certain ingredient, compute and return a
    list of recipe dictionaries that represent all the possible combinations of
    ingredient recipes.

    Arguments:
    A list of lists of recipe dictionaries

    Returns:
    A list of recipe dictionaries containing all combinations
    of recipes for each (nested) ingredient
    """
    # initialize the list to hold the combined recipes
    combined_recipes = []

    # check edge case
    if not nested_recipes:
        return []

    # helper function to generate all combinations
    def recursive_combinations(index, current_recipe):
        # base case
        # if index = length, means all ingredients have been iterated through
        if index == len(nested_recipes):
            combined_recipes.append(current_recipe)
        else:
            # iterate over each recipe in that exist for the current ingredient
            for recipe in nested_recipes[index]:
                new_recipe = add_recipes(
                    [current_recipe, recipe]
                )  # call helper function
                # recursive call for next index
                recursive_combinations(index + 1, new_recipe)

    recursive_combinations(0, {})

    return combined_recipes


def all_flat_recipes(recipes_db, food_name, forbidden_items=None):
    """
    Given a recipes database, the name of a food (str), produce a list (in any
    order) of all possible flat recipe dictionaries for that category.

    Returns an empty list if there are no possible recipes

    Arguments:
    Recipes database
    Name of food for which function should find all flattened recipes
    Optionally: forbidden foods to be excluded when looking through recipes

    Returns:
    List of all possible flat recipe dictionaries for input food
    """
    # initialize forbidden items (if they exist)
    if forbidden_items is None:
        forbidden_items = set()
    else:
        forbidden_items = set(forbidden_items)

    atomic_costs = get_atomic_excluding_forbidden(forbidden_items, recipes_db)

    compound_possibilities = get_compound_excluding_forbidden(
        forbidden_items, recipes_db
    )

    completed = {}

    # recursive helper function
    def recursive_helper(food):
        # edge case: check if the food itself is forbidden
        if food in forbidden_items:
            completed[food] = []
            return []
        # base case 1: food is already in completed
        if food in completed:
            return completed[food]
        # Base case 2: food is atomic
        if food in atomic_costs:
            completed[food] = [{food: 1}]
            return completed[food]
        # recursive case: if the food is compound
        elif food in compound_possibilities:
            all_recipes = []
            for variant_recipe in compound_possibilities[food]:
                possible_ingredient_recipes = []
                check = True  # check edge cases
                for ingredient, quantity in variant_recipe:
                    # recursive call woohoo
                    # recursively get all possible recipes for
                    # potentially nested ingredients
                    ingredient_recipes = recursive_helper(ingredient)
                    if not ingredient_recipes:
                        check = False
                        break
                    # scaling recipes
                    scaled_recipes = [
                        scaled_recipe(var, quantity) for var in ingredient_recipes
                    ]
                    possible_ingredient_recipes.append(scaled_recipes)
                if check:
                    # combine recipes
                    combined = combine_recipes(possible_ingredient_recipes)
                    all_recipes.extend(combined)
            completed[food] = all_recipes
            return all_recipes
        else:
            # food item is not in the database or is forbidden
            completed[food] = []
            return []

    return recursive_helper(food_name)


def get_atomic_excluding_forbidden(forbidden_items, recipes_db):
    """
    Helper function that returns a list of atomic ingredients
    excluding forbidden ingredients
    """
    # initialize atomic costs and compound possibilities dictionaries
    # excluding forbidden items
    atomic_costs = {
        food: cost
        for food, cost in atomic_ingredient_costs(recipes_db).items()
        if food not in forbidden_items  # only add food if not forbidden
    }
    return atomic_costs


def get_compound_excluding_forbidden(forbidden_items, recipes_db):
    """
    Helper function that returns a list of compound possibilities excluding
    forbidden ingredients
    """
    compound_possibilities = {}
    for food, recipes in compound_ingredient_possibilities(recipes_db).items():
        if (
            food not in forbidden_items
        ):  # add to "valid" list if food itself not forbidden
            valid_recipes = []
            for recipe in recipes:
                # exclude recipes that contain forbidden items
                check = True
                for ingredient, _ in recipe:
                    if ingredient in forbidden_items:
                        check = False
                if check:
                    valid_recipes.append(recipe)
            if valid_recipes:
                compound_possibilities[food] = valid_recipes
    return compound_possibilities


"""
if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes_db = pickle.load(f)
        costs_dict = atomic_ingredient_costs(example_recipes_db)
        total = 0
        for food in costs_dict:
            total += costs_dict[food]
        # print(total)
        compounds_dict = compound_ingredient_possibilities(example_recipes_db)
        print(compounds_dict)
        variations_counter = 0
        for food in compounds_dict:
            if len(compounds_dict[food]) > 1:
                variations_counter += 1
        print(variations_counter)
        print(add_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}]))
        soup = {"carrots": 5, "celery": 3, "broth": 2, "noodles": 1, "chicken": 3, "salt": 10}
        scaled_soup = scaled_recipe(soup, 3)
        print(scaled_soup)
        carrot_cake = {"carrots": 5, "flour": 8, "sugar": 10, "oil": 5, "eggs": 4, "salt": 3}
        bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
        recipe_dicts = [soup, carrot_cake, bread]
        combined_recipe = add_recipes(recipe_dicts)
        print(combined_recipe)
        dairy_recipes_db = [
        ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
        ('compound', 'cheese', [('milk', 1), ('time', 1)]),
        ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
        ('atomic', 'milking stool', 5),
        ('atomic', 'cutting-edge laboratory', 1000),
        ('atomic', 'time', 10000),
        ('atomic', 'cow', 100),
        ]
        dairy_recipes_db2 = [
        ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
        ('compound', 'cheese', [('milk', 1), ('time', 1)]),
        ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
        ('atomic', 'milking stool', 5),
        ('atomic', 'cutting-edge laboratory', 1000),
        ('atomic', 'time', 10000),
        ]
        print(lowest_cost(dairy_recipes_db2, 'cheese'))
        cookie_recipes_db = [
        ('compound', 'cookie sandwich', [('cookie', 2), ('ice cream scoop', 3)]),
        ('compound', 'cookie', [('chocolate chips', 3)]),
        ('compound', 'cookie', [('sugar', 10)]),
        ('atomic', 'chocolate chips', 200),
        ('atomic', 'sugar', 5),
        ('compound', 'ice cream scoop', [('vanilla ice cream', 1)]),
        ('compound', 'ice cream scoop', [('chocolate ice cream', 1)]),
        ('atomic', 'vanilla ice cream', 20),
        ('atomic', 'chocolate ice cream', 30),
        ]
        print(lowest_cost(cookie_recipes_db, 'cookie sandwich'))

"""
