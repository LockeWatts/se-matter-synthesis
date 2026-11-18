-- This mod adds recipes to technologies that a save may already have researched.
-- Factorio only applies a technology's unlocks when it is researched, so grant
-- them here for every force that already has the technology.
local technologies = { "se-space-matter-fusion", "sems-advanced-matter-fusion" }

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
