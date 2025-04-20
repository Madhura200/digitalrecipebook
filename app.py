import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from utils import get_recipe_by_id, filter_recipes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# File for storing favorite recipes
FAVORITES_FILE = "favorites.json"

# Load recipe data with UTF-8 encoding
def load_recipes():
    """Load recipes from JSON file with UTF-8 encoding."""
    try:
        with open('data/recipes.json', 'r', encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading recipes: {e}")
        return []


def load_favorites():
    """Load favorite recipe IDs from file."""
    if not os.path.exists(FAVORITES_FILE):
        return []
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as file:
            favorites = json.load(file)
            return [str(fav) for fav in favorites]  # Convert all IDs to strings
    except json.JSONDecodeError:
        logging.error("Error decoding favorites.json. Returning empty list.")
        return []


def save_favorites(favorites):
    """Save favorite recipe IDs to file with UTF-8 encoding."""
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
            json.dump(favorites, file, indent=4)
        logging.info(f"Favorites successfully saved: {favorites}")
    except Exception as e:
        logging.error(f"Error saving favorites: {e}")

@app.route("/")
def index():
    """Homepage with recipe search and filtering."""
    recipes = load_recipes()
    
    if not recipes:
        flash("No recipes found. Please check your dataset.", "warning")
    
    meal_types = sorted(set(recipe.get("mealType", "Other") for recipe in recipes))
    cuisines = sorted(set(recipe.get("cuisine", "Other") for recipe in recipes))
    diets = sorted(set(diet for recipe in recipes for diet in recipe.get("diets", ["None"])))

    # Get search parameters
    search_query = request.args.get("search", "")
    meal_type = request.args.get("meal_type", "")
    cuisine = request.args.get("cuisine", "")
    diet = request.args.get("diet", "")
    ingredients = request.args.get("ingredients", "")

    # Filter recipes
    filtered_recipes = filter_recipes(
        recipes, 
        search_query, 
        meal_type, 
        cuisine, 
        diet, 
        ingredients.split(",") if ingredients else []
    )

    return render_template(
        "index.html", 
        recipes=filtered_recipes, 
        meal_types=meal_types,
        cuisines=cuisines,
        diets=diets,
        search_query=search_query,
        meal_type=meal_type,
        cuisine=cuisine,
        diet=diet,
        ingredients=ingredients
    )

@app.route("/recipe/<recipe_id>")
def recipe_detail(recipe_id):
    """Display detailed information about a recipe."""
    recipes = load_recipes()
    recipe = get_recipe_by_id(recipes, recipe_id)

    if not recipe:
        flash("Recipe not found", "danger")
        return redirect(url_for("index"))

    is_favorite = str(recipe_id) in load_favorites()

    return render_template("recipe_detail.html", recipe=recipe, is_favorite=is_favorite)

@app.route("/favorites")
def favorites():
    """Display user's favorite recipes."""
    favorites = load_favorites()
    recipes = load_recipes()
    favorite_recipes = [recipe for recipe in recipes if str(recipe.get("id")) in favorites]

    if not favorite_recipes:
        flash("You haven't added any recipes to favorites yet.", "info")

    return render_template("favorites.html", recipes=favorite_recipes)

@app.route("/toggle_favorite/<recipe_id>", methods=["POST"])
def toggle_favorite(recipe_id):
    """Add or remove a recipe from favorites."""
    favorites = load_favorites()
    recipe_id = str(recipe_id)  # Ensure recipe_id is always a string
    logging.info(f"Before toggle - Current favorites: {favorites}")
    logging.info(f"Toggling favorite for recipe_id: {recipe_id} (Type: {type(recipe_id)})")

    if recipe_id in favorites:
        favorites.remove(recipe_id)
        logging.info(f"Removed recipe {recipe_id} from favorites")
        flash("Recipe removed from favorites", "success")
    else:
        favorites.append(recipe_id)
        logging.info(f"Added recipe {recipe_id} to favorites")
        flash("Recipe added to favorites", "success")

    save_favorites(favorites)
    logging.info(f"After toggle - Updated favorites: {load_favorites()}")  # Reload to confirm

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "success", "is_favorite": recipe_id in favorites})

    return redirect(request.referrer or url_for("index"))

@app.route("/search")
def search():
    """Search for recipes and redirect to index with search parameters."""
    return redirect(url_for(
        "index", 
        search=request.args.get("search", ""), 
        meal_type=request.args.get("meal_type", ""), 
        cuisine=request.args.get("cuisine", ""), 
        diet=request.args.get("diet", ""), 
        ingredients=request.args.get("ingredients", "")
    ))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", error="Server error. Please try again later."), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
