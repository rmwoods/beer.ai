Need to determine how to store these recipes.

1. Determine batch size - `recipe.boil_size` (could be in G or L). Want to normalize grains to this.
  - this could be pre-boil volume (before you've lost water to boil). There is also the amount that goes to the fermenter, and the amount that goes to the bottles.
  - `recipe.batch_size` looks to be post boil?
2. Start with fermentables: recipe.fermentables
  1. name + origin should be unique (though it looks like origin could be part of name)
  2. Quantity we care about is fermentable.amount (kg) - should be normalized to boil size
  3. All fermentables go in at the same time, so order is not important here. These get "mashed" (steeped in warm water)
  4. Amount of time and temperature will change for above.
  5. Can sometimes have multiple steps of mashing (e.g. temp 1 for t1 and temp 2 for t2).
  - Note - all grains are almost always involved in all the mashing
-  Liquid strained from solids, but this always happens. Not part of the recipe.
3. Boil - usually boiled 60-90 minutes. Time is specified in `recipe.boil_time` (minutes)
  - Different intervals, we add hops. `recipe.hops`
  - Recipes specify when to add hops by the amount of time _left_ in the boil
  - Need amount, alpha acid, form. hop.amount (g), hop.alpha (mass percentage?), hop.form (string, e.g. "Leaf", "Pellet").
    - Need to normalize such that quantity of alpha acids is consistent if percent alpha acids changes.
    - We need to normalize amount to the boil size
    - Note: technically, we should take into account how boil size changes as time progresses but we probably don't need to.
  1. Boil `time` minutes
  2. e.g. hop1 @ 90 min, hop2 @ 45 min, hop3 @ 10 min (boil hop 1 for 90 minutes, add hop 2 after 45 minutes, add hop 2 after 80 minutes)
  3. Can also get hops at 0, e.g. after boil ends (flame out hopping or whirlpool hopping).
  - Sometimes other ingredients added to a boil, e.g. yeast nutrients or finings, but these are personal preference and we can ignore them.
4. Fermentation. Note - this is super important, but home brew recipes don't really specify this in any detail. All we can do is pick out yeast. recipe.yeasts
  1. Need yeast name and laboratory: yeast.name, yeast.laboratory
  2. There would be a lot more details here, but not in these recipes.
5. Potentially dry hopping. Specified in the recipe.hops list. recipe.hops
  - Dry hop step is specified by hop.use, e.g. "Boil" or "Dry Hop"
  1. Need name, amount (g), time (minutes). Amount should be normalized to `batch_size`, `hop.name`, `hop.amount`, `hop.time`
6. Misc category
  - These things can go in with the fermentation, after the fermentation, sometimes in the boil, sometimes in the mash.
  - misc.name specifies unique item
  - misc.use, misc.time (minutes? days?) specifies where in the recipe the ingredient goes and for how long. Normalization will depend on what stage it is added.
  - misc.amount (kg?) specify how much
7. <EOR> (end of recipe)

Extra notes:
   - May be worth enforcing ordering of ingredients:
      1. fermentables
      2. hops + boil
      3. Yeasts
      ?. Misc can go anywhere
   - Probably want to scale everything to a boil size of 1
