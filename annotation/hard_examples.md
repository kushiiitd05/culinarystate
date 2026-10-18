# Hard examples (synthetic sentences) with the expected annotation

| # | Text | Expected events / labels | Why it is hard |
|---|---|---|---|
| H1 | "Spoon out 1 tbsp of the melted butter and set aside." | Reserve(target=butter, output=reserved butter, portion="1 tbsp") | remainder stays `butter`; grams UNKNOWN |
| H2 | "Stir the flour into the remaining butter." | Merge(inputs=[flour, butter], output=roux); coref "the remaining butter"→butter | "remaining" is coref, not a new entity |
| H3 | "Drain, reserving 100ml of the cooking water." | Split(pot→pasta, cooking water) → Reserve(cooking water, 100 ml) → Discard(cooking water) | three events from one verb phrase |
| H4 | "Divide the dough into 8 equal balls." | Split(dough, 8 outputs × "1/8") | fractions only because "equal" is stated |
| H5 | "Divide the mixture between the tins." | Split(mixture, outputs with fraction null) | number of tins from ingredients/equipment; shares unstated |
| H6 | "Meanwhile, fry the onions until soft." | Transform(onions, fry, endpoint="soft") | "meanwhile" = parallel; order by text position |
| H7 | "Return the chicken to the pan with the sauce." | Merge(inputs=[chicken, sauce], output=…) + Transfer if pan changes | chicken was removed earlier → coref to its entity |
| H8 | "Heat oven to 200C/180C fan/gas 6." | TEMPERATURE span (one); no event (preheat is a tool state) | setpoint ≠ food temperature |
| H9 | "Cook for 5-7 mins or until golden." | Transform(time="5-7 min", endpoint="golden") | time range + endpoint both kept |
| H10 | "Add the beans, or chickpeas if you prefer." | ALTERNATIVE span; line `alternatives` | alternative is not a second ingredient |
| H11 | "Season to taste." | Merge(inputs=[dish, salt, pepper]) only if salt/pepper lines exist; else note | implicit seasoning entities |
| H12 | "Pour over the reserved syrup." | Recombine(target=reserved syrup, output=cake) | reserved entity must exist earlier |
| H13 | "Whisk the egg whites to stiff peaks." | Transform(egg whites, whisk, endpoint="stiff peaks", sets={texture: stiff peaks}) | endpoint is a state |
| H14 | "Leave to marinate overnight in the fridge." | Transfer(…, fridge) + Transform(marinate, time="overnight") | TIME is qualitative-ish; keep raw |
| H15 | "Add half the cheese, then the rest on top." | Split(cheese, ["half 1/2","rest 1/2"]) then two Merges | "half" is an explicit fraction |
| H16 | "Fry the paneer in batches." | Transform(paneer, fry) (+ note "batches") | do not create one entity per batch unless named |
