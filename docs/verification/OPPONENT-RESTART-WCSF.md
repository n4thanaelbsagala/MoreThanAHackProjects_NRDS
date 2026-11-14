# Opposite-team restart experiment: exploratory result

Date: 2026-11-12. Base v8: `c9d1c46082784f12562e8de609d74fd93c1a00cb`.

The opt-in `config_v9_experiment.json` tries to release D earlier only after an observed moving-ball candidate for the team opposite the last confirmed team before D. At 25 fps it requires three uninterrupted frames with speed at least 0.2 m/s; at WCSF's 10 fps it requires two frames. It does not alter `config_v8.json` or default inference behavior. Missing ball, a new stoppage cue and halftime reset the fast path.

On the previously inspected WCSF provider-reference match, v8 had 82.52% H/A/D agreement, 0.50283 spellF1 and 32/102 clean restarts still D at the reference restart. The candidate had 82.94% agreement, 0.50305 spellF1 and 26/102 restarts still D. Still-D after one second fell from 20/99 to 13/99. Strict live-team agreement rose from 87.06% to 87.90%, while conditional live-team agreement fell from 89.78% to 89.40%.

The prespecified gate **failed**: when the reference team changed, the first predicted live team matched the team before D on 6/80 evaluable events versus 5/75 for v8. Because the denominators also differ, this does not establish a lower or higher rate; it fails the conservative absolute-count condition. The spellF1 increase is only 0.00023 and could be noise. Do not recommend this candidate for the team's model or make a performance PR based on this result.

The WCSF match has been inspected repeatedly, and these provider labels are not independently verified human annotations. The seven IDSSE development matches are not available locally (the repository documents approximately 2.5 GiB of source data), and they have also been used for earlier selection. No untouched final-test match exists in the current workspace. A credible solution needs an external match set with labels and a frozen protocol before evaluation; the challenge public window cannot be used for tuning.

The exact aggregate comparison and source fingerprints are in `OPPONENT-RESTART-WCSF.json`. All 100 local tests passed. With the experimental option disabled, the unchanged v8 configuration generated the full 199,319-frame tactical CSV and passed the official format validator; its SHA-256 was exactly the previously published v8 hash `97bf92b0c189c01d0b27b5bce897e3f5713ea5904cdb6b3edd524d0b29a0ff19`. No raw match data, per-frame predictions, or challenge labels are tracked.
