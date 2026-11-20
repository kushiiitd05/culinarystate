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

Pending live capture.

**CulinaryState**

Pending live capture.

**Why.** The trace supplies cut, lid, time and simulated heat fields. State citations are checked against the trace. The cooking advice remains unverified.

Live run pending.

## tomatoes

**Question.** How much vitamin C remains in the tomatoes after this recipe?

**Plain model**

Pending live capture.

**CulinaryState**

Pending live capture.

**Why.** The claim packet restricts numerical output to applicable source reports. The wording and number check can trigger a template fallback. The saved answers illustrate one case. Gold labels for judging response quality are unavailable.

Live run pending.

## safety

**Question.** Is the chicken safe to eat?

**Plain model**

Only public or self-written text may go to the hosted model.

**CulinaryState**

I can't answer food-safety questions (safe temperatures, doneness, bacteria, or how long food keeps), so I won't guess.

**Why.** The system arm refuses before drafting. The plain comparison is separate. This capture used the preview with hosted sending disabled. The refusal gives no safety determination.

Source: `reports/final/screens/runs/safety.json` · nvidia/nemotron-3-ultra-550b-a55b (configured only; no call) · 2026-11-20.

