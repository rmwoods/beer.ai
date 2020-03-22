# High-Level Tasks
## 1. BJCP vs. Empirical
Exploratory data analysis
Compare the BJCP and real recipes:
* (ABV, IBU, colour)
* Characteristic ingredients

## 2. Generate recipe for style X
For a given style, what is a "typical" recipe?
Generate a vector in ingredient-space.

## 3. Generate recipe interpolating between styles X, Y
For a given set of styles, generate a recipe that captures the defining characteristics of both styles. 

## 4. Where does a recipe sit in its style? 
For a given style and recipe, how "typical" is the recipe?

## 5. Generate random recipe
Generate a recipe that is:
* Uncommon
* Not terrible
  * Identify patterns in ingredients that produce good flavours
  * Which are still uncommon

# Low-Level Tasks
## Documentation
* Add tabular data dictionary for fields in `all\_recipes.h5` 
  * Core
  * Ingredients
* Add super high level overview of data pipeline
  * .xml ---(converter.py)---> .h5 ---(recipe2vec)---> .h5   
