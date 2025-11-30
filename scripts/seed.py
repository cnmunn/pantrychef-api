"""Seed script to populate the database with sample ingredients and recipes."""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker, engine
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe, RecipeIngredient


# =============================================================================
# INGREDIENT DATA (~100 ingredients)
# =============================================================================

INGREDIENTS: list[dict] = [
    # PRODUCE - Vegetables (25 items)
    {"name": "Onion", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Garlic", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Tomato", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Potato", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Carrot", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Celery", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Bell Pepper", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Broccoli", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Spinach", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Lettuce", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Cucumber", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Zucchini", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Mushroom", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Green Beans", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Corn", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Asparagus", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Cabbage", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Cauliflower", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Eggplant", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Jalapeño", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Ginger", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Green Onion", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Sweet Potato", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Avocado", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Kale", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    
    # PRODUCE - Fruits (10 items)
    {"name": "Lemon", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Lime", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Apple", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Banana", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Orange", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Strawberry", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Blueberry", "category": "produce", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    
    # DAIRY (10 items)
    {"name": "Milk", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Butter", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Cheddar Cheese", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Parmesan Cheese", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Mozzarella Cheese", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Cream Cheese", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Sour Cream", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Heavy Cream", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Greek Yogurt", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "dairy"},
    {"name": "Egg", "category": "dairy", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "eggs"},
    
    # PROTEIN - Meat (12 items)
    {"name": "Chicken Breast", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Chicken Thigh", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Ground Beef", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Beef Steak", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Pork Chop", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Bacon", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Italian Sausage", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Ground Turkey", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Ham", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Salmon", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True, "allergens": "fish"},
    {"name": "Shrimp", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True, "allergens": "shellfish"},
    {"name": "Tuna", "category": "protein", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True, "allergens": "fish"},
    
    # PROTEIN - Plant-based (5 items)
    {"name": "Tofu", "category": "protein", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True, "allergens": "soy"},
    {"name": "Black Beans", "category": "protein", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Chickpeas", "category": "protein", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Lentils", "category": "protein", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Kidney Beans", "category": "protein", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    
    # GRAINS & PASTA (12 items)
    {"name": "White Rice", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Brown Rice", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Pasta", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    {"name": "Spaghetti", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    {"name": "Penne", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    {"name": "Bread", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    {"name": "Flour", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    {"name": "Bread Crumbs", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    {"name": "Tortilla", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    {"name": "Quinoa", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Oats", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Couscous", "category": "grains", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "wheat"},
    
    # PANTRY STAPLES (10 items)
    {"name": "Olive Oil", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Vegetable Oil", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Chicken Broth", "category": "pantry", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True},
    {"name": "Vegetable Broth", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Canned Tomatoes", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Tomato Paste", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Coconut Milk", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Peanut Butter", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True, "allergens": "peanuts"},
    {"name": "Sugar", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Brown Sugar", "category": "pantry", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    
    # CONDIMENTS & SAUCES (10 items)
    {"name": "Soy Sauce", "category": "condiments", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": False, "allergens": "soy,wheat"},
    {"name": "Hot Sauce", "category": "condiments", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Worcestershire Sauce", "category": "condiments", "is_vegetarian": False, "is_vegan": False, "is_gluten_free": True, "allergens": "fish"},
    {"name": "Mustard", "category": "condiments", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Mayonnaise", "category": "condiments", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True, "allergens": "eggs"},
    {"name": "Ketchup", "category": "condiments", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Balsamic Vinegar", "category": "condiments", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Red Wine Vinegar", "category": "condiments", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Honey", "category": "condiments", "is_vegetarian": True, "is_vegan": False, "is_gluten_free": True},
    {"name": "Maple Syrup", "category": "condiments", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    
    # SPICES & HERBS (15 items)
    {"name": "Salt", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Black Pepper", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Paprika", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Cumin", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Chili Powder", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Oregano", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Basil", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Thyme", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Rosemary", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Cinnamon", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Cayenne Pepper", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Italian Seasoning", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Garlic Powder", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Onion Powder", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    {"name": "Cilantro", "category": "spices", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True},
    
    # NUTS & SEEDS (5 items)
    {"name": "Almonds", "category": "nuts", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True, "allergens": "nuts"},
    {"name": "Walnuts", "category": "nuts", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True, "allergens": "nuts"},
    {"name": "Pine Nuts", "category": "nuts", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True, "allergens": "nuts"},
    {"name": "Sesame Seeds", "category": "nuts", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True, "allergens": "sesame"},
    {"name": "Peanuts", "category": "nuts", "is_vegetarian": True, "is_vegan": True, "is_gluten_free": True, "allergens": "peanuts"},
]


# =============================================================================
# RECIPE DATA (25 recipes)
# =============================================================================

# We'll reference ingredients by name, then resolve to IDs after seeding ingredients
RECIPES: list[dict] = [
    # 1. Classic Spaghetti Bolognese
    {
        "title": "Classic Spaghetti Bolognese",
        "description": "A rich and hearty Italian meat sauce served over spaghetti.",
        "instructions": """1. Heat olive oil in a large pot over medium heat.
2. Add onion, carrot, and celery. Cook until softened, about 5 minutes.
3. Add garlic and cook for 1 minute more.
4. Add ground beef and cook until browned, breaking it up with a spoon.
5. Add canned tomatoes, tomato paste, oregano, basil, salt, and pepper.
6. Simmer for at least 30 minutes, stirring occasionally.
7. Meanwhile, cook spaghetti according to package directions.
8. Serve sauce over spaghetti, topped with parmesan cheese.""",
        "prep_time": 15,
        "cook_time": 45,
        "difficulty_level": "medium",
        "servings": 6,
        "ingredients": [
            {"name": "Spaghetti", "quantity": "1", "unit": "pound"},
            {"name": "Ground Beef", "quantity": "1", "unit": "pound"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Carrot", "quantity": "2", "unit": "medium"},
            {"name": "Celery", "quantity": "2", "unit": "stalks"},
            {"name": "Garlic", "quantity": "4", "unit": "cloves"},
            {"name": "Canned Tomatoes", "quantity": "28", "unit": "oz"},
            {"name": "Tomato Paste", "quantity": "2", "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Oregano", "quantity": "1", "unit": "tsp"},
            {"name": "Basil", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
            {"name": "Parmesan Cheese", "quantity": "1/2", "unit": "cup", "optional": True},
        ],
    },
    
    # 2. Chicken Stir Fry
    {
        "title": "Quick Chicken Stir Fry",
        "description": "A fast and healthy weeknight dinner with tender chicken and crisp vegetables.",
        "instructions": """1. Cut chicken breast into bite-sized pieces and season with salt and pepper.
2. Heat vegetable oil in a wok or large skillet over high heat.
3. Add chicken and cook until golden, about 5-6 minutes. Remove and set aside.
4. Add bell pepper, broccoli, and carrot to the pan. Stir fry for 3-4 minutes.
5. Add garlic and ginger, cook for 30 seconds.
6. Return chicken to the pan.
7. Mix soy sauce and add to the pan. Toss everything together.
8. Serve over white rice, garnished with green onion and sesame seeds.""",
        "prep_time": 15,
        "cook_time": 15,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Chicken Breast", "quantity": "1.5", "unit": "pounds"},
            {"name": "Bell Pepper", "quantity": "2", "unit": "medium"},
            {"name": "Broccoli", "quantity": "2", "unit": "cups"},
            {"name": "Carrot", "quantity": "2", "unit": "medium"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Ginger", "quantity": "1", "unit": "inch"},
            {"name": "Soy Sauce", "quantity": "3", "unit": "tbsp"},
            {"name": "Vegetable Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "White Rice", "quantity": "2", "unit": "cups"},
            {"name": "Green Onion", "quantity": "3", "unit": "stalks", "optional": True},
            {"name": "Sesame Seeds", "quantity": "1", "unit": "tbsp", "optional": True},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 3. Vegetarian Black Bean Tacos
    {
        "title": "Vegetarian Black Bean Tacos",
        "description": "Flavorful and filling tacos loaded with seasoned black beans and fresh toppings.",
        "instructions": """1. Drain and rinse black beans.
2. Heat olive oil in a skillet over medium heat.
3. Add onion and cook until softened, about 3 minutes.
4. Add garlic, cumin, chili powder, and paprika. Cook for 30 seconds.
5. Add black beans and 1/4 cup water. Mash some beans and simmer for 5 minutes.
6. Season with salt and pepper.
7. Warm tortillas in a dry pan or microwave.
8. Fill tortillas with beans, top with avocado, tomato, lettuce, sour cream, and cheese.
9. Squeeze lime juice over tacos and serve with cilantro.""",
        "prep_time": 10,
        "cook_time": 15,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Black Beans", "quantity": "2", "unit": "cans (15 oz)"},
            {"name": "Tortilla", "quantity": "8", "unit": "small"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Cumin", "quantity": "1", "unit": "tsp"},
            {"name": "Chili Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Paprika", "quantity": "1/2", "unit": "tsp"},
            {"name": "Olive Oil", "quantity": "1", "unit": "tbsp"},
            {"name": "Avocado", "quantity": "2", "unit": "medium"},
            {"name": "Tomato", "quantity": "2", "unit": "medium"},
            {"name": "Lettuce", "quantity": "2", "unit": "cups"},
            {"name": "Sour Cream", "quantity": "1/2", "unit": "cup", "optional": True},
            {"name": "Cheddar Cheese", "quantity": "1", "unit": "cup", "optional": True},
            {"name": "Lime", "quantity": "1", "unit": "whole"},
            {"name": "Cilantro", "quantity": "1/4", "unit": "cup", "optional": True},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 4. Creamy Garlic Parmesan Pasta
    {
        "title": "Creamy Garlic Parmesan Pasta",
        "description": "A decadent pasta dish with a rich, creamy garlic parmesan sauce.",
        "instructions": """1. Cook penne according to package directions. Reserve 1 cup pasta water.
2. In a large skillet, melt butter over medium heat.
3. Add garlic and cook until fragrant, about 1 minute.
4. Add heavy cream and bring to a simmer.
5. Stir in parmesan cheese until melted and smooth.
6. Season with salt, pepper, and Italian seasoning.
7. Add cooked pasta and toss to coat. Add pasta water as needed.
8. Serve immediately, topped with extra parmesan and fresh basil.""",
        "prep_time": 10,
        "cook_time": 20,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Penne", "quantity": "1", "unit": "pound"},
            {"name": "Butter", "quantity": "4", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "6", "unit": "cloves"},
            {"name": "Heavy Cream", "quantity": "1.5", "unit": "cups"},
            {"name": "Parmesan Cheese", "quantity": "1.5", "unit": "cups"},
            {"name": "Italian Seasoning", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
            {"name": "Basil", "quantity": "2", "unit": "tbsp", "optional": True},
        ],
    },
    
    # 5. Honey Garlic Salmon
    {
        "title": "Honey Garlic Glazed Salmon",
        "description": "Perfectly seared salmon fillets with a sweet and savory honey garlic glaze.",
        "instructions": """1. Mix honey, soy sauce, garlic, and lemon juice in a bowl for the glaze.
2. Season salmon fillets with salt and pepper.
3. Heat olive oil in a skillet over medium-high heat.
4. Place salmon skin-side up and cook for 4 minutes until golden.
5. Flip salmon and pour glaze over the top.
6. Cook for another 3-4 minutes until salmon is cooked through.
7. Baste salmon with the glaze from the pan.
8. Serve with the pan sauce drizzled on top and lemon wedges.""",
        "prep_time": 10,
        "cook_time": 15,
        "difficulty_level": "medium",
        "servings": 4,
        "ingredients": [
            {"name": "Salmon", "quantity": "4", "unit": "fillets (6 oz each)"},
            {"name": "Honey", "quantity": "3", "unit": "tbsp"},
            {"name": "Soy Sauce", "quantity": "2", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "4", "unit": "cloves"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 6. Classic Caesar Salad
    {
        "title": "Classic Caesar Salad",
        "description": "Crisp romaine lettuce with homemade Caesar dressing, croutons, and parmesan.",
        "instructions": """1. For dressing: whisk together mayonnaise, garlic, lemon juice, worcestershire sauce, and parmesan.
2. Season with salt and pepper.
3. Tear lettuce into bite-sized pieces and place in a large bowl.
4. Drizzle dressing over lettuce and toss to coat.
5. Top with bread crumbs (or croutons) and extra parmesan.
6. Add grilled chicken breast for a heartier meal.
7. Serve immediately while lettuce is crisp.""",
        "prep_time": 15,
        "cook_time": 0,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Lettuce", "quantity": "2", "unit": "heads"},
            {"name": "Parmesan Cheese", "quantity": "1", "unit": "cup"},
            {"name": "Mayonnaise", "quantity": "1/2", "unit": "cup"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Worcestershire Sauce", "quantity": "1", "unit": "tsp"},
            {"name": "Bread Crumbs", "quantity": "1", "unit": "cup"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
            {"name": "Chicken Breast", "quantity": "2", "unit": "breasts", "optional": True},
        ],
    },
    
    # 7. Thai Coconut Curry
    {
        "title": "Thai Coconut Vegetable Curry",
        "description": "A fragrant and creamy Thai curry loaded with vegetables and tofu.",
        "instructions": """1. Press tofu to remove excess moisture, then cube it.
2. Heat vegetable oil in a large pot or wok over medium-high heat.
3. Add tofu and cook until golden on all sides. Remove and set aside.
4. Add onion and bell pepper to the pot. Cook for 3 minutes.
5. Add garlic, ginger, and curry powder. Stir for 30 seconds.
6. Pour in coconut milk and vegetable broth. Bring to a simmer.
7. Add broccoli, zucchini, and tofu back to the pot.
8. Simmer for 10-15 minutes until vegetables are tender.
9. Season with soy sauce, salt, and pepper.
10. Serve over white rice with lime wedges and cilantro.""",
        "prep_time": 20,
        "cook_time": 25,
        "difficulty_level": "medium",
        "servings": 4,
        "ingredients": [
            {"name": "Tofu", "quantity": "14", "unit": "oz"},
            {"name": "Coconut Milk", "quantity": "1", "unit": "can (14 oz)"},
            {"name": "Vegetable Broth", "quantity": "1", "unit": "cup"},
            {"name": "Broccoli", "quantity": "2", "unit": "cups"},
            {"name": "Bell Pepper", "quantity": "2", "unit": "medium"},
            {"name": "Zucchini", "quantity": "2", "unit": "medium"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Garlic", "quantity": "4", "unit": "cloves"},
            {"name": "Ginger", "quantity": "1", "unit": "inch"},
            {"name": "Vegetable Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Soy Sauce", "quantity": "2", "unit": "tbsp"},
            {"name": "White Rice", "quantity": "2", "unit": "cups"},
            {"name": "Lime", "quantity": "1", "unit": "whole"},
            {"name": "Cilantro", "quantity": "1/4", "unit": "cup", "optional": True},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 8. Classic Beef Burger
    {
        "title": "Classic Beef Burger",
        "description": "Juicy homemade beef burgers with all the classic fixings.",
        "instructions": """1. Mix ground beef with salt, pepper, garlic powder, and onion powder.
2. Form into 4 patties, making a slight indent in the center of each.
3. Heat a grill or cast iron pan over high heat.
4. Cook patties for 4-5 minutes per side for medium doneness.
5. Add cheddar cheese in the last minute of cooking to melt.
6. Toast bread buns on the grill or in a pan.
7. Assemble burgers with lettuce, tomato, onion, ketchup, and mustard.
8. Serve immediately with your favorite sides.""",
        "prep_time": 15,
        "cook_time": 12,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Ground Beef", "quantity": "1.5", "unit": "pounds"},
            {"name": "Bread", "quantity": "4", "unit": "buns"},
            {"name": "Cheddar Cheese", "quantity": "4", "unit": "slices"},
            {"name": "Lettuce", "quantity": "4", "unit": "leaves"},
            {"name": "Tomato", "quantity": "1", "unit": "large"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Ketchup", "quantity": "4", "unit": "tbsp"},
            {"name": "Mustard", "quantity": "2", "unit": "tbsp"},
            {"name": "Garlic Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Onion Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
        ],
    },
    
    # 9. Mushroom Risotto
    {
        "title": "Creamy Mushroom Risotto",
        "description": "A classic Italian rice dish with earthy mushrooms and parmesan.",
        "instructions": """1. Warm chicken broth in a saucepan and keep at a low simmer.
2. In a large pan, melt butter and sauté mushrooms until golden. Remove and set aside.
3. Add olive oil and onion. Cook until translucent.
4. Add rice and stir for 1-2 minutes until lightly toasted.
5. Add a ladleful of warm broth, stirring until absorbed.
6. Continue adding broth one ladle at a time, stirring constantly.
7. After about 18-20 minutes, rice should be creamy and al dente.
8. Stir in mushrooms, parmesan, and remaining butter.
9. Season with salt and pepper. Serve immediately.""",
        "prep_time": 10,
        "cook_time": 35,
        "difficulty_level": "hard",
        "servings": 4,
        "ingredients": [
            {"name": "White Rice", "quantity": "1.5", "unit": "cups"},
            {"name": "Mushroom", "quantity": "8", "unit": "oz"},
            {"name": "Chicken Broth", "quantity": "6", "unit": "cups"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Butter", "quantity": "4", "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Parmesan Cheese", "quantity": "1", "unit": "cup"},
            {"name": "Thyme", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 10. Shrimp Scampi
    {
        "title": "Garlic Butter Shrimp Scampi",
        "description": "Succulent shrimp in a rich garlic butter wine sauce over linguine.",
        "instructions": """1. Cook pasta according to package directions. Reserve 1 cup pasta water.
2. In a large skillet, melt butter with olive oil over medium heat.
3. Add garlic and red pepper flakes. Cook for 30 seconds.
4. Add shrimp and cook for 2-3 minutes per side until pink.
5. Remove shrimp and set aside.
6. Add lemon juice to the pan and scrape up any browned bits.
7. Return shrimp to the pan with cooked pasta.
8. Toss everything together, adding pasta water as needed.
9. Season with salt and pepper. Garnish with parsley.""",
        "prep_time": 10,
        "cook_time": 20,
        "difficulty_level": "medium",
        "servings": 4,
        "ingredients": [
            {"name": "Shrimp", "quantity": "1", "unit": "pound"},
            {"name": "Pasta", "quantity": "12", "unit": "oz"},
            {"name": "Butter", "quantity": "4", "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "6", "unit": "cloves"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Cayenne Pepper", "quantity": "1/4", "unit": "tsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 11. Vegetable Fried Rice
    {
        "title": "Easy Vegetable Fried Rice",
        "description": "A quick and delicious way to use leftover rice with fresh vegetables.",
        "instructions": """1. Beat eggs and set aside.
2. Heat vegetable oil in a wok or large skillet over high heat.
3. Add beaten eggs and scramble. Remove and set aside.
4. Add more oil if needed. Stir fry carrot, peas, and corn for 2 minutes.
5. Add rice and stir fry for 3-4 minutes, breaking up any clumps.
6. Push rice to the side, add garlic and ginger. Cook 30 seconds.
7. Mix everything together. Add soy sauce and sesame seeds.
8. Return eggs to the pan and toss.
9. Garnish with green onion and serve hot.""",
        "prep_time": 10,
        "cook_time": 15,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "White Rice", "quantity": "3", "unit": "cups (cooked)"},
            {"name": "Egg", "quantity": "3", "unit": "large"},
            {"name": "Carrot", "quantity": "1", "unit": "medium"},
            {"name": "Corn", "quantity": "1/2", "unit": "cup"},
            {"name": "Green Beans", "quantity": "1/2", "unit": "cup"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Ginger", "quantity": "1", "unit": "tsp"},
            {"name": "Soy Sauce", "quantity": "3", "unit": "tbsp"},
            {"name": "Vegetable Oil", "quantity": "3", "unit": "tbsp"},
            {"name": "Sesame Seeds", "quantity": "1", "unit": "tbsp", "optional": True},
            {"name": "Green Onion", "quantity": "3", "unit": "stalks"},
            {"name": "Salt", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 12. Caprese Salad
    {
        "title": "Fresh Caprese Salad",
        "description": "A simple Italian salad with fresh tomatoes, mozzarella, and basil.",
        "instructions": """1. Slice tomatoes and mozzarella into 1/4 inch thick rounds.
2. Arrange alternating slices of tomato and mozzarella on a platter.
3. Tuck fresh basil leaves between slices.
4. Drizzle generously with olive oil.
5. Drizzle with balsamic vinegar.
6. Season with salt and freshly cracked black pepper.
7. Let sit for 5 minutes before serving to let flavors meld.
8. Serve at room temperature.""",
        "prep_time": 10,
        "cook_time": 0,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Tomato", "quantity": "4", "unit": "medium"},
            {"name": "Mozzarella Cheese", "quantity": "8", "unit": "oz"},
            {"name": "Basil", "quantity": "1/2", "unit": "cup (fresh leaves)"},
            {"name": "Olive Oil", "quantity": "3", "unit": "tbsp"},
            {"name": "Balsamic Vinegar", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 13. Lemon Herb Chicken
    {
        "title": "Lemon Herb Roasted Chicken",
        "description": "Juicy chicken thighs roasted with bright lemon and fresh herbs.",
        "instructions": """1. Preheat oven to 425°F (220°C).
2. Mix olive oil, lemon juice, garlic, rosemary, thyme, salt, and pepper.
3. Place chicken thighs in a baking dish.
4. Pour herb mixture over chicken, turning to coat evenly.
5. Slice remaining lemon and place around chicken.
6. Roast for 35-40 minutes until chicken is cooked through (165°F internal).
7. Let rest for 5 minutes before serving.
8. Spoon pan juices over chicken when serving.""",
        "prep_time": 15,
        "cook_time": 40,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Chicken Thigh", "quantity": "8", "unit": "pieces"},
            {"name": "Lemon", "quantity": "2", "unit": "whole"},
            {"name": "Garlic", "quantity": "6", "unit": "cloves"},
            {"name": "Rosemary", "quantity": "2", "unit": "tbsp"},
            {"name": "Thyme", "quantity": "1", "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": "3", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
        ],
    },
    
    # 14. Breakfast Scramble
    {
        "title": "Loaded Breakfast Scramble",
        "description": "Fluffy scrambled eggs loaded with bacon, cheese, and vegetables.",
        "instructions": """1. Cook bacon in a skillet until crispy. Remove and set aside.
2. Pour off most of the bacon fat, leaving about 1 tbsp.
3. Add bell pepper and onion. Cook until softened, about 3 minutes.
4. Beat eggs with milk, salt, and pepper.
5. Pour eggs into the skillet over medium-low heat.
6. Gently stir and fold eggs as they cook.
7. When eggs are almost set, add cheese and crumbled bacon.
8. Remove from heat while still slightly wet (they'll continue cooking).
9. Serve immediately with hot sauce on the side.""",
        "prep_time": 10,
        "cook_time": 15,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Egg", "quantity": "8", "unit": "large"},
            {"name": "Bacon", "quantity": "6", "unit": "strips"},
            {"name": "Cheddar Cheese", "quantity": "1", "unit": "cup"},
            {"name": "Bell Pepper", "quantity": "1", "unit": "medium"},
            {"name": "Onion", "quantity": "1/2", "unit": "medium"},
            {"name": "Milk", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
            {"name": "Hot Sauce", "quantity": "1", "unit": "tbsp", "optional": True},
        ],
    },
    
    # 15. Chickpea Salad
    {
        "title": "Mediterranean Chickpea Salad",
        "description": "A protein-packed salad with chickpeas, cucumber, tomatoes, and feta.",
        "instructions": """1. Drain and rinse chickpeas.
2. Dice cucumber, tomatoes, and bell pepper into similar-sized pieces.
3. Thinly slice red onion.
4. In a large bowl, combine chickpeas and all vegetables.
5. Make dressing: whisk olive oil, lemon juice, garlic, oregano, salt, and pepper.
6. Pour dressing over salad and toss to combine.
7. Add crumbled feta cheese on top (don't mix in).
8. Refrigerate for 15 minutes before serving to let flavors develop.
9. Serve cold or at room temperature.""",
        "prep_time": 15,
        "cook_time": 0,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Chickpeas", "quantity": "2", "unit": "cans (15 oz)"},
            {"name": "Cucumber", "quantity": "1", "unit": "large"},
            {"name": "Tomato", "quantity": "2", "unit": "medium"},
            {"name": "Bell Pepper", "quantity": "1", "unit": "medium"},
            {"name": "Onion", "quantity": "1/2", "unit": "small"},
            {"name": "Olive Oil", "quantity": "3", "unit": "tbsp"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Garlic", "quantity": "1", "unit": "clove"},
            {"name": "Oregano", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 16. Beef Tacos
    {
        "title": "Classic Ground Beef Tacos",
        "description": "Seasoned ground beef tacos with all your favorite toppings.",
        "instructions": """1. Heat oil in a skillet over medium-high heat.
2. Add ground beef and cook until browned, breaking it up.
3. Add onion and cook until softened.
4. Add garlic, cumin, chili powder, paprika, salt, and pepper.
5. Add tomato paste and 1/4 cup water. Simmer for 5 minutes.
6. Warm tortillas in a dry pan or microwave.
7. Fill tortillas with beef mixture.
8. Top with lettuce, tomato, cheese, sour cream, and hot sauce.
9. Serve with lime wedges.""",
        "prep_time": 10,
        "cook_time": 20,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Ground Beef", "quantity": "1", "unit": "pound"},
            {"name": "Tortilla", "quantity": "8", "unit": "small"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Tomato Paste", "quantity": "2", "unit": "tbsp"},
            {"name": "Cumin", "quantity": "1", "unit": "tsp"},
            {"name": "Chili Powder", "quantity": "1", "unit": "tbsp"},
            {"name": "Paprika", "quantity": "1/2", "unit": "tsp"},
            {"name": "Lettuce", "quantity": "2", "unit": "cups"},
            {"name": "Tomato", "quantity": "2", "unit": "medium"},
            {"name": "Cheddar Cheese", "quantity": "1", "unit": "cup"},
            {"name": "Sour Cream", "quantity": "1/2", "unit": "cup", "optional": True},
            {"name": "Hot Sauce", "quantity": "2", "unit": "tbsp", "optional": True},
            {"name": "Lime", "quantity": "1", "unit": "whole"},
            {"name": "Vegetable Oil", "quantity": "1", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
        ],
    },
    
    # 17. Baked Potato
    {
        "title": "Loaded Baked Potato",
        "description": "Crispy-skinned baked potatoes with all the classic toppings.",
        "instructions": """1. Preheat oven to 400°F (200°C).
2. Wash and dry potatoes. Prick several times with a fork.
3. Rub with olive oil and season generously with salt.
4. Place directly on oven rack and bake for 45-60 minutes.
5. Potatoes are done when a fork slides in easily.
6. Cut a slit in the top and squeeze to open.
7. Add butter, sour cream, cheddar cheese, and bacon bits.
8. Top with green onion and black pepper.
9. Serve immediately while hot.""",
        "prep_time": 10,
        "cook_time": 60,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Potato", "quantity": "4", "unit": "large"},
            {"name": "Butter", "quantity": "4", "unit": "tbsp"},
            {"name": "Sour Cream", "quantity": "1/2", "unit": "cup"},
            {"name": "Cheddar Cheese", "quantity": "1", "unit": "cup"},
            {"name": "Bacon", "quantity": "4", "unit": "strips"},
            {"name": "Green Onion", "quantity": "4", "unit": "stalks"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
        ],
    },
    
    # 18. Tomato Soup
    {
        "title": "Creamy Tomato Soup",
        "description": "A comforting homemade tomato soup perfect for pairing with grilled cheese.",
        "instructions": """1. Heat olive oil and butter in a large pot over medium heat.
2. Add onion and carrot. Cook until softened, about 5 minutes.
3. Add garlic and cook for 1 minute.
4. Add canned tomatoes, vegetable broth, basil, and sugar.
5. Bring to a boil, then reduce heat and simmer for 20 minutes.
6. Use an immersion blender to puree until smooth.
7. Stir in heavy cream and season with salt and pepper.
8. Serve hot with a drizzle of cream and fresh basil.""",
        "prep_time": 10,
        "cook_time": 30,
        "difficulty_level": "easy",
        "servings": 6,
        "ingredients": [
            {"name": "Canned Tomatoes", "quantity": "28", "unit": "oz"},
            {"name": "Vegetable Broth", "quantity": "2", "unit": "cups"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Carrot", "quantity": "1", "unit": "medium"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Butter", "quantity": "2", "unit": "tbsp"},
            {"name": "Heavy Cream", "quantity": "1/2", "unit": "cup"},
            {"name": "Basil", "quantity": "1", "unit": "tsp"},
            {"name": "Sugar", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
        ],
    },
    
    # 19. Quinoa Bowl
    {
        "title": "Mediterranean Quinoa Bowl",
        "description": "A healthy and colorful grain bowl with fresh vegetables and lemon dressing.",
        "instructions": """1. Cook quinoa according to package directions. Let cool slightly.
2. Dice cucumber, tomatoes, and bell pepper.
3. Drain and rinse chickpeas.
4. Make dressing: whisk olive oil, lemon juice, garlic, salt, and pepper.
5. In a large bowl, combine quinoa, vegetables, and chickpeas.
6. Drizzle with dressing and toss to combine.
7. Top with avocado slices and fresh herbs.
8. Serve warm or cold.""",
        "prep_time": 15,
        "cook_time": 20,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Quinoa", "quantity": "1", "unit": "cup"},
            {"name": "Chickpeas", "quantity": "1", "unit": "can (15 oz)"},
            {"name": "Cucumber", "quantity": "1", "unit": "medium"},
            {"name": "Tomato", "quantity": "2", "unit": "medium"},
            {"name": "Bell Pepper", "quantity": "1", "unit": "medium"},
            {"name": "Avocado", "quantity": "1", "unit": "medium"},
            {"name": "Olive Oil", "quantity": "3", "unit": "tbsp"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Garlic", "quantity": "1", "unit": "clove"},
            {"name": "Salt", "quantity": "1/2", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 20. Pork Chops
    {
        "title": "Pan-Seared Pork Chops",
        "description": "Perfectly seared pork chops with a simple herb butter sauce.",
        "instructions": """1. Remove pork chops from refrigerator 30 minutes before cooking.
2. Season generously with salt, pepper, and garlic powder.
3. Heat olive oil in a large skillet over medium-high heat.
4. Add pork chops and cook for 4-5 minutes per side until golden.
5. Add butter, garlic, rosemary, and thyme to the pan.
6. Baste pork chops with the melted herb butter.
7. Let rest for 5 minutes before serving.
8. Spoon pan sauce over pork chops when serving.""",
        "prep_time": 35,
        "cook_time": 15,
        "difficulty_level": "medium",
        "servings": 4,
        "ingredients": [
            {"name": "Pork Chop", "quantity": "4", "unit": "pieces (1 inch thick)"},
            {"name": "Butter", "quantity": "3", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "4", "unit": "cloves"},
            {"name": "Rosemary", "quantity": "2", "unit": "sprigs"},
            {"name": "Thyme", "quantity": "4", "unit": "sprigs"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Garlic Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
        ],
    },
    
    # 21. Spinach Salad
    {
        "title": "Warm Spinach Salad with Bacon",
        "description": "Fresh spinach topped with warm bacon dressing and a poached egg.",
        "instructions": """1. Cook bacon until crispy. Remove and crumble, reserving drippings.
2. To the warm bacon fat, add red wine vinegar, mustard, and honey.
3. Whisk until combined - this is your warm dressing.
4. Place spinach in a large bowl.
5. Slice mushrooms and add to spinach.
6. Pour warm dressing over spinach - it will wilt slightly.
7. Top with crumbled bacon and poached or soft-boiled egg.
8. Season with salt and pepper. Serve immediately.""",
        "prep_time": 10,
        "cook_time": 15,
        "difficulty_level": "medium",
        "servings": 4,
        "ingredients": [
            {"name": "Spinach", "quantity": "8", "unit": "cups"},
            {"name": "Bacon", "quantity": "6", "unit": "strips"},
            {"name": "Mushroom", "quantity": "8", "unit": "oz"},
            {"name": "Egg", "quantity": "4", "unit": "large"},
            {"name": "Red Wine Vinegar", "quantity": "2", "unit": "tbsp"},
            {"name": "Mustard", "quantity": "1", "unit": "tsp"},
            {"name": "Honey", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1/4", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/4", "unit": "tsp"},
        ],
    },
    
    # 22. Lentil Soup
    {
        "title": "Hearty Lentil Soup",
        "description": "A warming, protein-rich soup perfect for cold days.",
        "instructions": """1. Heat olive oil in a large pot over medium heat.
2. Add onion, carrot, and celery. Cook until softened, about 5 minutes.
3. Add garlic, cumin, and paprika. Stir for 30 seconds.
4. Add lentils, canned tomatoes, and vegetable broth.
5. Bring to a boil, then reduce heat and simmer for 25-30 minutes.
6. Lentils should be tender but not mushy.
7. Add spinach and stir until wilted.
8. Season with salt, pepper, and lemon juice.
9. Serve hot with crusty bread.""",
        "prep_time": 15,
        "cook_time": 35,
        "difficulty_level": "easy",
        "servings": 6,
        "ingredients": [
            {"name": "Lentils", "quantity": "1.5", "unit": "cups"},
            {"name": "Vegetable Broth", "quantity": "6", "unit": "cups"},
            {"name": "Canned Tomatoes", "quantity": "14", "unit": "oz"},
            {"name": "Onion", "quantity": "1", "unit": "medium"},
            {"name": "Carrot", "quantity": "2", "unit": "medium"},
            {"name": "Celery", "quantity": "2", "unit": "stalks"},
            {"name": "Garlic", "quantity": "4", "unit": "cloves"},
            {"name": "Spinach", "quantity": "2", "unit": "cups"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Cumin", "quantity": "1", "unit": "tsp"},
            {"name": "Paprika", "quantity": "1/2", "unit": "tsp"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1/2", "unit": "tsp"},
        ],
    },
    
    # 23. Grilled Cheese
    {
        "title": "Ultimate Grilled Cheese Sandwich",
        "description": "Crispy, buttery bread with perfectly melted cheese.",
        "instructions": """1. Butter one side of each bread slice generously.
2. Heat a skillet over medium-low heat.
3. Place one slice butter-side down in the pan.
4. Layer cheddar and mozzarella cheese on the bread.
5. Top with second slice, butter-side up.
6. Cook for 3-4 minutes until golden brown.
7. Flip carefully and cook another 3-4 minutes.
8. Press down gently to help cheese melt.
9. Cut diagonally and serve with tomato soup.""",
        "prep_time": 5,
        "cook_time": 10,
        "difficulty_level": "easy",
        "servings": 2,
        "ingredients": [
            {"name": "Bread", "quantity": "4", "unit": "slices"},
            {"name": "Cheddar Cheese", "quantity": "4", "unit": "slices"},
            {"name": "Mozzarella Cheese", "quantity": "4", "unit": "slices"},
            {"name": "Butter", "quantity": "3", "unit": "tbsp"},
        ],
    },
    
    # 24. Banana Oatmeal
    {
        "title": "Banana Nut Oatmeal",
        "description": "Creamy oatmeal topped with caramelized bananas and crunchy walnuts.",
        "instructions": """1. Bring milk and water to a boil in a saucepan.
2. Add oats and reduce heat to medium-low.
3. Cook for 5 minutes, stirring occasionally.
4. Meanwhile, melt butter in a small pan.
5. Add sliced banana and brown sugar. Cook until caramelized.
6. When oatmeal is creamy, stir in cinnamon and a pinch of salt.
7. Serve oatmeal topped with caramelized bananas and walnuts.
8. Drizzle with maple syrup and enjoy warm.""",
        "prep_time": 5,
        "cook_time": 10,
        "difficulty_level": "easy",
        "servings": 2,
        "ingredients": [
            {"name": "Oats", "quantity": "1", "unit": "cup"},
            {"name": "Milk", "quantity": "1.5", "unit": "cups"},
            {"name": "Banana", "quantity": "2", "unit": "medium"},
            {"name": "Walnuts", "quantity": "1/4", "unit": "cup"},
            {"name": "Brown Sugar", "quantity": "2", "unit": "tbsp"},
            {"name": "Butter", "quantity": "1", "unit": "tbsp"},
            {"name": "Cinnamon", "quantity": "1/2", "unit": "tsp"},
            {"name": "Maple Syrup", "quantity": "2", "unit": "tbsp", "optional": True},
            {"name": "Salt", "quantity": "1", "unit": "pinch"},
        ],
    },
    
    # 25. Teriyaki Chicken
    {
        "title": "Teriyaki Chicken Bowl",
        "description": "Sweet and savory teriyaki chicken served over fluffy rice with vegetables.",
        "instructions": """1. Make teriyaki sauce: combine soy sauce, honey, garlic, and ginger.
2. Cut chicken breast into bite-sized pieces.
3. Heat vegetable oil in a large skillet over medium-high heat.
4. Add chicken and cook until golden and cooked through, about 6-7 minutes.
5. Add broccoli to the pan and cook for 2-3 minutes.
6. Pour teriyaki sauce over chicken and vegetables.
7. Simmer until sauce thickens slightly, about 2 minutes.
8. Serve over white rice, garnished with sesame seeds and green onion.""",
        "prep_time": 15,
        "cook_time": 20,
        "difficulty_level": "easy",
        "servings": 4,
        "ingredients": [
            {"name": "Chicken Breast", "quantity": "1.5", "unit": "pounds"},
            {"name": "White Rice", "quantity": "2", "unit": "cups"},
            {"name": "Broccoli", "quantity": "2", "unit": "cups"},
            {"name": "Soy Sauce", "quantity": "1/4", "unit": "cup"},
            {"name": "Honey", "quantity": "3", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Ginger", "quantity": "1", "unit": "tsp"},
            {"name": "Vegetable Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Sesame Seeds", "quantity": "1", "unit": "tbsp", "optional": True},
            {"name": "Green Onion", "quantity": "3", "unit": "stalks", "optional": True},
        ],
    },
]


async def seed_ingredients(session: AsyncSession) -> dict[str, int]:
    """Seed ingredients and return a mapping of name to id."""
    print("🌱 Seeding ingredients...")
    
    # Check if ingredients already exist
    result = await session.execute(select(Ingredient).limit(1))
    if result.scalar_one_or_none():
        print("   ⚠️  Ingredients already exist, fetching existing data...")
        result = await session.execute(select(Ingredient))
        ingredients = result.scalars().all()
        return {ing.name: ing.id for ing in ingredients}
    
    # Create all ingredients
    ingredient_map = {}
    for ing_data in INGREDIENTS:
        ingredient = Ingredient(**ing_data)
        session.add(ingredient)
        await session.flush()  # Get the ID
        ingredient_map[ingredient.name] = ingredient.id
    
    await session.commit()
    print(f"   ✅ Created {len(INGREDIENTS)} ingredients")
    return ingredient_map


async def seed_recipes(session: AsyncSession, ingredient_map: dict[str, int]) -> None:
    """Seed recipes with their ingredients."""
    print("🍳 Seeding recipes...")
    
    # Check if recipes already exist
    result = await session.execute(select(Recipe).limit(1))
    if result.scalar_one_or_none():
        print("   ⚠️  Recipes already exist, skipping...")
        return
    
    recipes_created = 0
    for recipe_data in RECIPES:
        # Extract ingredients from recipe data
        ingredients_list = recipe_data.pop("ingredients")
        
        # Create recipe
        recipe = Recipe(**recipe_data)
        session.add(recipe)
        await session.flush()  # Get the recipe ID
        
        # Create recipe ingredients
        for ing in ingredients_list:
            ingredient_name = ing["name"]
            if ingredient_name not in ingredient_map:
                print(f"   ⚠️  Warning: Ingredient '{ingredient_name}' not found, skipping...")
                continue
            
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_map[ingredient_name],
                quantity=ing.get("quantity"),
                unit=ing.get("unit"),
                optional=ing.get("optional", False),
            )
            session.add(recipe_ingredient)
        
        recipes_created += 1
    
    await session.commit()
    print(f"   ✅ Created {recipes_created} recipes")


async def main() -> None:
    """Main seeding function."""
    print("\n" + "=" * 50)
    print("🚀 Starting PantryChef Database Seeder")
    print("=" * 50 + "\n")
    
    async with async_session_maker() as session:
        try:
            # Seed ingredients first and get the mapping
            ingredient_map = await seed_ingredients(session)
            
            # Then seed recipes using the ingredient mapping
            await seed_recipes(session, ingredient_map)
            
            print("\n" + "=" * 50)
            print("✨ Seeding complete!")
            print("=" * 50 + "\n")
            
            # Print summary
            result = await session.execute(select(Ingredient))
            ingredient_count = len(result.scalars().all())
            
            result = await session.execute(select(Recipe))
            recipe_count = len(result.scalars().all())
            
            print(f"📊 Database Summary:")
            print(f"   - Ingredients: {ingredient_count}")
            print(f"   - Recipes: {recipe_count}\n")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
