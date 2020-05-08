# High-Level Tasks
## 1. BJCP vs. Empirical
Exploratory data analysis
Compare the BJCP and real recipes:
* (ABV, IBU, colour)
* Characteristic ingredients

Deliverable? Interactive plots / tables
* Lookup table of style -> ranges of properties.
* IBU vs ABV (Rory likes this)
  * Color of point represents SRM.
  * Size of point could represent number of recipes or spread of data.
  * Size could also be spread of data
  * Could also do contour lines
  * FG, OG
  * Matrix plots - can show relationships of all 4 variables. Highlighting section of data in 1 plot shows same points in other relationships
* Word cloud
  * Beer names
  * Hop varieties
  * Styles?
* Hop vs boil time (Rory also likes this)
  * Show amount of hop added at each point in boil time for different beers
  * Compare style A to style B
  * Show how this changes over time

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
