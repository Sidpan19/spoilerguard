# Evaluation results

Golden set rows used: 10. Skipped for missing gold labels: 0.
Viewer profiles: catching up [100, 400, 900, 1100, 1150], current [1190, 1195, 1196]. 10 videos x 8 profiles = 80 cases per system.
Input per video: title + hashtags recorded in the CSV. No description text.
'Warn' means verdict SPOILER or RISKY. n is tiny; read counts, not percentages.

## Overall

| System | Recall (spoilers warned) | False alarms (safe warned) | Precision | Accuracy | Decisive (SAFE/SPOILER) | Decisive correct |
|---|---|---|---|---|---|---|
| a_rules_only | 62/62 (100%) | 2/18 (11%) | 62/64 (97%) | 78/80 (98%) | 55/80 (69%) | 55/55 (100%) |
| b_rules_keyword | 62/62 (100%) | 2/18 (11%) | 62/64 (97%) | 78/80 (98%) | 55/80 (69%) | 55/55 (100%) |
| c_rules_llm_cache | 62/62 (100%) | 2/18 (11%) | 62/64 (97%) | 78/80 (98%) | 55/80 (69%) | 55/55 (100%) |
| d_warn_everything | 62/62 (100%) | 18/18 (100%) | 62/80 (78%) | 62/80 (78%) | 0/80 (0%) | 0/0 |

## By group

| System | Slice | Recall | False alarms | Accuracy | Decisive |
|---|---|---|---|---|---|
| a_rules_only | explicit (E) | 34/34 (100%) | 0/6 (0%) | 40/40 (100%) | 40/40 (100%) |
| a_rules_only | weak (W) | 28/28 (100%) | 2/12 (17%) | 38/40 (95%) | 15/40 (38%) |
| b_rules_keyword | explicit (E) | 34/34 (100%) | 0/6 (0%) | 40/40 (100%) | 40/40 (100%) |
| b_rules_keyword | weak (W) | 28/28 (100%) | 2/12 (17%) | 38/40 (95%) | 15/40 (38%) |
| c_rules_llm_cache | explicit (E) | 34/34 (100%) | 0/6 (0%) | 40/40 (100%) | 40/40 (100%) |
| c_rules_llm_cache | weak (W) | 28/28 (100%) | 2/12 (17%) | 38/40 (95%) | 15/40 (38%) |
| d_warn_everything | explicit (E) | 34/34 (100%) | 6/6 (100%) | 34/40 (85%) | 0/40 (0%) |
| d_warn_everything | weak (W) | 28/28 (100%) | 12/12 (100%) | 28/40 (70%) | 0/40 (0%) |

## By viewer type

| System | Slice | Recall | False alarms | Accuracy | Decisive |
|---|---|---|---|---|---|
| a_rules_only | catching up | 48/48 (100%) | 0/2 (0%) | 50/50 (100%) | 32/50 (64%) |
| a_rules_only | current | 14/14 (100%) | 2/16 (12%) | 28/30 (93%) | 23/30 (77%) |
| b_rules_keyword | catching up | 48/48 (100%) | 0/2 (0%) | 50/50 (100%) | 32/50 (64%) |
| b_rules_keyword | current | 14/14 (100%) | 2/16 (12%) | 28/30 (93%) | 23/30 (77%) |
| c_rules_llm_cache | catching up | 48/48 (100%) | 0/2 (0%) | 50/50 (100%) | 32/50 (64%) |
| c_rules_llm_cache | current | 14/14 (100%) | 2/16 (12%) | 28/30 (93%) | 23/30 (77%) |
| d_warn_everything | catching up | 48/48 (100%) | 2/2 (100%) | 48/50 (96%) | 0/50 (0%) |
| d_warn_everything | current | 14/14 (100%) | 16/16 (100%) | 14/30 (47%) | 0/30 (0%) |

## Verdicts per video (system c)

Cell = verdict / gold. Wrong hard verdicts in bold.

| id | gold H | horizon found | 100 | 400 | 900 | 1100 | 1150 | 1190 | 1195 | 1196 |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | 1196 | Ch. 1196 | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SAFE / safe |
| E2 | 1196 | Ch. 1196 | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SAFE / safe |
| E3 | 1196 | Ch. 1196 | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SAFE / safe |
| E4 | 1196 | Ch. 1196 | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SAFE / safe |
| E5 | 1195 | Ch. 1195 | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SAFE / safe | SAFE / safe |
| W1 | 1132 | Ch. 1132 | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SPOILER / spoiler | SAFE / safe | SAFE / safe | SAFE / safe | SAFE / safe |
| W2 | 1194 | Ch. 49 to 1195 | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | SAFE / safe | SAFE / safe |
| W3 | 1196 | Ch. 49 to 1197 | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / safe |
| W4 | 1123 | Ch. 223 to 1124 | SPOILER / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | SAFE / safe | SAFE / safe | SAFE / safe | SAFE / safe |
| W5 | 1196 | Ch. ? to 1197 | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / spoiler | RISKY / safe |

## Failure analysis (systems b and c)

Misses (spoiler not warned) are the costly error. False alarms are RISKY or SPOILER on a safe case.

**b_rules_keyword**: 2 errors (0 misses, 2 false alarms)

- FALSE ALARM W3 at Ch. 1196: verdict RISKY, horizon found Ch. 49 to 1197, gold 1196. Rung: 5 format risk. Horizon (Ch. 49 to 1197) overlaps your Ch. 1196; cannot rule a spoiler in or out.
- FALSE ALARM W5 at Ch. 1196: verdict RISKY, horizon found Ch. ? to 1197, gold 1196. Rung: 5 format risk. Horizon (Ch. ? to 1197) overlaps your Ch. 1196; cannot rule a spoiler in or out.

**c_rules_llm_cache**: 2 errors (0 misses, 2 false alarms)

- FALSE ALARM W3 at Ch. 1196: verdict RISKY, horizon found Ch. 49 to 1197, gold 1196. Rung: 5 format risk. Horizon (Ch. 49 to 1197) overlaps your Ch. 1196; cannot rule a spoiler in or out.
- FALSE ALARM W5 at Ch. 1196: verdict RISKY, horizon found Ch. ? to 1197, gold 1196. Rung: 5 format risk. Horizon (Ch. ? to 1197) overlaps your Ch. 1196; cannot rule a spoiler in or out.

## Checks

- Stored CSV labels vs labels computed from gold horizon: all match.
- Shuffle sanity (system b): accuracy 0.97 with true horizons vs 0.84 mean over 20 shuffles. A working eval should drop.
- System c used cached LLM output for 10/10 videos; the rest fell back to keywords.
