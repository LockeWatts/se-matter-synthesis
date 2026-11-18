-- This mod adds recipes to technologies that a save may already have researched.
-- Factorio only applies a technology's unlocks at the moment it is researched, so
-- whenever the mod is added or updated, grant them to every force that has it.
local technologies = { "se-space-matter-fusion", "sems-advanced-matter-fusion" }

script.on_configuration_changed(function()
  for _, force in pairs(game.forces) do
    for _, tech_name in pairs(technologies) do
      local tech = force.technologies[tech_name]
      if tech and tech.researched then
        for _, effect in pairs(tech.prototype.effects) do
          if effect.type == "unlock-recipe" and force.recipes[effect.recipe] then
            force.recipes[effect.recipe].enabled = true
          end
        end
      end
    end
  end
end)
