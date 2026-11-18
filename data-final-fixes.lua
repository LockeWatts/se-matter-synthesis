local lib = require("lib")

-- Done last so fusion recipes added or changed by other mods are covered too.
for _, name in ipairs(lib.fusion_recipe_names()) do
  lib.prepare_for_productivity(data.raw.recipe[name])
end

local tech = data.raw.technology[lib.productivity_tech_name]
if tech then tech.effects = lib.productivity_effects() end
