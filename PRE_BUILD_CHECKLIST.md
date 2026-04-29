# Pre-Build Checklist — The Money Crew

**Status:** Pre-build phase. Do not start coding the pipeline until all blockers below are resolved.
**Created:** 2026-04-26
**Source:** Gap analysis of [CLAUDE.md](CLAUDE.md) before scaffolding.

---

## ⚠️ Hard architectural constraint (added 2026-04-26)

**Project must be VPS-deployable from day one.** User intends to deploy to a cheap Linux VPS (no GPU) in the future.

**Implications:**
- **No self-hosted ComfyUI in production** — use Replicate (or equivalent API) for image generation. ComfyUI may still be used locally for prototyping but not as a production runtime dependency.
- **No Mac-only code paths** — no `mps` hardcoding, no `launchd`, no Homebrew calls from Python.
- **All paths via `pathlib` + env vars** — no hardcoded `/Users/...`.
- **Cron, not launchd**, for scheduling.
- **VoxCPM** stays local for now; future VPS deployment may require swap to a TTS API (ElevenLabs etc.) if VPS CPU/RAM is insufficient. Flag, not blocker.
- **Conflict with CLAUDE.md Mac M1/M2/M3 section** — those notes are valid for local dev only; production code must not depend on them. CLAUDE.md should be updated once architecture is locked.

**Revised stack:**

| Phase | Service | Notes |
|-------|---------|-------|
| Hero shot generation | Replicate (ToonYou) | One-time, ~$0.40–0.80 total |
| IP-Adapter variations | Replicate | One-time, ~$1.60 for 80 images |
| LoRA training | Google Colab free tier | $0, outputs portable .safetensors |
| Production scene generation | Replicate (with custom LoRA) | ~$3/month |
| Animation | fal.ai WAN image-to-video | ~$15/month |
| Voiceover | VoxCPM local | $0 |
| Assembly | FFmpeg | $0, runs anywhere |
| Upload | YouTube Data API v3 | $0 |

**Revised one-time bootstrap cost:** ~$2.50.
**Revised monthly recurring:** ~$18/month (still in line with the $15–20 estimate, not the original $5).

---

## Blockers (must resolve before any code is written)

- [x] **1. Character consistency strategy chosen.** ✅ DECIDED 2026-04-26 (revised twice: VPS-portability, then MVP-first)
  - **MVP method (2-week validation, current):** IP-Adapter at inference time — one hero shot per character used as IP-Adapter reference for every scene. ~75–80% consistency. No LoRA training. Works on Replicate today.
  - **Post-MVP method (only if validation succeeds):** LoRA per character via Path B (AI bootstrap on Colab). ~95% consistency. Adds ~1 week of work. Skipped until MVP signal justifies it.
  - **Why MVP-first:** User wants 2-week signal on whether channel format works before deeper investment. LoRA-first has 5 extra failure modes (Colab timeouts, cog packaging, training drift, etc.) that aren't worth it pre-validation.
  - **MVP production flow:** Replicate ToonYou model + IP-Adapter conditioning from hero shot → 10 scenes per video → FFmpeg Ken Burns pan/zoom (skip fal.ai animation for MVP) → VoxCPM voice → FFmpeg assembly → YouTube upload.
  - **MVP cost target:** ~$0 (free credits) for 5 videos. Bootstrap ~$0.20 for 4 hero shots. Per-video ~$1.30.
  - **Decision point:** End of week 2 — review view/subscriber data, decide LoRA + fal.ai animation investment.

- [ ] **2. `ANTHROPIC_API_KEY` added to `.env` template.**
  Script generator calls Claude but key is not listed in CLAUDE.md env block. Also pick the model:
  - **Model:** _____________________ (recommended: `claude-sonnet-4-6` for cost, `claude-opus-4-7` for quality)

- [ ] **3. Voiceover voice mapping defined.**
  VoxCPM needs reference samples per character so they sound distinct.
  - [ ] Rico voice sample (kid boy, energetic)
  - [ ] Penny voice sample (kid girl, friendly)
  - [ ] Max voice sample (teen boy, cool/smart)
  - [ ] Nana voice sample (grandma, warm/wise)

- [ ] **4. Audio/video sync strategy decided.**
  Voiceover is one continuous ~55s file; 10 clips × 5s = 50s. Pick one:
  - **Option A:** Generate voiceover first, get word-level timestamps, time scene cuts to narration beats.
  - **Option B:** Generate clips first, use FFmpeg `atempo` to stretch/trim voiceover to match.
  - **Option C:** Variable scene count per script (5–12 scenes depending on narration length).
  - **Decision:** _____________________

- [ ] **5. Realistic budget approved.**
  CLAUDE.md says ~$5/month — actual estimate:
  - fal.ai: 10 scenes × $0.05 × 30 days = **$15/month**
  - Anthropic API: ~$1–3/month (depending on model)
  - Total: **$16–20/month** (not $5). Update CLAUDE.md once approved.

- [ ] **6. fal.ai model ID verified.**
  CLAUDE.md lists `fal-ai/wan/image-to-video` — confirm this exact endpoint exists on fal.ai dashboard, or substitute the correct WAN 2.x image-to-video ID. Run one test call with $0.05 to verify before wiring it up.

- [ ] **7. ComfyUI workflow JSON exported.**
  API call needs an actual workflow graph, not just settings. Open ComfyUI → build the ToonYou workflow → "Save (API Format)" → save as `assets/workflows/toonyou_scene.json`.

---

## Easy fixes (resolve while building, not blockers)

- [ ] **8. YouTube OAuth bootstrap script.** One-time `auth.py` to do the OAuth dance and produce the refresh token.
- [ ] **9. Topic deduplication state file.** Define location: `outputs/used_topics.json` with `{date, character, topic}` records.
- [ ] **10. Background music sourced.** Download tracks from YouTube Audio Library into `assets/music/`. Need ~10 tracks for variety.
- [ ] **11. Alert channel chosen** for `send_alert()`. Options: email (SMTP), Slack webhook, macOS `osascript` notification.
- [ ] **12. "Made for kids" policy.** Decide per character — Rico/Penny likely yes, Max/Nana likely no. Note: kids-targeted disables comments, personalized ads, end screens, notifications.
- [ ] **13. Cartoon font picked.** CLAUDE.md references `assets/fonts/cartoon.ttf` — pick one (e.g. Bangers, Luckiest Guy from Google Fonts) with commercial-use license.
- [ ] **14. ComfyUI auto-start.** CLAUDE.md says "keep ComfyUI running in background" but no launch logic. Either `launchd` agent on Mac, or pipeline checks port 8188 and starts ComfyUI if down.
- [ ] **15. YouTube quota tracking.** API has 10,000 units/day; one upload ≈ 1,600 units. Daily posting is safe but log usage to catch any retry storms.

---

## Recommended build order

Once blockers are resolved, build in this order. Each step gates the next.

1. **Solve character consistency** (blocker #1) — produce one good static Rico image you're happy with.
2. **Record/source voice samples** (blocker #3) — produce one good Rico voiceover clip.
3. **Export ComfyUI workflow JSON** (blocker #7) — manual workflow first, scripted later.
4. **Verify fal.ai with one test call** (blocker #6) — animate the static Rico image, confirm cost + quality.
5. **Scaffold Python project** — folders, `requirements.txt`, `.env.example`, `.gitignore`, config modules.
6. **Wire pipeline steps in order** — script → image → animation → voice → assemble → upload, with `--step` flag working at each stage.
7. **End-to-end dry run** — full pipeline with `upload --privacy=private` to one test video.
8. **Cron job + monitoring** — only after one successful manual end-to-end run.

---

## Decisions log

Record final decisions here as they're made (with date) so we have a single source of truth before scaffolding.

| # | Decision | Choice | Date |
|---|----------|--------|------|
| 1 | Character consistency method | LoRA × 4, AI-bootstrapped via IP-Adapter, trained on Colab free tier | 2026-04-26 |
| 2 | Claude model for scripts | | |
| 4 | Audio/video sync strategy | | |
| 5 | Approved monthly budget | | |
| 11 | Alert channel | | |
| 12 | "Made for kids" per character | | |
