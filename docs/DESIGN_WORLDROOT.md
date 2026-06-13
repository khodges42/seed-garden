# Worldroot Design Document v1

## Purpose

Worldroot is a persistent ecosystem simulation that evolves one cycle per day.

It is not a game.

It is not intended to be optimized.

It is not intended to be won.

Its purpose is to generate emergent history.

Worldroot transforms simple ecological rules into stories.

The simulation is intended to evoke:

* Mystery
* Wonder
* Impermanence
* Renewal
* Curiosity

The simulation should feel alive without becoming complex.

---

# Core Philosophy

Worldroot remembers only what matters.

Most events are forgotten.

History becomes mythology.

The world should accumulate stories, not logs.

---

# Simulation Model

Worldroot is a finite grid.

Initial implementation:

```txt
20 x 20
```

Future implementations may allow larger worlds.

Each cell contains one entity.

---

# Cell Types

```txt
. Empty / Void
, Sprout
* Bloom
T Tree
o Wanderer
x Rot
~ Water
# Stone
```

---

# Symbolic Meaning

The simulation does not use these meanings internally.

The narrator may use them.

```txt
Empty     -> Void
Sprout    -> Possibility
Bloom     -> Life
Tree      -> Memory
Wanderer  -> Change
Rot       -> Death / Return
Water     -> Potential
Stone     -> Permanence
```

These meanings are descriptive only.

Simulation rules should not depend on symbolism.

---

# Cycles

The world advances one cycle per day.

Every entity tracks:

```json
{
  "kind": "tree",
  "cycles": 14
}
```

Cycles represent persistence.

The world itself also tracks cycles.

```json
{
  "world_cycle": 412
}
```

Entity cycles and world cycles are separate concepts.

---

# World Generation

The first world is generated from:

```txt
seed
+
I Ching
```

The generated world becomes persistent.

After creation:

```txt
previous state
+
seed
+
I Ching
```

produce the next state.

---

# I Ching Relationship

The I Ching influences Worldroot.

Worldroot is considered a reflection of the current hexagram.

The hexagram modifies:

```txt
growth
rot
movement
```

The exact modifier values are implementation details.

Worldroot should never generate its own oracle.

The oracle comes from Seed Garden.

---

# Water

Water is stable.

Water rarely changes.

Water serves as a source of growth.

Sprouts and blooms near water grow more easily.

Water creates recognizable geography.

---

# Stone

Stone is stable.

Stone rarely changes.

Stone creates boundaries.

Stone serves as an anchor for world structure.

---

# Sprouts

Sprouts represent emerging life.

Sprouts may:

```txt
grow into blooms
die into emptiness
```

Sprouts are common.

Sprouts are short-lived.

---

# Blooms

Blooms represent flourishing life.

Blooms may:

```txt
spread
become trees
die into rot
```

Blooms are the primary growth stage.

---

# Trees

Trees represent memory.

Trees are long-lived.

Trees may:

```txt
spread slowly
survive many cycles
die
```

Trees are candidates for naming.

---

# Rot

Rot represents decay.

Rot is not evil.

Rot is necessary.

Rot may:

```txt
spread
consume life
return to emptiness
```

Rot creates cycles.

Without rot, the world stagnates.

---

# Wanderers

A wanderer is anything that wanders and affects change.

Examples:

* Spirit
* Traveler
* Cat
* Shaman
* Lost soul

Wanderers move.

Wanderers disrupt stable patterns.

Wanderers may:

```txt
encourage growth
spread decay
trigger events
```

Wanderers are intentionally unpredictable.

---

# Naming

Most entities are anonymous.

Rare entities may become named in V2, V1 names will be generic as in "Tree of 42 cycles" or "The Oldest Wanderer"

Requirements:

```txt
must survive many cycles
must be rare
must not exceed system limits
```

Example:

```json
{
  "kind": "tree",
  "cycles": 84,
  "name": "Ashroot"
}
```

Named entities become part of history.

---

# Death

Death is essential.

Everything can die.

Named entities can die.

Deaths may become chronicle events.

A world without death becomes stagnant.

---

# Records

Worldroot tracks records.

Examples:

```txt
Oldest Tree
Largest Bloom
Longest Era
Greatest Rot Tide
Most Wanderers
```

Records persist.

---

# Eras

History is divided into eras.

An era begins when conditions change significantly.

Examples:

```txt
massive bloom
collapse
extinction
rot tide
population shift
```

Era boundaries are important historical events.

---

# Chronicle

The chronicle stores:

```txt
Era Changes
Named Births
Named Deaths
Records
Major Events
```

The chronicle does not store:

```txt
Every Cycle
Every Grid
Every Population Count
```

History is compressed.

---

# Events

Events emerge from world conditions.

Examples:

```txt
The First Bloom

The Rot Tide

The Last Tree Fell

The Wanderers Vanished

The Returning Waters
```

Events are generated from state transitions.

Events should feel mythic.

---

# Determinism

Worldroot must be deterministic.

Given:

```txt
same previous state
same seed
same hexagram
```

the same next state must be produced.

Global randomness is prohibited.

Hash-based randomness should be used.

---

# Design Goal

Worldroot should produce stories that appear intentional without actually being authored.

The simulation should be simple enough to understand.

The resulting mythology should be richer than the underlying rules.

---

# Details

My recommendation: keep **Worldroot v1 extremely small**, but make the rules expressive.

## 1. Use one entity per cell

Do not model inventories, multiple organisms, energy pools, etc.

```json
{
  "kind": "tree",
  "cycles": 14,
  "name": null
}
```

That’s enough.

## 2. Use this lifecycle

```txt
empty → sprout → bloom → tree
             ↘ rot → empty
```

Water and stone are mostly permanent.

Wanderers move around and perturb things.

## 3. Simple base rules

Per cycle:

```txt
Empty near life may become sprout.
Sprout may become bloom.
Bloom may become tree.
Overcrowded bloom/tree may become rot.
Rot eventually becomes empty.
Wanderers move to nearby cells.
Wanderers sometimes create sprout or rot.
```

That’s your whole engine.

## 4. Let I Ching modify probabilities only

Do not make 64 custom rule sets yet.

Just:

```json
{
  "growth": 0.15,
  "rot": -0.05,
  "movement": 0.10
}
```

Then apply those to base probabilities.

## 5. Notable Entities

Most entities are anonymous.

Rare entities may become notable if they survive for an unusually long time or play a significant role in the ecosystem.

Notable entities are not given randomly generated names.

Instead, they are referred to by descriptive titles derived from their characteristics.

Examples:

Tree of 42 Cycles
Tree of 103 Cycles
The Oldest Wanderer
The Last Bloom
The Western Tree
The Eastern Wanderer
The Old Root
The First Tree
tree with cycles >= 30
wanderer with cycles >= 12

may become notable.

Hard cap:

max_notable = max(3, width // 4)

For a 20x20 world, this produces at most 5 notable entities.

Notable entities are eligible for inclusion in the chronicle.

Examples:

The Tree of 42 Cycles fell during the Rot Tide.

The Oldest Wanderer vanished during the Quiet Era.

The First Tree endured for 103 cycles.

When a notable entity dies, the event may be recorded permanently in the chronicle.

Notability exists to create continuity and mythology, not individuality.


I particularly like that last line:

> **Notability exists to create continuity and mythology, not individuality.**

It feels very aligned with the tone of Worldroot. The world remembers *that something endured*, not necessarily its proper name.

## 6. Use era changes sparingly

V1 triggers:

```txt
life_count == 0
rot_count > 30% of grid
life_count changes by >35%
named entity dies
```

That’s enough to make the world feel historical without spam.

## 7. Keep the chronicle tiny

```json
{
  "current_era": {},
  "eras": [],
  "notable_events": [],
  "records": {}
}
```

Caps:

```txt
eras: 12
notable_events: 25
```

## 8. Make Worldroot output both machine and poem

```json
{
  "cycle": 12,
  "ascii": "...",
  "stats": {},
  "events": [],
  "caption": "Rot gathers beneath the western trees."
}
```

The caption can be simple template text in v1.

