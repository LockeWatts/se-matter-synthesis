local config = require("config")
local lib = require("lib")

local template = data.raw.recipe[lib.template_recipe_name]
local fusion_tech = data.raw.technology[lib.fusion_tech_name]
local cube_tech = data.raw.technology[lib.naquium_cube_tech_name]
local cube_item = data.raw.item[lib.naquium_cube_item_name]
if not (template and fusion_tech and cube_tech and cube_item) then
  error("se-matter-synthesis: could not find the Space Exploration prototypes this mod builds on ('" ..
    lib.template_recipe_name .. "', '" .. lib.fusion_tech_name .. "', '" .. lib.naquium_cube_tech_name ..
    "'). Space Exploration may have renamed them.")
end

-- Space Exploration rewrites the science packs and levels of other mods' leveled
-- technologies. This is its documented opt-out.
se_procedural_tech_exclusions = se_procedural_tech_exclusions or {}
table.insert(se_procedural_tech_exclusions, config.prefix)

--------------------------------------------------------------------------------
-- Water, oil products and coal
--------------------------------------------------------------------------------
-- Copies of "Matter fusion (Iron)" with the product swapped, so they always track
-- whatever inputs Space Exploration (or its compatibility patches) give that recipe.
local template_product = data.raw.item[lib.template_product_name]
local product_unlocks = {}

for _, def in ipairs(config.products) do
  local product_proto = data.raw[def.type] and data.raw[def.type][def.name]
  if product_proto then
    local recipe = table.deepcopy(template)
    recipe.name = config.prefix .. "matter-fusion-" .. def.name
    recipe.energy_required = def.time
    recipe.enabled = false
    recipe.order = "b-" .. def.order
    recipe.localised_name = { "recipe-name.se-matter-fusion-to", { def.type .. "-name." .. def.name } }
    recipe.icons = lib.swap_product_icon(template.icons, template_product, product_proto)

    local results = {}
    for _, result in ipairs(recipe.results) do
      if result.name ~= lib.template_product_name then table.insert(results, result) end
    end
    local product = { type = def.type, name = def.name, amount = def.amount }
    if def.type == "fluid" then
      -- After the hot coolant, so the coolant keeps its usual output port.
      table.insert(results, product)
    else
      table.insert(results, 1, product)
    end
    recipe.results = results

    data:extend({ recipe })
    table.insert(product_unlocks, { type = "unlock-recipe", recipe = recipe.name })
  end
end

local products_unit = table.deepcopy(fusion_tech.unit)
products_unit.count = config.products_tech_count
products_unit.count_formula = nil

--------------------------------------------------------------------------------
-- Advanced matter fusion
--------------------------------------------------------------------------------
local matrix = table.deepcopy(cube_item)
matrix.name = lib.matrix_name
matrix.localised_name = nil
matrix.localised_description = nil
matrix.pictures = nil
matrix.icon = lib.matrix_icon
matrix.icon_size = lib.matrix_icon_size
matrix.icons = nil
matrix.order = (cube_item.order or "") .. "-z[" .. lib.matrix_name .. "]"

local matrix_recipe = {
  type = "recipe",
  name = lib.matrix_name,
  categories = { lib.fusion_category },
  enabled = false,
  energy_required = config.advanced.matrix_time,
  ingredients = table.deepcopy(config.advanced.matrix_ingredients),
  results = { { type = "item", name = lib.matrix_name, amount = 1 } },
  always_show_made_in = true,
}

local advanced_unlocks = { { type = "unlock-recipe", recipe = lib.matrix_name } }
local advanced_recipes = {}
for _, name in ipairs(lib.fusion_recipe_names()) do
  local advanced = lib.make_advanced_recipe(data.raw.recipe[name])
  if advanced then
    table.insert(advanced_recipes, advanced)
    table.insert(advanced_unlocks, { type = "unlock-recipe", recipe = advanced.name })
  end
end

data:extend({ matrix, matrix_recipe })
data:extend(advanced_recipes)

--------------------------------------------------------------------------------
-- Technologies
--------------------------------------------------------------------------------
data:extend({
  {
    type = "technology",
    name = lib.products_tech_name,
    icons = lib.tech_icons(fusion_tech),
    order = (fusion_tech.order or "") .. "-a",
    effects = product_unlocks,
    prerequisites = { lib.fusion_tech_name },
    unit = products_unit,
  },
  {
    type = "technology",
    name = lib.advanced_tech_name,
    icons = lib.tech_icons(fusion_tech, config.advanced.tint),
    order = (fusion_tech.order or "") .. "-b",
    effects = advanced_unlocks,
    prerequisites = { lib.products_tech_name, lib.naquium_cube_tech_name },
    unit = {
      count = config.advanced.tech_count,
      time = cube_tech.unit.time or 60,
      ingredients = table.deepcopy(cube_tech.unit.ingredients),
    },
  },
  {
    type = "technology",
    name = lib.productivity_tech_name,
    icons = lib.productivity_tech_icons(fusion_tech),
    order = (fusion_tech.order or "") .. "-c",
    effects = lib.productivity_effects(),
    prerequisites = { lib.fusion_tech_name },
    unit = {
      count_formula = config.productivity_cost_formula,
      time = fusion_tech.unit.time or 60,
      ingredients = table.deepcopy(fusion_tech.unit.ingredients),
    },
    max_level = "infinite",
    upgrade = true,
  },
})
