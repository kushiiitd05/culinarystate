# CulinaryState rehearsal run sheet

Use this six-minute demonstration during the scheduled rehearsal. Start with the signed snapshot, then use the local console if it is ready. Keep this run sheet and the captured slides open before presenting. Record actual timings and any recovery in the rehearsal log on the day.

| Time | Click or action | Say |
|---|---|---|
| 0:00–0:45 | Open `/compare`. Point to the signature badge and the final-state differences for Tomato A–D. | “Each scenario adds a different ingredient to the pot. The engine records that change before deciding whether the evidence transfers.” |
| 0:45–1:25 | Follow Tomato C into `/lab?s=tomato-c`. Select the final step and the Compatibility tab. | “An unavailable axis gets a reason. The ingredient pH band crosses the threshold, and the mixture pH remains unknown.” |
| 1:25–2:45 | Start `./tools/live_demo.sh`. Open `/live`, choose **Carrots came out mushy**, click **Ask live**, and show Pipeline. On Answer, click **Compare with plain LLM**. | “The two drafts use the same model with different context. The engine checks structured citations against its trace. In the saved run the parser recognized zero citations. The cooking suggestions remain unverified.” |
| 2:45–3:55 | Choose **Tomatoes · vitamin C**, click **Ask live**, then compare. Open Evidence. | “The system answer is governed by the claim packet. Point to the evidence row, then read whichever answer the plain model actually returned.” |
| 3:55–4:50 | Choose **Roast potatoes soggy**, click **Ask live**, then open Similar recipes. | “The search ranks titles by shared words. The source policy limits which recipes we show and send to the model.” |
| 4:50–5:30 | Choose **Chicken · is it safe?**, clear the model-send checkbox, click **Ask live**, and show the refusal. | “The system refuses the safety request. The plain comparison is unsent in this demonstration.” |
| 5:30–6:00 | Finish on the limitations slide. | “D1 through D5 are partial. The frozen hypothesis rules were not met. The demo shows how the engine constrains what the system says.” |

If the live engine goes offline, switch to the signed Compare and Lab pages. Point to the saved responses and screenshots in the submission materials while explaining which views were recorded. Use the video if it has been recorded and verified. The public fallback is [CulinaryState Explorer](https://culinarystate-group17.vercel.app). For a slow model response, show the Pipeline tab once and move to the saved materials.

## Parv's fallback recording shot list

1. Open the local console on its own browser window. Close tabs containing account or credential pages.
2. Use macOS **Shift–Command–5 → Record Selected Portion**. Frame the browser content and leave the address bar visible only if it shows the loopback URL.
3. Record the carrots Pipeline and side-by-side answer, the tomato nutrient comparison, the potato Similar recipes view and the chicken refusal. Follow the preset labels and keep source and verification badges visible.
4. Stop recording, trim any waiting time, and save as `reports/final/screens/live_fallback_2026-11-24.mp4` or provide the source recording for conversion. Play it end to end before including it in the ZIP.

Sources and presentation assets: `handoff/PARV_HANDOVER_2026-11-17.md` §6 and `reports/final/screens/MANIFEST.json`. Use the exact saved output for any quantitative examples.
