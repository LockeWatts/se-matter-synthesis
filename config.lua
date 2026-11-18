-- All balance numbers live here.
local config = {}

-- Prefix for every prototype this mod adds.
config.prefix = "sems-"

-- New matter fusion recipes. Each one costs the same inputs as SE's
-- "Matter fusion (Iron)" (which yields 10 iron ore in 1 second).
--   type   : "fluid" or "item"
--   amount : yield per craft, before productivity
--   time   : craft time in seconds (the Material fabricator has crafting speed 4)
--   requires : technology that normally unlocks the product; it becomes a prerequisite
--              of Matter fusion so the product cannot be reached before it
config.products = {
  { type = "fluid", name = "water",         amount = 500, time = 1, order = "a" },
  { type = "fluid", name = "petroleum-gas", amount = 100, time = 1, order = "b" },
  { type = "fluid", name = "light-oil",     amount = 100, time = 1, order = "c" },
  { type = "fluid", name = "heavy-oil",     amount = 100, time = 1, order = "d" },
  { type = "fluid", name = "se-methane-gas", amount = 100, time = 1, order = "e", requires = "se-processing-methane-ice" },
  { type = "item",  name = "coal",          amount = 10,  time = 1, order = "f" },
}

-- The recipes above are added to SE's own "Matter fusion" technology. Its research
-- cost is raised to this many units to pay for them (SE's own value is 500).
-- Set to nil to leave SE's cost alone.
config.fusion_tech_count = 1000

-- Infinite research: productivity added to every matter fusion recipe per level (0.1 = +10%).
config.productivity_per_level = 0.1

-- Science pack count for level L of the infinite research.
config.productivity_cost_formula = "1000*L"

-- Factorio caps recipe productivity at +300% unless the recipe raises the cap.
-- 100 = +10,000%, which at +10% per level is reached at level 1000.
config.maximum_productivity = 100

-- Advanced matter fusion: a strictly better version of every fusion recipe.
-- The data card is replaced by a fusion matrix that is always returned, and
-- there is no contaminated scrap or junk data.
config.advanced = {
  -- One advanced craft equals this many basic crafts (inputs, outputs and time).
  batch = 5,
  -- Coolant used per unit of product, relative to the basic recipe (0.2 = one fifth).
  coolant_factor = 0.2,
  -- Research units. Uses the same science packs as SE's Naquium cube technology.
  tech_count = 1000,
  -- Fusion matrix recipe, crafted in the Material fabricator.
  matrix_time = 30,
  matrix_ingredients = {
    { type = "item",  name = "se-naquium-cube",           amount = 1 },
    { type = "item",  name = "se-superconductive-cable",  amount = 4 },
    { type = "item",  name = "se-fusion-test-data",       amount = 10 },
    { type = "fluid", name = "se-particle-stream",        amount = 100 },
  },
  -- Tint applied to SE's Matter fusion technology icon for the advanced technology.
  tint = { r = 1, g = 0.55, b = 0.95 },
}

return config
