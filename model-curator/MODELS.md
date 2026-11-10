# OpenCode model Pareto frontiers

Fetched 2026-11-10; AA Intelligence Index version 5 (API reports major.minor, not patch).

AA catalog: 734 configurations, 118 with a current score.

## How to read this

Higher intelligence and lower AA cost per task are better. A frontier entry is not strictly dominated on both axes. Equal points are retained; effort variants are separate points.

Both tables use **AA cost per Intelligence Index task**, not token prices, OpenCode charges, or measured Go allowance consumption. Go is the Go-available subset, not an allowance-adjusted frontier. AA costs are a proxy; discounts, caching and routing can make actual OpenCode costs differ. Cost is per benchmark task, not per successful task.

Matching preserves versions and dates; no fuzzy or cross-version score substitution. Named/default AA configurations remain named/default; explicit effort settings must be supported by the catalog. Availability does not imply privacy-policy approval.

## Go frontier

30 catalog endpoints; 15 matched paid-price endpoints; 26 comparable configurations; 12 frontier points.

| OpenCode model | AA configuration | Score | AA $/task |
|---|---|---:|---:|
| `gpt-6-luna` | [GPT-6 Luna (Low)](https://artificialanalysis.ai/models/gpt-6-luna-low) | 9.7 | 0.0051 |
| `gpt-6-luna` | [GPT-6 Luna (Medium)](https://artificialanalysis.ai/models/gpt-6-luna-medium) | 18.5 | 0.0422 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Low)](https://artificialanalysis.ai/models/claude-haiku-5-5-low) | 18.6 | 0.0438 |
| `gpt-6-luna` | [GPT-6 Luna (High)](https://artificialanalysis.ai/models/gpt-6-luna-high) | 21.4 | 0.0729 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Medium)](https://artificialanalysis.ai/models/claude-haiku-5-5-medium) | 24.6 | 0.0918 |
| `mimo-v2.6-flash` | [MiMo-V2.6-Flash](https://artificialanalysis.ai/models/mimo-v2-6-flash) | 26.7 | 0.1285 |
| `gpt-6-luna` | [GPT-6 Luna (Max)](https://artificialanalysis.ai/models/gpt-6-luna) | 27.9 | 0.1520 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (High)](https://artificialanalysis.ai/models/claude-haiku-5-5-high) | 29.9 | 0.1586 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Xhigh)](https://artificialanalysis.ai/models/claude-haiku-5-5-xhigh) | 34.6 | 0.2484 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Max)](https://artificialanalysis.ai/models/claude-haiku-5-5) | 36.5 | 0.4110 |
| `kimi-k3.1-pro` | [Kimi K3.1 Pro](https://artificialanalysis.ai/models/kimi-k3-1-pro) | 46.5 | 3.6812 |
| `gemini-4-argon` | [Gemini 4 Argon (High)](https://artificialanalysis.ai/models/gemini-4-argon) | 50.4 | 9.9466 |

<details>
<summary>All comparable configurations</summary>

| OpenCode model | AA configuration | Score | AA $/task |
|---|---|---:|---:|
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Low)](https://artificialanalysis.ai/models/claude-haiku-5-5-low) | 18.6 | 0.0438 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Medium)](https://artificialanalysis.ai/models/claude-haiku-5-5-medium) | 24.6 | 0.0918 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (High)](https://artificialanalysis.ai/models/claude-haiku-5-5-high) | 29.9 | 0.1586 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Xhigh)](https://artificialanalysis.ai/models/claude-haiku-5-5-xhigh) | 34.6 | 0.2484 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Max)](https://artificialanalysis.ai/models/claude-haiku-5-5) | 36.5 | 0.4110 |
| `deepseek-v4-pro` | [DeepSeek V4 Pro 0813 (Max)](https://artificialanalysis.ai/models/deepseek-v4-pro) | 23.1 | 1.7691 |
| `gemini-4-argon` | [Gemini 4 Argon (High)](https://artificialanalysis.ai/models/gemini-4-argon) | 50.4 | 9.9466 |
| `glm-5.3` | [GLM-5.3 (Low)](https://artificialanalysis.ai/models/glm-5-3-low) | 23.1 | 1.5749 |
| `glm-5.3` | [GLM-5.3 (Max)](https://artificialanalysis.ai/models/glm-5-3) | 31.7 | 5.0093 |
| `glm-5.3-flash` | [GLM-5.3-Flash](https://artificialanalysis.ai/models/glm-5-3-flash) | 27.8 | 0.5833 |
| `gpt-5.6-luna` | [GPT-5.6 Luna (Max)](https://artificialanalysis.ai/models/gpt-5-6-luna) | 23.8 | 0.3313 |
| `gpt-6-luna` | [GPT-6 Luna (Low)](https://artificialanalysis.ai/models/gpt-6-luna-low) | 9.7 | 0.0051 |
| `gpt-6-luna` | [GPT-6 Luna (Medium)](https://artificialanalysis.ai/models/gpt-6-luna-medium) | 18.5 | 0.0422 |
| `gpt-6-luna` | [GPT-6 Luna (High)](https://artificialanalysis.ai/models/gpt-6-luna-high) | 21.4 | 0.0729 |
| `gpt-6-luna` | [GPT-6 Luna (Xhigh)](https://artificialanalysis.ai/models/gpt-6-luna-xhigh) | 23.5 | 0.1041 |
| `gpt-6-luna` | [GPT-6 Luna (Max)](https://artificialanalysis.ai/models/gpt-6-luna) | 27.9 | 0.1520 |
| `grok-4.7` | [Grok 4.7 (Low)](https://artificialanalysis.ai/models/grok-4-7-low) | 31.1 | 2.9222 |
| `grok-4.7` | [Grok 4.7 (High)](https://artificialanalysis.ai/models/grok-4-7-high) | 35.2 | 6.1836 |
| `grok-4.7` | [Grok 4.7 (Xhigh)](https://artificialanalysis.ai/models/grok-4-7) | 35.5 | 7.7715 |
| `kimi-k3.1-pro` | [Kimi K3.1 Pro](https://artificialanalysis.ai/models/kimi-k3-1-pro) | 46.5 | 3.6812 |
| `mimo-v2.6-flash` | [MiMo-V2.6-Flash](https://artificialanalysis.ai/models/mimo-v2-6-flash) | 26.7 | 0.1285 |
| `mimo-v2.6-pro` | [MiMo-V2.6-Pro](https://artificialanalysis.ai/models/mimo-v2-6-pro) | 29.9 | 0.2572 |
| `minimax-m3` | [MiniMax-M3](https://artificialanalysis.ai/models/minimax-m3) | 18.9 | 1.2851 |
| `minimax-m3.1-flash` | [MiniMax-M3.1-Flash](https://artificialanalysis.ai/models/minimax-m3-1-flash) | 29.1 | 0.4910 |
| `qwen3.8-max` | [Qwen3.8 Max (0902)](https://artificialanalysis.ai/models/qwen3-8-max) | 33.7 | 10.0239 |
| `step-5-preview` | [Step 5 Preview](https://artificialanalysis.ai/models/step-5) | 28.5 | 2.3453 |

</details>

### Go: free endpoints and special pricing (separate)

These do not change the AA cost axis. Free endpoints are excluded from the frontier. Discounted paid models remain eligible using AA reference costs. OpenCode rates below are input/output dollars per million tokens, for context only.

- `beam-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `deepseek-v4-pro`: catalog rates $0.66/$1.98.
  - Published pricing rules: `[{"factor": 2, "when": {"any": [{"all": [{"utc_hours": {"gte": "01:00"}}, {"utc_hours": {"lt": "04:00"}}]}, {"all": [{"utc_hours": {"gte": "06:00"}}, {"utc_hours": {"lt": "10:00"}}]}], "utc_days": {"in": ["mon", "tue", "wed", "thu", "fri"]}}}]`
- `deepseek-v4.1-flash`: catalog rates $0.15/$0.6.
  - Published pricing rules: `[{"factor": 2, "when": {"any": [{"all": [{"utc_hours": {"gte": "01:00"}}, {"utc_hours": {"lt": "04:00"}}]}, {"all": [{"utc_hours": {"gte": "06:00"}}, {"utc_hours": {"lt": "10:00"}}]}], "utc_days": {"in": ["mon", "tue", "wed", "thu", "fri"]}}}]`
- `gemini-4-argon`: catalog rates $2/$10.
  - Post-promotion rates inferred from the date-only multiplier: $4/$20.
  - Published pricing rules: `[{"factor": 2, "when": {"date": {"gte": "2026-12-01"}}}]`
- `iceman-contributor-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `longcat-2.5-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.

<details>
<summary>Unmatched or insufficient data</summary>

- `deepseek-v4.1-flash`: AA score or positive task cost missing
- `glm-5.2`: AA score or positive task cost missing
- `hy3`: AA score or positive task cost missing
- `hy4`: no exact AA identity match
- `hy4-preview`: no exact AA identity match
- `kimi-k2.7-code`: AA score or positive task cost missing
- `kimi-k3`: AA effort not explicitly supported by catalog; AA score or positive task cost missing
- `longcat-2.0`: AA score or positive task cost missing
- `muse-spark-1.2-contributor`: AA score or positive task cost missing
- `muse-spark-1.3-contributor`: AA effort not explicitly supported by catalog; AA score or positive task cost missing
- `qwen3.7-plus`: AA score or positive task cost missing
- `qwen3.8-flash`: no exact AA identity match

</details>

## Paid frontier

84 catalog endpoints; 25 matched paid-price endpoints; 62 comparable configurations; 19 frontier points.

| OpenCode model | AA configuration | Score | AA $/task |
|---|---|---:|---:|
| `gpt-6-luna` | [GPT-6 Luna (Low)](https://artificialanalysis.ai/models/gpt-6-luna-low) | 9.7 | 0.0051 |
| `gpt-6-luna` | [GPT-6 Luna (Medium)](https://artificialanalysis.ai/models/gpt-6-luna-medium) | 18.5 | 0.0422 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Low)](https://artificialanalysis.ai/models/claude-haiku-5-5-low) | 18.6 | 0.0438 |
| `gpt-6-luna` | [GPT-6 Luna (High)](https://artificialanalysis.ai/models/gpt-6-luna-high) | 21.4 | 0.0729 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Medium)](https://artificialanalysis.ai/models/claude-haiku-5-5-medium) | 24.6 | 0.0918 |
| `gpt-6-luna` | [GPT-6 Luna (Max)](https://artificialanalysis.ai/models/gpt-6-luna) | 27.9 | 0.1520 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (High)](https://artificialanalysis.ai/models/claude-haiku-5-5-high) | 29.9 | 0.1586 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Low)](https://artificialanalysis.ai/models/gpt-6-1-sol-low) | 34.8 | 0.1615 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Medium)](https://artificialanalysis.ai/models/gpt-6-1-sol-medium) | 46.3 | 0.3594 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (High)](https://artificialanalysis.ai/models/gpt-6-1-sol-high) | 50.3 | 0.5910 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Xhigh)](https://artificialanalysis.ai/models/gpt-6-1-sol-xhigh) | 52.5 | 0.7640 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Max)](https://artificialanalysis.ai/models/gpt-6-1-sol) | 54.6 | 1.2721 |
| `gpt-6-astra` | [GPT-6 Astra (High)](https://artificialanalysis.ai/models/gpt-6-astra-high) | 54.8 | 3.2386 |
| `gpt-6-astra` | [GPT-6 Astra (Xhigh)](https://artificialanalysis.ai/models/gpt-6-astra-xhigh) | 55.3 | 3.6589 |
| `claude-fable-5-2` | [Claude Fable 5.2 (Medium, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2-medium) | 56.4 | 3.8026 |
| `claude-opus-5-5` | [Claude Opus 5.5 (Xhigh, Default Fallback)](https://artificialanalysis.ai/models/claude-opus-5-5-xhigh) | 57.4 | 6.0472 |
| `claude-fable-5-2` | [Claude Fable 5.2 (High, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2-high) | 61.8 | 9.0784 |
| `claude-fable-5-2` | [Claude Fable 5.2 (Xhigh, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2-xhigh) | 62.2 | 14.8286 |
| `claude-fable-5-2` | [Claude Fable 5.2 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2) | 64.6 | 26.5386 |

<details>
<summary>All comparable configurations</summary>

| OpenCode model | AA configuration | Score | AA $/task |
|---|---|---:|---:|
| `claude-fable-5-1` | [Claude Fable 5.1 (Low, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-1-low) | 38.7 | 4.4711 |
| `claude-fable-5-1` | [Claude Fable 5.1 (Medium, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-1-medium) | 43.2 | 5.5643 |
| `claude-fable-5-1` | [Claude Fable 5.1 (High, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-1-high) | 47.2 | 7.5400 |
| `claude-fable-5-1` | [Claude Fable 5.1 (Xhigh, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-1-xhigh) | 50 | 10.8475 |
| `claude-fable-5-1` | [Claude Fable 5.1 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-1) | 49.2 | 12.9940 |
| `claude-fable-5-2` | [Claude Fable 5.2 (Low, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2-low) | 53.9 | 3.0972 |
| `claude-fable-5-2` | [Claude Fable 5.2 (Medium, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2-medium) | 56.4 | 3.8026 |
| `claude-fable-5-2` | [Claude Fable 5.2 (High, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2-high) | 61.8 | 9.0784 |
| `claude-fable-5-2` | [Claude Fable 5.2 (Xhigh, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2-xhigh) | 62.2 | 14.8286 |
| `claude-fable-5-2` | [Claude Fable 5.2 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-2) | 64.6 | 26.5386 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Low)](https://artificialanalysis.ai/models/claude-haiku-5-5-low) | 18.6 | 0.0438 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Medium)](https://artificialanalysis.ai/models/claude-haiku-5-5-medium) | 24.6 | 0.0918 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (High)](https://artificialanalysis.ai/models/claude-haiku-5-5-high) | 29.9 | 0.1586 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Xhigh)](https://artificialanalysis.ai/models/claude-haiku-5-5-xhigh) | 34.6 | 0.2484 |
| `claude-haiku-5-5` | [Claude Haiku 5.5 (Max)](https://artificialanalysis.ai/models/claude-haiku-5-5) | 36.5 | 0.4110 |
| `claude-opus-5` | [Claude Opus 5 (Max)](https://artificialanalysis.ai/models/claude-opus-5) | 44.2 | 11.8215 |
| `claude-opus-5-5` | [Claude Opus 5.5 (Low, Default Fallback)](https://artificialanalysis.ai/models/claude-opus-5-5-low) | 34.8 | 0.9755 |
| `claude-opus-5-5` | [Claude Opus 5.5 (Medium, Default Fallback)](https://artificialanalysis.ai/models/claude-opus-5-5-medium) | 48.2 | 2.4511 |
| `claude-opus-5-5` | [Claude Opus 5.5 (High, Default Fallback)](https://artificialanalysis.ai/models/claude-opus-5-5-high) | 51.8 | 3.4647 |
| `claude-opus-5-5` | [Claude Opus 5.5 (Xhigh, Default Fallback)](https://artificialanalysis.ai/models/claude-opus-5-5-xhigh) | 57.4 | 6.0472 |
| `claude-opus-5-5` | [Claude Opus 5.5 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-opus-5-5) | 59.1 | 10.0364 |
| `claude-sonnet-5-5` | [Claude Sonnet 5.5 (Low, Default Fallback)](https://artificialanalysis.ai/models/claude-sonnet-5-5-low) | 25.6 | 0.5113 |
| `claude-sonnet-5-5` | [Claude Sonnet 5.5 (Medium, Default Fallback)](https://artificialanalysis.ai/models/claude-sonnet-5-5-medium) | 30.8 | 0.7807 |
| `claude-sonnet-5-5` | [Claude Sonnet 5.5 (High, Default Fallback)](https://artificialanalysis.ai/models/claude-sonnet-5-5-high) | 41.5 | 1.6361 |
| `claude-sonnet-5-5` | [Claude Sonnet 5.5 (Xhigh, Default Fallback)](https://artificialanalysis.ai/models/claude-sonnet-5-5-xhigh) | 49.9 | 4.0920 |
| `claude-sonnet-5-5` | [Claude Sonnet 5.5 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-sonnet-5-5) | 54.5 | 10.0206 |
| `deepseek-v4-pro` | [DeepSeek V4 Pro 0813 (Max)](https://artificialanalysis.ai/models/deepseek-v4-pro) | 23.1 | 1.7691 |
| `gemini-3.5-flash-lite` | [Gemini 3.5 Flash-Lite](https://artificialanalysis.ai/models/gemini-3-5-flash-lite) | 11.7 | 0.6929 |
| `gemini-3.8-flash` | [Gemini 3.8 Flash (Medium)](https://artificialanalysis.ai/models/gemini-3-8-flash-medium) | 30.1 | 6.2586 |
| `gemini-3.8-flash` | [Gemini 3.8 Flash (High)](https://artificialanalysis.ai/models/gemini-3-8-flash) | 30.8 | 7.7660 |
| `gemini-4-argon` | [Gemini 4 Argon (High)](https://artificialanalysis.ai/models/gemini-4-argon) | 50.4 | 9.9466 |
| `glm-5.3` | [GLM-5.3 (Low)](https://artificialanalysis.ai/models/glm-5-3-low) | 23.1 | 1.5749 |
| `glm-5.3` | [GLM-5.3 (Max)](https://artificialanalysis.ai/models/glm-5-3) | 31.7 | 5.0093 |
| `glm-5.3-flash` | [GLM-5.3-Flash](https://artificialanalysis.ai/models/glm-5-3-flash) | 27.8 | 0.5833 |
| `gpt-5.6-luna` | [GPT-5.6 Luna (Max)](https://artificialanalysis.ai/models/gpt-5-6-luna) | 23.8 | 0.3313 |
| `gpt-5.6-terra` | [GPT-5.6 Terra (Max)](https://artificialanalysis.ai/models/gpt-5-6-terra) | 32.3 | 3.7349 |
| `gpt-6-astra` | [GPT-6 Astra (Low)](https://artificialanalysis.ai/models/gpt-6-astra-low) | 43.3 | 1.4237 |
| `gpt-6-astra` | [GPT-6 Astra (Medium)](https://artificialanalysis.ai/models/gpt-6-astra-medium) | 51.6 | 2.7324 |
| `gpt-6-astra` | [GPT-6 Astra (High)](https://artificialanalysis.ai/models/gpt-6-astra-high) | 54.8 | 3.2386 |
| `gpt-6-astra` | [GPT-6 Astra (Xhigh)](https://artificialanalysis.ai/models/gpt-6-astra-xhigh) | 55.3 | 3.6589 |
| `gpt-6-astra` | [GPT-6 Astra (Max)](https://artificialanalysis.ai/models/gpt-6-astra) | 56.9 | 6.2447 |
| `gpt-6-luna` | [GPT-6 Luna (Low)](https://artificialanalysis.ai/models/gpt-6-luna-low) | 9.7 | 0.0051 |
| `gpt-6-luna` | [GPT-6 Luna (Medium)](https://artificialanalysis.ai/models/gpt-6-luna-medium) | 18.5 | 0.0422 |
| `gpt-6-luna` | [GPT-6 Luna (High)](https://artificialanalysis.ai/models/gpt-6-luna-high) | 21.4 | 0.0729 |
| `gpt-6-luna` | [GPT-6 Luna (Xhigh)](https://artificialanalysis.ai/models/gpt-6-luna-xhigh) | 23.5 | 0.1041 |
| `gpt-6-luna` | [GPT-6 Luna (Max)](https://artificialanalysis.ai/models/gpt-6-luna) | 27.9 | 0.1520 |
| `gpt-6-sol` | [GPT-6 Sol (Max)](https://artificialanalysis.ai/models/gpt-6-sol) | 44.2 | 2.4658 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Low)](https://artificialanalysis.ai/models/gpt-6-1-sol-low) | 34.8 | 0.1615 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Medium)](https://artificialanalysis.ai/models/gpt-6-1-sol-medium) | 46.3 | 0.3594 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (High)](https://artificialanalysis.ai/models/gpt-6-1-sol-high) | 50.3 | 0.5910 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Xhigh)](https://artificialanalysis.ai/models/gpt-6-1-sol-xhigh) | 52.5 | 0.7640 |
| `gpt-6.1-sol` | [GPT-6.1 Sol (Max)](https://artificialanalysis.ai/models/gpt-6-1-sol) | 54.6 | 1.2721 |
| `grok-4.6` | [Grok 4.6 (Xhigh)](https://artificialanalysis.ai/models/grok-4-6-xhigh) | 31 | 4.6786 |
| `grok-4.7` | [Grok 4.7 (Low)](https://artificialanalysis.ai/models/grok-4-7-low) | 31.1 | 2.9222 |
| `grok-4.7` | [Grok 4.7 (High)](https://artificialanalysis.ai/models/grok-4-7-high) | 35.2 | 6.1836 |
| `grok-4.7` | [Grok 4.7 (Xhigh)](https://artificialanalysis.ai/models/grok-4-7) | 35.5 | 7.7715 |
| `kimi-k3` | [Kimi K3 (Low)](https://artificialanalysis.ai/models/kimi-k3-low) | 17.4 | 2.3688 |
| `minimax-m3` | [MiniMax-M3](https://artificialanalysis.ai/models/minimax-m3) | 18.9 | 1.2851 |
| `mistral-large-4` | [Mistral Large 4 (High)](https://artificialanalysis.ai/models/mistral-large-4) | 26.1 | 2.0617 |
| `muse-wonder-1.0` | [Muse Wonder (High)](https://artificialanalysis.ai/models/muse-wonder-high) | 40.5 | 4.5605 |
| `muse-wonder-1.0` | [Muse Wonder (Max)](https://artificialanalysis.ai/models/muse-wonder) | 43.6 | 6.9520 |
| `qwen3.8-max` | [Qwen3.8 Max (0902)](https://artificialanalysis.ai/models/qwen3-8-max) | 33.7 | 10.0239 |

</details>

### Paid: free endpoints and special pricing (separate)

These do not change the AA cost axis. Free endpoints are excluded from the frontier. Discounted paid models remain eligible using AA reference costs. OpenCode rates below are input/output dollars per million tokens, for context only.

- `beam-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `big-pickle`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `deepseek-v4.1-flash-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
  - Nonfree counterpart in this catalog: `deepseek-v4.1-flash`: $0.3/$1.2 (base/post-promo rates).
- `flint-40b-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `gemini-3.6-flash`: catalog rates $0.75/$3.75.
  - Post-promotion rates inferred from the date-only multiplier: $1.5/$7.5.
  - Published pricing rules: `[{"factor": 2, "when": {"date": {"gte": "2027-01-01"}}}]`
- `gemini-3.7-flash`: catalog rates $0.75/$3.75.
  - Post-promotion rates inferred from the date-only multiplier: $1.5/$7.5.
  - Published pricing rules: `[{"factor": 2, "when": {"date": {"gte": "2027-01-01"}}}]`
- `gemini-3.8-flash`: catalog rates $0.75/$3.75.
  - Post-promotion rates inferred from the date-only multiplier: $1.5/$7.5.
  - Published pricing rules: `[{"factor": 2, "when": {"date": {"gte": "2027-01-01"}}}]`
- `gemini-4-argon`: catalog rates $2/$10.
  - Post-promotion rates inferred from the date-only multiplier: $4/$20.
  - Published pricing rules: `[{"factor": 2, "when": {"date": {"gte": "2026-12-01"}}}]`
- `glm-5.3-flash-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
  - Nonfree counterpart in this catalog: `glm-5.3-flash`: $0.15/$0.5 (base/post-promo rates).
- `iceman-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `inkling-2-small-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `longcat-2.5-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `mimo-v2.6-flash-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `minimax-m3.1-flash-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `nemotron-3.5-lightning-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.
- `nemotron-3.5-super-vl-free`: catalog rates $0/$0. Free endpoint; regular price not supplied by this catalog entry.

<details>
<summary>Unmatched or insufficient data</summary>

- `claude-fable-5`: AA score or positive task cost missing
- `claude-haiku-4-5`: no exact AA identity match
- `claude-opus-4-5`: AA score or positive task cost missing
- `claude-opus-4-6`: AA score or positive task cost missing
- `claude-opus-4-7`: AA score or positive task cost missing
- `claude-opus-4-8`: AA score or positive task cost missing
- `claude-sonnet-4-5`: no exact AA identity match
- `claude-sonnet-4-6`: AA score or positive task cost missing
- `claude-sonnet-5`: AA score or positive task cost missing
- `deepseek-v4.1-flash`: AA score or positive task cost missing
- `gemini-3.5-flash`: AA score or positive task cost missing
- `gemini-3.6-flash`: AA score or positive task cost missing
- `gemini-3.7-flash`: AA score or positive task cost missing
- `glm-5`: AA score or positive task cost missing
- `glm-5.1`: AA score or positive task cost missing
- `glm-5.2`: AA score or positive task cost missing
- `gpt-5`: AA score or positive task cost missing
- `gpt-5-codex`: AA score or positive task cost missing
- `gpt-5-nano`: AA score or positive task cost missing
- `gpt-5.1`: AA score or positive task cost missing
- `gpt-5.1-codex`: AA score or positive task cost missing
- `gpt-5.1-codex-max`: no exact AA identity match
- `gpt-5.1-codex-mini`: AA score or positive task cost missing
- `gpt-5.2`: AA score or positive task cost missing
- `gpt-5.2-codex`: AA score or positive task cost missing
- `gpt-5.3-codex`: AA score or positive task cost missing
- `gpt-5.3-codex-spark`: no exact AA identity match
- `gpt-5.4`: AA score or positive task cost missing
- `gpt-5.4-mini`: AA score or positive task cost missing
- `gpt-5.4-nano`: AA score or positive task cost missing
- `gpt-5.4-pro`: AA score or positive task cost missing
- `gpt-5.5`: AA score or positive task cost missing
- `gpt-5.5-pro`: AA score or positive task cost missing
- `gpt-5.6-sol`: AA score or positive task cost missing
- `grok-4.5`: AA score or positive task cost missing
- `grok-build-0.1`: no exact AA identity match
- `kimi-k2.5`: AA score or positive task cost missing
- `kimi-k2.6`: AA score or positive task cost missing
- `kimi-k2.7-code`: AA score or positive task cost missing
- `minimax-m2.5`: AA score or positive task cost missing
- `minimax-m2.7`: AA score or positive task cost missing
- `muse-ember-1.0`: no exact AA identity match
- `muse-spark-1.2`: AA score or positive task cost missing
- `muse-spark-1.3`: AA effort not explicitly supported by catalog; AA score or positive task cost missing
- `qwen3.5-plus`: no exact AA identity match
- `qwen3.6-plus`: AA score or positive task cost missing
- `qwen3.8-flash`: no exact AA identity match

</details>

## Sources

Scores and benchmark task costs: [Artificial Analysis](https://artificialanalysis.ai/) ([free API](https://artificialanalysis.ai/api/v2/language/models/free)).

- OpenCode Go: https://opencode.ai/inference/go/v1/models
- OpenCode Paid: https://opencode.ai/inference/v1/models

No model selections or local configuration are changed by this report.
