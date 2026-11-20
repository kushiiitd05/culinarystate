// Self-written demo recipes, one per engine path, scored on 17 Nov 2026 by how much state the engine fills
// (cut, lid, stated time -> simulated food temperature and thermal dose) and whether a same-process public
// reference recipe exists. Different dishes, not variations of one.

export type Preset = { label: string; text: string; question: string; shows: string };
export type PresetGroup = { group: string; hint: string; presets: Preset[] };

export const PRESET_GROUPS: PresetGroup[] = [
  {
    group: "Fix my dish", hint: "state-aware advice: the model gets the step-by-step state, simulation and a similar public recipe",
    presets: [
      { label: "★ Carrots came out mushy", shows: "simulated thermal dose, cut size, lid",
        text: "Peel and dice the carrots. Boil the carrots in water with the lid on for 10 minutes. Drain the carrots.",
        question: "My carrots came out too soft and mushy. What should I change next time?" },
      { label: "Eggs too salty", shows: "salt tracked through the lot, butter as fat",
        text: "Crack the eggs into a bowl and whisk with salt. Melt the butter in a pan over medium heat. Pour in the eggs and stir for 3 minutes. Add the grated cheese and garlic powder. Cook for 1 minute.",
        question: "I added too much salt to the scrambled eggs. How can I save them?" },
      { label: "Roast potatoes soggy", shows: "two heat steps: boil then roast",
        text: "Peel and cut the potatoes into chunks. Boil the potatoes in water for 8 minutes. Drain the potatoes. Roast the potatoes in oil in the oven at 200 C for 40 minutes.",
        question: "My roast potatoes came out soggy, not crispy. What went wrong?" },
      { label: "Onions burned", shows: "frying, simulated thermal dose",
        text: "Slice the onions. Fry the onions in butter over high heat for 10 minutes.",
        question: "My onions burned. How do I avoid it next time?" },
      { label: "Rice mushy", shows: "simmer at 90 °C with the lid on",
        text: "Rinse the rice. Simmer the rice in water with the lid on for 15 minutes.",
        question: "My rice turned out mushy and sticky. What should I change?" },
      { label: "Pasta · vinegar by mistake", shows: "acid in the cooking water",
        text: "Boil the pasta in water with vinegar and the lid off for 10 minutes. Drain the pasta.",
        question: "Oops, I boiled the pasta with vinegar by mistake. How can I fix it?" },
    ],
  },
  {
    group: "Nutrients", hint: "claim packet + verifier: a cited number, or UNKNOWN with the reason",
    presets: [
      { label: "Tomatoes · vitamin C", shows: "DIRECT: USDA evidence row applies",
        text: "Dice the tomatoes. Boil the tomatoes in water with the lid on for 15 minutes.",
        question: "How much vitamin C remains in the tomatoes after this recipe?" },
      { label: "Broccoli stir-fry · vitamin C", shows: "UNKNOWN: no evidence row for this context",
        text: "Cut the broccoli into florets. Stir-fry the broccoli in oil for 4 minutes.",
        question: "How much vitamin C remains in the broccoli after this recipe?" },
      { label: "Roasted peppers · vitamin C", shows: "UNKNOWN with simulated thermal dose",
        text: "Slice the bell peppers. Roast the bell peppers in the oven at 220 C for 20 minutes.",
        question: "How much vitamin C remains in the bell peppers after this recipe?" },
    ],
  },
  {
    group: "Safety", hint: "refused by design, before any model call",
    presets: [
      { label: "Chicken · is it safe?", shows: "food-safety refusal",
        text: "Cut the chicken into strips. Fry the chicken in oil for 6 minutes.",
        question: "Is the chicken safe to eat?" },
    ],
  },
];

export const DEFAULT_PRESET = PRESET_GROUPS[0].presets[0];
