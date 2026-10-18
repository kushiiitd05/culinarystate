# OpenPI 2.0 food subset (X12, MIT)

- procedures: train 174, dev 15, test 8
- state changes: train 6,751, dev 548, test 330
- entities linked to ING: 1442/3144
- top attributes: location 1592, temperature 854, weight 643, cleanness 629, composition 438, volume 362, moisture 345, fullness 341, texture 284, wetness 181, shape 138, size 137, power 126, taste 108, container 98
- use: external check for DEL-3 state tracking (entity/attribute before→after per step); crowd labels, open vocabulary, '|' = alternative phrasings. Not our Gold.
