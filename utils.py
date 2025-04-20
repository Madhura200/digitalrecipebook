def get_recipe_by_id(recipes, recipe_id):
    """
    Find a recipe by its ID
    
    Args:
        recipes: List of recipe dictionaries
        recipe_id: The ID to search for
        
    Returns:
        The recipe dict if found, otherwise None
    """
    for recipe in recipes:
        if str(recipe.get('id')) == str(recipe_id):
            return recipe
    return None

def filter_recipes(recipes, search_query='', meal_type='', cuisine='', diet='', ingredients=None):
    """
    Filter recipes based on various criteria
    
    Args:
        recipes: List of recipe dictionaries
        search_query: Text to search for in recipe name
        meal_type: Specific meal type to filter by
        cuisine: Specific cuisine to filter by
        diet: Specific diet to filter by
        ingredients: List of ingredients that should be in the recipe
        
    Returns:
        Filtered list of recipes
    """
    filtered = recipes.copy()
    
    # Filter by search query
    if search_query:
        search_query = search_query.lower()
        filtered = [
            recipe for recipe in filtered 
            if search_query in recipe.get('name', '').lower() or 
               search_query in recipe.get('description', '').lower()
        ]
    
    # Filter by meal type
    if meal_type:
        filtered = [
            recipe for recipe in filtered 
            if recipe.get('mealType') == meal_type
        ]
    
    # Filter by cuisine
    if cuisine:
        filtered = [
            recipe for recipe in filtered 
            if recipe.get('cuisine') == cuisine
        ]
    
    # Filter by diet
    if diet:
        filtered = [
            recipe for recipe in filtered 
            if diet in recipe.get('diets', [])
        ]
    
    # Filter by ingredients
    if ingredients and any(ingredients):
        # Remove empty strings and whitespace
        ingredients = [i.strip().lower() for i in ingredients if i.strip()]
        if ingredients:
            filtered = [
                recipe for recipe in filtered 
                if all(
                    any(ing.lower() in recipe_ing.lower() 
                        for recipe_ing in recipe.get('ingredients', []))
                    for ing in ingredients
                )
            ]
    
    return filtered
