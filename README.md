# Fridge Recipe Suggester

A Python CLI that suggests recipes based on ingredients you have on hand, powered by the Claude API with prompt caching.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

**Interactive mode** — prompts you for ingredients:
```bash
python fridge.py
```

**Direct mode** — pass ingredients as arguments:
```bash
python fridge.py eggs milk cheese
python fridge.py "chicken breast" garlic onion tomatoes
python fridge.py spinach feta lemon garlic
```

## Prompt Caching

The system prompt is cached using Anthropic's ephemeral cache (5-minute TTL).
The first call writes the cache; subsequent calls within the window read from it
at ~10% of normal input token cost. Each run prints whether it hit or missed the cache.

## Example Output

```
Finding recipes for: eggs, spinach, feta, garlic...

============================================================
  Recipes using: eggs, spinach, feta, garlic
============================================================

### 1. Spinach and Feta Frittata
...

------------------------------------------------------------
  Cache hit  — 843 tokens read from cache (saved ~90%)
  Tokens: 47 input, 312 output
```
