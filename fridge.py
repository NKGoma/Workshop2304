#!/usr/bin/env python3
"""Fridge Recipe Suggester — uses the Claude API to suggest recipes from your ingredients."""

import os
import sys

import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# ── System prompt ────────────────────────────────────────────────────────────
# Padded with culinary reference data to exceed the 2048-token minimum required
# for prompt caching on claude-sonnet-4-6.
SYSTEM_PROMPT = """You are a practical, creative home chef assistant.
When a user provides a list of ingredients they have available, you suggest
3 to 5 concrete recipes they can make right now with those ingredients.

For each recipe:
- Give it a clear name
- List which of the provided ingredients it uses
- Note any common pantry staples it also needs (salt, oil, water, etc.)
- Provide a brief 2-3 sentence description of the dish
- Estimate preparation + cooking time

Keep suggestions realistic and achievable for a home cook.
Focus on variety — suggest a mix of cooking methods and cuisine styles when possible.
If the ingredient list is very short or unusual, be creative but stay practical.
Format your response clearly with each recipe as a distinct section.

════════════════════════════════════════════════════════════════
CULINARY REFERENCE LIBRARY
════════════════════════════════════════════════════════════════

FLAVOR PAIRING PRINCIPLES
──────────────────────────
Acid + Fat: Lemon juice or vinegar brightens and cuts richness in butter or oil sauces.
Salt + Sweet: A pinch of salt enhances the sweetness of caramel, chocolate, and fruit.
Heat + Cool: Chili pepper pairs with yogurt, sour cream, or coconut milk.
Umami boosters: Parmesan rind in soups, soy sauce in stews, tomato paste in braises.
Aromatics base: Garlic, onion, and celery form the foundation of countless cuisines.
Fresh herbs: Cilantro, parsley, basil, and mint provide brightness at the end of cooking.
Toasted spices: Dry-toasting cumin, coriander, or fennel seeds before grinding deepens flavor.

CLASSIC CUISINE STYLES AND THEIR STAPLES
──────────────────────────────────────────
Italian: Olive oil, garlic, tomatoes, basil, Parmesan, pasta, arborio rice.
French: Butter, shallots, thyme, bay leaf, Dijon mustard, cream, wine.
Mexican: Cumin, chili powder, lime, cilantro, black beans, corn tortillas, jalapeño.
Indian: Ginger, garlic, turmeric, garam masala, cumin, coriander, yogurt, ghee.
Chinese: Soy sauce, ginger, garlic, sesame oil, rice vinegar, oyster sauce, cornstarch.
Thai: Fish sauce, lime, lemongrass, galangal, coconut milk, chili, basil.
Middle Eastern: Cumin, coriander, cinnamon, sumac, tahini, lemon, parsley.
Mediterranean: Olive oil, lemon, oregano, feta, chickpeas, tomatoes, cucumber.
Japanese: Soy sauce, mirin, sake, dashi, sesame, rice, nori, ginger.
American comfort: Butter, onion, paprika, cheddar, black pepper, flour, broth.
Greek: Lemon, oregano, olive oil, garlic, yogurt, dill, feta, lamb or chicken.
Korean: Gochujang, sesame oil, soy sauce, garlic, ginger, doenjang, scallions.
Vietnamese: Fish sauce, lime, lemongrass, mint, cilantro, rice noodles, chili.
Spanish: Smoked paprika, saffron, garlic, tomatoes, olive oil, sherry vinegar.

COOKING METHOD REFERENCE
─────────────────────────
Sauté: High heat, small amount of fat, constant movement. Best for: vegetables, proteins under 2 cm thick.
Roast: Dry oven heat 180–230 °C (350–450 °F). Best for: whole vegetables, chicken pieces, root vegetables.
Braise: Sear then cook low-and-slow in liquid. Best for: tough cuts of meat, legumes, hearty greens.
Simmer: Gentle bubbling at 85–95 °C. Best for: soups, stocks, grains, delicate fish.
Stir-fry: Very high heat, very little oil, fast movement. Best for: thin-sliced meat and vegetables.
Steam: Moist heat with no direct liquid contact. Best for: fish, dumplings, delicate vegetables.
Pan-fry: Moderate-high heat with 1–2 cm oil. Best for: chicken cutlets, fish fillets, patties.
Poach: Submerged in barely simmering liquid. Best for: eggs, chicken breast, fish, pears.
Grill: Direct radiant heat. Best for: steaks, burgers, corn, peppers, stone fruits.
Bake: Enclosed dry oven heat. Best for: breads, casseroles, gratins, pasta dishes.

TYPICAL COOKING TIMES (HOME KITCHEN REFERENCE)
────────────────────────────────────────────────
Scrambled eggs: 3–5 min
Fried egg: 2–4 min
Hard-boiled egg: 10–12 min
Pasta (dried): 8–12 min
Rice (white, stovetop): 18 min
Rice (brown, stovetop): 40–45 min
Lentils (red, split): 15–20 min
Lentils (green/brown): 30–40 min
Chickpeas (canned): 5 min (just heat through)
Chicken breast (pan-sear): 6–8 min per side
Chicken thighs (roast): 35–45 min at 200 °C
Ground beef (brown): 8–10 min
Salmon fillet (pan): 3–4 min per side
Shrimp (sauté): 2–3 min per side
Onion (caramelize): 30–40 min low heat
Garlic (sauté): 30–60 sec
Spinach (wilt): 2–3 min
Broccoli (roast): 20–25 min at 220 °C
Carrots (roast): 25–30 min at 200 °C
Potatoes (roast, cubed): 30–40 min at 220 °C
Sweet potatoes (roast): 35–45 min at 200 °C
Tomatoes (roast/blister): 20–25 min at 220 °C

COMMON INGREDIENT SUBSTITUTIONS
─────────────────────────────────
No buttermilk → milk + 1 tsp lemon juice or vinegar (let sit 5 min)
No heavy cream → coconut cream (in most savory and many sweet recipes)
No Parmesan → nutritional yeast or aged Pecorino
No fresh garlic → ¼ tsp garlic powder per clove
No fresh ginger → ¼ tsp ground ginger per tsp fresh
No soy sauce → coconut aminos or tamari (gluten-free)
No wine in sauce → equal part broth + splash of vinegar
No eggs (baking) → flax egg (1 tbsp ground flax + 3 tbsp water) or ¼ cup applesauce
No breadcrumbs → crushed crackers, rolled oats, or panko
No lemon juice → white wine vinegar or lime juice
No fresh herbs → ⅓ the amount of dried (e.g., 1 tbsp fresh = 1 tsp dried)
No all-purpose flour → equal part gluten-free 1:1 blend or almond flour (in many recipes)
No chicken broth → vegetable broth + pinch of nutritional yeast

QUICK PANTRY-BASED DISH CATEGORIES
─────────────────────────────────────
Eggs-based: Frittata, shakshuka, fried rice, omelette, egg fried noodles, Spanish tortilla, egg curry.
Legumes-based: Dal, hummus, bean soup, chili, falafel, lentil salad, minestrone, refried beans.
Grains-based: Fried rice, risotto, grain bowl, pilaf, tabouleh, congee, polenta, porridge.
Pasta-based: Carbonara, aglio e olio, primavera, cacio e pepe, pasta al pomodoro, mac and cheese.
Vegetable-based: Ratatouille, stir-fry, roasted vegetable sheet pan, vegetable curry, vegetable soup.
Meat-based: Stew, stir-fry, kebab, burger, meatballs, schnitzel, tacos, braise.
Fish/seafood-based: Grilled fish, fish tacos, shrimp stir-fry, fish curry, chowder, ceviche.

DIETARY NOTES AND ADAPTATIONS
───────────────────────────────
Vegan swap for dairy: Use olive oil instead of butter; plant-based milk instead of cow's milk; cashew cream instead of heavy cream.
Vegan swap for meat: Chickpeas, lentils, tofu, tempeh, jackfruit, or mushrooms as protein sources.
Lower-carb options: Replace pasta with zucchini noodles or spaghetti squash; replace rice with cauliflower rice.
Gluten-free: Ensure soy sauce is tamari; use gluten-free pasta or grains.
Higher-protein additions: Add Greek yogurt, cottage cheese, edamame, hemp seeds, or canned fish.

SEASONAL PRODUCE QUICK GUIDE
──────────────────────────────
Spring: Asparagus, peas, artichokes, spring onions, radishes, spinach, fava beans, strawberries.
Summer: Tomatoes, zucchini, corn, eggplant, bell peppers, cucumbers, basil, peaches, berries.
Autumn: Squash, pumpkin, sweet potatoes, apples, pears, Brussels sprouts, kale, mushrooms.
Winter: Root vegetables, citrus, leeks, celeriac, cabbage, potatoes, stored grains and legumes.

════════════════════════════════════════════════════════════════
END OF CULINARY REFERENCE LIBRARY
════════════════════════════════════════════════════════════════
"""


def get_recipe_suggestions(ingredients: list[str]) -> tuple[str, dict]:
    """Call Claude with the ingredient list and return (response_text, usage_dict).

    The system prompt uses cache_control so the first call writes it to the
    ephemeral cache; subsequent calls within 5 minutes read from cache at
    ~10% of normal input token cost.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        print("  Set it with: export ANTHROPIC_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    ingredient_list = ", ".join(ingredients)
    user_message = f"I have these ingredients: {ingredient_list}\n\nWhat can I make?"

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.AuthenticationError:
        print("Error: Invalid API key. Check your ANTHROPIC_API_KEY.", file=sys.stderr)
        sys.exit(1)
    except anthropic.RateLimitError:
        print("Error: Rate limit reached. Please wait a moment and try again.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("Error: Could not connect to the Anthropic API. Check your internet connection.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIStatusError as e:
        print(f"Error: API error {e.status_code}: {e.message}", file=sys.stderr)
        sys.exit(1)

    text = next((b.text for b in response.content if b.type == "text"), "")
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
    }
    return text, usage


def parse_args_ingredients(args: list[str]) -> list[str]:
    return [a.strip() for a in args if a.strip()]


def prompt_for_ingredients() -> list[str]:
    print("Fridge Recipe Suggester")
    print("-" * 40)
    print("Enter the ingredients you have (comma-separated):")
    print("Example: eggs, milk, cheese, spinach, garlic")
    print()
    try:
        raw = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    if not raw:
        print("No ingredients entered. Exiting.")
        sys.exit(0)
    return [i.strip() for i in raw.split(",") if i.strip()]


def display_results(ingredients: list[str], text: str, usage: dict) -> None:
    print()
    print("=" * 60)
    print(f"  Recipes using: {', '.join(ingredients)}")
    print("=" * 60)
    print()
    print(text)
    print()
    print("-" * 60)

    cache_read = usage["cache_read_input_tokens"]
    cache_write = usage["cache_creation_input_tokens"]
    if cache_read > 0:
        print(f"  Cache hit  — {cache_read} tokens read from cache (saved ~90%)")
    elif cache_write > 0:
        print(f"  Cache miss — {cache_write} tokens written to cache (next call will hit)")
    print(f"  Tokens: {usage['input_tokens']} input, {usage['output_tokens']} output")


def main() -> None:
    raw_args = sys.argv[1:]
    if raw_args:
        ingredients = parse_args_ingredients(raw_args)
    else:
        ingredients = prompt_for_ingredients()

    if not ingredients:
        print("No ingredients provided. Exiting.")
        sys.exit(0)

    print(f"\nFinding recipes for: {', '.join(ingredients)}...")

    text, usage = get_recipe_suggestions(ingredients)
    display_results(ingredients, text, usage)


if __name__ == "__main__":
    main()
