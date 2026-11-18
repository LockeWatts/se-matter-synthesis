import lupa, sys
L = lupa.LuaRuntime(unpack_returned_tuples=True)
MOD = sys.argv[1]
L.execute(f'package.path = "{MOD}/?.lua;" .. package.path')
L.execute(r'''
function table.deepcopy(o) if type(o) ~= "table" then return o end local c = {} for k,v in pairs(o) do c[k] = table.deepcopy(v) end return c end
package.preload["util"] = function() return { technology_icon_constant_recipe_productivity = function(icon)
  return { {icon = icon, icon_size = 256}, {icon = "__core__/graphics/icons/technology/constants/constant-recipe-productivity.png", icon_size = 128, scale = 0.5, shift = {50, 50}, floating = true} } end } end
data = { raw = { recipe = {}, technology = {}, item = {}, fluid = {} } }
function data:extend(list) for _, p in ipairs(list) do assert(p.type and p.name, "prototype needs type and name") assert(not data.raw[p.type][p.name], "duplicate " .. p.name) data.raw[p.type][p.name] = p end end
local function icon(n) return "__base__/graphics/icons/" .. n .. ".png" end
data.raw.item["se-naquium-cube"] = {type="item", name="se-naquium-cube", icon="__space-exploration-graphics__/graphics/icons/naquium-cube.png", icon_size=64, stack_size=8, order="n-c", subgroup="naquium"}
data.raw.item["se-naquium-ore"] = {type="item", name="se-naquium-ore", icon="naq.png", icon_size=64}
data.raw.item["uranium-ore"] = {type="item", name="uranium-ore", icon="u.png", icon_size=64}
for _, n in ipairs({"iron-ore", "copper-ore", "coal"}) do data.raw.item[n] = {type="item", name=n, icon=icon(n), icon_size=64} end
for _, n in ipairs({"water", "petroleum-gas", "light-oil", "heavy-oil", "se-methane-gas"}) do data.raw.fluid[n] = {type="fluid", name=n, icon=icon("fluid/" .. n), icon_size=64} end
local function fusion(name, product)
  return { type="recipe", name=name, categories={"space-materialisation"}, enabled=false, energy_required=1,
    ingredients = { {type="item", name="se-fusion-test-data", amount=1, ignored_by_stats=1}, {type="fluid", name="se-particle-stream", amount=50}, {type="fluid", name="se-space-coolant-supercooled", amount=25} },
    results = { product, {type="item", name="se-contaminated-scrap", amount=1},
      {type="item", name="se-fusion-test-data", amount=1, shared_probability={min=0, max=0.99}, ignored_by_stats=1},
      {type="item", name="se-junk-data", amount=1, shared_probability={min=0.99, max=1}},
      {type="fluid", name="se-space-coolant-hot", amount=25} },
    icons = { {icon="blank.png", scale=0.5, icon_size=64}, {icon="particle-stream.png", scale=0.33, shift={8,-8}, icon_size=64},
      {icon=icon("iron-ore"), scale=0.33, shift={-8,8}, icon_size=64}, {icon="transition-arrow.png", scale=0.5, icon_size=64} },
    subgroup="materialisation", order="a-b", localised_name={"recipe-name.se-matter-fusion-to", {"item-name.iron-ore"}} }
end
data:extend({ fusion("se-matter-fusion-iron", {type="item", name="iron-ore", amount=10}),
  fusion("se-matter-fusion-copper", {type="item", name="copper-ore", amount=10}),
  (function() local r = fusion("se-matter-fusion-uranium", {type="item", name="uranium-ore", amount_min=1, amount_max=1, independent_probability=0.5}) r.energy_required = 6 return r end)(),
  (function() local r = fusion("se-matter-fusion-dirty", {type="item", name="se-contaminated-scrap", amount=15}) table.remove(r.results, 2) return r end)(),
  { type="technology", name="se-naquium-cube", icon="cube.png", icon_size=128, unit={count=100, time=60, ingredients={{"automation-science-pack",1},{"se-energy-science-pack-4",1},{"se-deep-space-science-pack-1",1}}} },
  { type="technology", name="se-processing-methane-ice", icon="m.png", icon_size=128, unit={count=100, time=60, ingredients={{"automation-science-pack",1}}} },
  { type="recipe", name="se-antimatter-stream", categories={"space-materialisation"}, ingredients={{type="fluid", name="se-particle-stream", amount=50}}, results={{type="fluid", name="se-antimatter-stream", amount=50}} },
  { type="technology", name="se-space-matter-fusion", icon="__space-exploration-graphics__/graphics/technology/material-fabricator.png", icon_size=128, order="e-g",
    unit={count=500, time=60, ingredients={{"automation-science-pack",1},{"se-energy-science-pack-4",1}}} } })
se_procedural_tech_exclusions = {"qol-"}
''')
L.execute('dofile("%s/data.lua")' % MOD)
L.execute('dofile("%s/data-final-fixes.lua")' % MOD)
print(L.eval(r'''(function()
  local out = {}
  local function ser(v, d) if type(v) ~= "table" then return tostring(v) end local keys = {} for k in pairs(v) do keys[#keys+1] = k end table.sort(keys, function(a,b) return tostring(a) < tostring(b) end)
    local parts = {} for _, k in ipairs(keys) do parts[#parts+1] = (type(k)=="number" and "" or (k .. "=")) .. ser(v[k]) end return "{" .. table.concat(parts, ", ") .. "}" end
  local names = {} for n in pairs(data.raw.recipe) do names[#names+1] = n end table.sort(names)
  for _, n in ipairs(names) do local r = data.raw.recipe[n]
    out[#out+1] = "RECIPE " .. n .. "  t=" .. tostring(r.energy_required) .. " allow_prod=" .. tostring(r.allow_productivity) .. " max_prod=" .. tostring(r.maximum_productivity) .. " order=" .. tostring(r.order)
    for _, res in ipairs(r.results) do out[#out+1] = "    -> " .. ser(res) end
    out[#out+1] = "    <- " .. ser(r.ingredients) if n:find("sems") and r.icons then out[#out+1] = "    icons: " .. #r.icons .. " layers, last " .. ser(r.icons[#r.icons]) .. "\n    name: " .. ser(r.localised_name) end end out[#out+1] = "ITEM " .. ser(data.raw.item["sems-fusion-matrix"])
  for _, n in ipairs({"se-space-matter-fusion", "sems-advanced-matter-fusion", "sems-matter-fusion-productivity-1"}) do out[#out+1] = "TECH " .. n .. "\n    " .. ser(data.raw.technology[n]) end
  out[#out+1] = "exclusions: " .. ser(se_procedural_tech_exclusions)
  out[#out+1] = "template untouched icon: " .. data.raw.recipe["se-matter-fusion-iron"].icons[3].icon
  return table.concat(out, "\n") end)()'''))
