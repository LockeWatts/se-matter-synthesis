local config = require("config")

local lib = {}

lib.template_recipe_name = "se-matter-fusion-iron"
lib.template_product_name = "iron-ore"
lib.fusion_tech_name = "se-space-matter-fusion"
lib.naquium_cube_tech_name = "se-naquium-cube"
lib.naquium_cube_item_name = "se-naquium-cube"
lib.fusion_category = "space-materialisation"
lib.card_name = "se-fusion-test-data"
lib.junk_name = "se-junk-data"
lib.scrap_name = "se-contaminated-scrap"
lib.coolant_in_name = "se-space-coolant-supercooled"
lib.coolant_out_name = "se-space-coolant-hot"
lib.matrix_name = config.prefix .. "fusion-matrix"
lib.products_tech_name = config.prefix .. "matter-fusion-fluids"
lib.advanced_tech_name = config.prefix .. "advanced-matter-fusion"
lib.productivity_tech_name = config.prefix .. "matter-fusion-productivity-1"

-- Items that mark a recipe as matter fusion when they go in and come back out.
lib.catalysts = { lib.card_name, lib.matrix_name }

-- Results that are catalysts or recycled waste rather than product.
-- Productivity must not duplicate them.
lib.non_product_results = {
  [lib.card_name] = true,
  [lib.matrix_name] = true,
  [lib.junk_name] = true,
  [lib.coolant_out_name] = true,
}

local function has_entry(list, name)
  for _, entry in pairs(list or {}) do
    if (entry.name or entry[1]) == name then return true end
  end
  return false
end

local function has_category(recipe, category)
  if recipe.category == category then return true end
  for _, c in pairs(recipe.categories or {}) do
    if c == category then return true end
  end
  return false
end

-- A matter fusion recipe is anything made in the Material fabricator that uses
-- a fusion catalyst (catalyst in, same catalyst out).
function lib.is_fusion_recipe(recipe)
  if not has_category(recipe, lib.fusion_category) then return false end
  for _, catalyst in ipairs(lib.catalysts) do
    if has_entry(recipe.ingredients, catalyst) and has_entry(recipe.results, catalyst) then return true end
  end
  return false
end

function lib.fusion_recipe_names()
  local names = {}
  for name, recipe in pairs(data.raw.recipe) do
    if lib.is_fusion_recipe(recipe) then table.insert(names, name) end
  end
  table.sort(names)
  return names
end

-- Let productivity apply to the recipe, lift the cap, and shield the catalysts.
function lib.prepare_for_productivity(recipe)
  recipe.allow_productivity = true
  recipe.maximum_productivity = math.max(recipe.maximum_productivity or 3, config.maximum_productivity)
  for _, result in pairs(recipe.results or {}) do
    if lib.non_product_results[result.name] then
      result.ignored_by_productivity = result.amount or result.amount_max or 1
    end
  end
end

function lib.productivity_effects()
  local effects = {}
  for _, name in ipairs(lib.fusion_recipe_names()) do
    table.insert(effects, {
      type = "change-recipe-productivity",
      recipe = name,
      change = config.productivity_per_level,
    })
  end
  return effects
end

local function scale_amounts(entry, factor)
  for _, key in ipairs({ "amount", "amount_min", "amount_max" }) do
    if entry[key] then entry[key] = math.max(1, math.floor(entry[key] * factor + 0.5)) end
  end
end

local function strip_prefix(name)
  for _, prefix in ipairs({ config.prefix, "se-" }) do
    if string.sub(name, 1, #prefix) == prefix then return string.sub(name, #prefix + 1) end
  end
  return name
end

local function localised_product_name(product)
  local kind = product.type or "item"
  local proto = data.raw[kind] and data.raw[kind][product.name]
  if proto and proto.localised_name then return proto.localised_name end
  return { kind .. "-name." .. product.name }
end

-- Build the advanced version of a card-based fusion recipe: a larger batch with
-- the fusion matrix as a permanent catalyst, less coolant, and no waste.
-- Returns nil if the recipe has nothing left once the waste is removed.
function lib.make_advanced_recipe(base)
  local batch = config.advanced.batch
  local coolant_scale = batch * config.advanced.coolant_factor
  local recipe = table.deepcopy(base)
  recipe.name = config.prefix .. "advanced-" .. strip_prefix(base.name)
  recipe.energy_required = (base.energy_required or 0.5) * batch
  recipe.enabled = false
  recipe.order = "c-" .. (base.order or base.name)
  recipe.main_product = nil

  local ingredients = { { type = "item", name = lib.matrix_name, amount = 1, ignored_by_stats = 1 } }
  for _, ingredient in ipairs(recipe.ingredients or {}) do
    if ingredient.name ~= lib.card_name then
      scale_amounts(ingredient, ingredient.name == lib.coolant_in_name and coolant_scale or batch)
      table.insert(ingredients, ingredient)
    end
  end
  recipe.ingredients = ingredients

  local results, products = {}, {}
  for _, result in ipairs(recipe.results or {}) do
    local name = result.name
    if name == lib.coolant_out_name then
      scale_amounts(result, coolant_scale)
      table.insert(results, result)
    elseif name ~= lib.card_name and name ~= lib.junk_name and name ~= lib.scrap_name then
      scale_amounts(result, batch)
      table.insert(results, result)
      table.insert(products, result)
    end
  end
  if #products == 0 then return nil end
  table.insert(results, {
    type = "item", name = lib.matrix_name, amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1,
  })
  recipe.results = results

  recipe.localised_name = { "recipe-name." .. config.prefix .. "advanced-matter-fusion-to", localised_product_name(products[1]) }
  if recipe.icons then
    table.insert(recipe.icons, {
      icon = data.raw.item[lib.naquium_cube_item_name].icon,
      icon_size = data.raw.item[lib.naquium_cube_item_name].icon_size or 64,
      scale = 0.2 * 64 / (data.raw.item[lib.naquium_cube_item_name].icon_size or 64),
      shift = { -9, -9 },
      tint = config.advanced.tint,
    })
  end
  return recipe
end

-- Re-point the "to" layer of the template's transition icon at a new product.
function lib.swap_product_icon(icons, old_proto, new_proto)
  icons = table.deepcopy(icons)
  if not (icons and old_proto and old_proto.icon) then return icons end
  local new_icon = new_proto.icon or (new_proto.icons and new_proto.icons[1] and new_proto.icons[1].icon)
  local new_size = new_proto.icon_size or (new_proto.icons and new_proto.icons[1] and new_proto.icons[1].icon_size) or 64
  if not new_icon then return icons end
  for _, layer in pairs(icons) do
    if layer.icon == old_proto.icon then
      local old_size = layer.icon_size or 64
      layer.icon = new_icon
      layer.icon_size = new_size
      if layer.scale then layer.scale = layer.scale * old_size / new_size end
    end
  end
  return icons
end

-- A technology's icon as a layer list, optionally tinted.
function lib.tech_icons(tech, tint)
  local icons = tech.icons and table.deepcopy(tech.icons) or { { icon = tech.icon, icon_size = tech.icon_size or 256 } }
  if tint then
    for _, layer in pairs(icons) do layer.tint = tint end
  end
  return icons
end

-- Technology icon with the vanilla "recipe productivity" corner badge when available.
function lib.productivity_tech_icons(tech)
  local icons = lib.tech_icons(tech)
  if tech.icons then return icons end
  local ok, util = pcall(require, "util")
  if ok and type(util) == "table" and util.technology_icon_constant_recipe_productivity then
    local vanilla = util.technology_icon_constant_recipe_productivity(tech.icon)
    if vanilla and vanilla[2] then table.insert(icons, vanilla[2]) end
  end
  return icons
end

return lib
