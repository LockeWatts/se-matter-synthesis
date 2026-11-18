# Space Exploration: Matter Synthesis

Extends the Material fabricator in [Space Exploration](https://mods.factorio.com/mod/space-exploration) so that, in the very late game, matter fusion can replace mining entirely.

Space Exploration's Matter fusion already turns particle stream into ores. This mod fills in what is missing, makes the process cleaner to run at scale, and lets research push its output up without limit.

## What it adds

**More fusion products.** Matter fusion now also unlocks recipes for:

- Water
- Petroleum gas, light oil and heavy oil
- Methane gas
- Coal

Together with Space Exploration's own ore recipes, these cover every raw input the fusion process itself consumes.

**Advanced matter fusion.** A later technology, after Naquium cube, with a better version of every fusion recipe:

- Uses a fusion matrix, a permanent catalyst that is always returned, in place of the fusion test data card that is slowly used up.
- Produces no contaminated scrap and no junk data.
- Needs one fifth of the coolant.
- Runs in batches five times larger, so the catalyst only cycles once per batch.
- Adds a naquium ore recipe that has no basic version.

**Matter fusion productivity.** An infinite research giving +10% output per level on every matter fusion recipe. Only the product is increased; catalysts and coolant are not duplicated.

## Changes to Space Exploration

- The Matter fusion technology costs 1000 units, up from 500, and requires Methane ice processing.
- Matter fusion recipes accept productivity from the research above, up to +10,000%.

Nothing else in Space Exploration is changed. Other Material fabricator recipes, such as antimatter, get no productivity.

## Requirements

- Factorio 2.1
- Space Exploration 0.7.64 or later

Like Space Exploration itself, it cannot be used with Space Age.

## Balance

Yields, costs and the productivity rate are all set in `config.lua` inside the mod. There are no in-game settings yet.

## Credits

Space Exploration is by Earendel. This mod depends on it and contains none of its code or artwork.
