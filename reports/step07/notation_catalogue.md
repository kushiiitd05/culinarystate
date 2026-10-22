# Step 07 notation catalogue (data-derived)

Source: `registry/notation_rule_registry_v1.csv` (built by `tools/build_notation_registry.py` from latest COND versions). Executed by the normaliser: FLAG / QUALIFY / SPLIT. INFO rows are documentation only. Meanings marked CANDIDATE_READINGS / UNKNOWN_UNVERIFIED are NOT asserted.

| id | field | symbol | readings | status | action | n | examples |
|---|---|---|---|---|---|---|---|
| NR-001 | duration | `/` | range 15/20 min | alternatives | per-step times | CANDIDATE_READINGS | FLAG | 18 | LEGUMES,CKD 15/20MIN,BLD,DRAIND,BKD // LEGUMES,CKD 15/20MIN,BLD,DRND,FRIED // LEGUMES,CKD  |
| NR-002 | temperature | `- (spaced)` | negative sign | range fragment of a preceding value | CANDIDATE_READINGS | FLAG | 24 | - 20°C // - 30°C // - 75 °C |
| NR-003 | any | `~ / approx / around / about / ca.` | approximate value (qualifier) | STANDARD_CONVENTION | QUALIFY | 71 | MILK,HEATED APPROX 1 HOUR // MILK,HEATED APPROX 10MIN // MILK,HEATED APPROX 30MIN |
| NR-004 | duration | `;` | list of separate durations whose roles (e.g. cook vs storage) are not stated | CANDIDATE_READINGS | SPLIT | 245 | 2 min; 5months // 2 min; 4 months // 2 min; 10 months |
| NR-005 | temperature | `- (tight, leading)` | negative temperature (e.g. frozen storage) | STANDARD_CONVENTION | INFO | 246 | -23°C // -70°C // -18°C |
| NR-006 | temperature | `- (between numbers)` | range low-high | STANDARD_CONVENTION | INFO | 206 | 1-2°C // 96-98°C // 190-210°C |
| NR-007 | any | `> / above / over / at least` | open upper bound (value is a lower limit) | STANDARD_CONVENTION | INFO | 69 | > 75 °C // > 80 °C // > 90 °C |
| NR-008 | any | `< / below / up to` | open lower bound (value is an upper limit) | STANDARD_CONVENTION | INFO | 0 |  |
| NR-009 | duration | `, (descriptor)` | separator between descriptor words (USDA style), not between values | CANDIDATE_READINGS | INFO | 28 | MILK,HEATED APPROX 1 HOUR // MILK,HEATED APPROX 10MIN // MILK,HEATED APPROX 30MIN |
| NR-010 | duration | `CKD BLD BKD DRND FRIED` | USDA method/state abbreviations; expansions not source-verified here | UNKNOWN_UNVERIFIED | INFO | 25 | ALC BEV,NOT STIRRED IN,BKD 25 MIN // ALC BEV,STIRRED,BKD/SIMMRD 1 HR // ALC BEV,STIRRED,BK |
| NR-011 | duration | `+` | sequential methods (BOILED+BAKED) | combined | CANDIDATE_READINGS | INFO | 6 | LEGUMES,CKD 15/20MIN,BOILED+BAKED // LEGUMES,CKD 15/20MIN,BOILED+FRIED // LEGUMES,CKD 2/2. |
| NR-012 | duration | `/ (between words)` | alternative or combined methods (BKD/SIMMRD) | CANDIDATE_READINGS | INFO | 6 | ALC BEV,STIRRED,BKD/SIMMRD 1 HR // ALC BEV,STIRRED,BKD/SIMMRD 1.5 HR // ALC BEV,STIRRED,BK |
| NR-013 | pressure | `psi bar atm kPa MPa` | unit; gauge vs absolute not stated | STANDARD_CONVENTION | INFO | 129 | 15 psi // 400 Mpa // 600 Mpa |
