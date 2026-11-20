# Demo stories

The saved response files carry the recorded answers and verifier status.

## tomato-a-d

**Question.** How much vitamin C remains in the tomatoes after this recipe?

**Plain model**

Tomato A: water only
After boiling tomatoes in water for 15 minutes, some of the vitamin C content will be lost due to heat exposure and leaching into the cooking water. The exact amount of remaining vitamin C cannot be precisely determined without knowing the initial concentration and the specific conditions of the boiling process.

Tomato B: water and salt
The boiling process can reduce the amount of vitamin C in tomatoes, and depending on the duration and temperature, approximately 20-30% of the vitamin C may be lost during this cooking method. However, the exact percentage of remaining vitamin C cannot be precisely determined without knowing the initial content and specific conditions of the cooking process.

Tomato C: water, salt and vinegar
The boiling process can reduce the amount of vitamin C in tomatoes, but the addition of salt and vinegar might slightly preserve some of it due to their acidity. However, without specific values for the initial vitamin C content and the exact conditions of cooking, an exact percentage cannot be provided.

Tomato D: water, salt, vinegar and oil
The amount of vitamin C remaining in the tomatoes after boiling them in water with salt, vinegar, and olive oil for 15 minutes would be significantly reduced compared to raw tomatoes, as heat can degrade vitamin C. However, the exact percentage retained cannot be specified without knowing the initial vitamin C content and the specific conditions of the cooking process.

**CulinaryState**

Tomato A: water only
For tomato at step 2, the measured vitc value is EVD-002765=95.0% [EVD-002765]. This is taken from the cited evidence and nothing is inferred beyond it.

Tomato B: water and salt
For tomato at step 2, vitc is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_NULL. A nearby row exists (EVD-002765) but its number cannot be transferred to this context.

Tomato C: water, salt and vinegar
For tomato at step 2, vitc is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_NULL. A nearby row exists (EVD-002765) but its number cannot be transferred to this context.

Tomato D: water, salt, vinegar and oil
For tomato at step 2, vitc is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_NULL. A nearby row exists (EVD-002765) but its number cannot be transferred to this context.

**Why.** The evidence compiler uses the recorded pot state to restrict transfer. A receives a table report. B–D retain UNKNOWN. Ingredient pH crosswalk is AI-drafted. Mixture pH remains unknown.

Verifier annotation: Tomato B · 20 [no source]

Source: `reports/final/screens/runs/tomato-a-d.json` · qwen2.5:7b-instruct · 2026-11-17.

## carrots

**Question.** My carrots came out too soft and mushy. What should I change next time?

**Plain model**

Reduce the boiling time to 5–7 minutes and test the carrots with a fork for doneness before draining. Alternatively, cut the carrots into larger pieces so they take longer to cook through.

**CulinaryState**

- Reduce the boil time: step 3 shows duration_min = 10 and a simulated thermal_dose_typical_min of 6.426; try 5–7 minutes instead.  
- Cut larger pieces: step 2 records cell_integrity = CUT and step 3 piece_size_class = DICED (exact size unknown); use ½‑inch batons or larger dice to slow heat penetration.  
- Add acid to the cooking water: step 3 acid_present = NO_RECOGNIZED_MARKER; a splash of lemon juice or vinegar helps stabilize pectin and keep carrots firmer.  
- Salt the water: step 3 salt_present = NO_RECOGNIZED_MARKER; 1–2 % salt by weight can firm vegetable cell walls.  
- Leave the lid off: step 3 lid_state = COVERED; uncovering reduces steam pressure and slightly lowers the effective cooking temperature.

**Why.** The system had access to cut, lid, time and simulated heat. The parser recognized zero structured citations in this answer. The cooking advice remains unverified.

Source: `reports/final/screens/runs/carrots.json` · nvidia/nemotron-3-ultra-550b-a55b · 2026-11-20.

## tomatoes

**Question.** How much vitamin C remains in the tomatoes after this recipe?

**Plain model**

Boiling diced tomatoes for 15 minutes causes severe vitamin C loss—typically 60–80%—as the water-soluble vitamin leaches into the cooking water and degrades from prolonged heat exposure. The lid traps steam but does not prevent nutrient loss into the liquid, so most remaining vitamin C would be found in the cooking water rather than the tomatoes themselves.

**CulinaryState**

95.0% [EVD-002765]. The measurement method/platform is unknown.

**Why.** The claim packet allowed the cited table value under DIRECT and retained the measurement-method caveat. The saved answers illustrate one case. Gold labels for judging response quality are unavailable.

Verifier annotation: 60 [no source], 80 [no source]

Source: `reports/final/screens/runs/tomatoes.json` · nvidia/nemotron-3-ultra-550b-a55b · 2026-11-20.

## safety

**Question.** Is the chicken safe to eat?

**Plain model**

Only public or self-written text may go to the hosted model.

**CulinaryState**

I can't answer food-safety questions (safe temperatures, doneness, bacteria, or how long food keeps), so I won't guess.

**Why.** The system arm refuses before drafting. The plain comparison is separate. This capture used the preview with hosted sending disabled. The refusal gives no safety determination.

Source: `reports/final/screens/runs/safety.json` · nvidia/nemotron-3-ultra-550b-a55b (configured only; no call) · 2026-11-20.

