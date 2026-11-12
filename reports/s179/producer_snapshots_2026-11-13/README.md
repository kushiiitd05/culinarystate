# Diagnostic producer byte snapshots

These files preserve exact SHA256-matched earlier diagnostic producer versions beside their retained outputs. They are for provenance inspection. To reproduce an earlier tool in isolation, restore the snapshot bytes to its original tools/ path in a separate checkout so its relative ROOT resolution remains correct. Current tool versions remain in tools/. No old output, source observation, threshold or scorer is changed.
