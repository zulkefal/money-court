# Writing scripts by hand

This folder is the **video queue**. Every JSON file here is a Money Court video waiting to be rendered. The daily workflow ([`.github/workflows/daily.yml`](../.github/workflows/daily.yml)) picks the oldest script (FIFO by filename), renders + uploads it, then moves it to `scripts/archive/`.

Drop a new script in here whenever you want to queue a video. If you have `ANTHROPIC_API_KEY` set, the workflow auto-tops the queue back up to 5 after each run; if you don't, the queue only ever has what you put in.

## Quick start (copy-paste template)

Save as `scripts/verdict_<name1>_vs_<name2>_<topic-slug>.json`:

```json
{
  "video_id": "verdict-dan-vs-zoe-credit-card-debt-001",
  "character": "judge_vera",
  "topic": "Ignoring credit card debt letters vs responding to them (Dan vs Zoe)",
  "scenes": [
    {
      "id": 1,
      "narration": "I'm Judge Vera, and today's case is one I see every single day — two people, same debt, completely different outcomes. Court is in session!",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, cartoon woman named judge vera, silver hair in a neat bun, sharp dark eyes, black judge robes with a gold gavel badge, standing confidently behind a courtroom bench pointing her gavel forward, kids comic book illustration"
    },
    {
      "id": 2,
      "narration": "Dan and Zoe are both thirty years old, both owe eight thousand dollars on maxed-out credit cards, and both just received their first debt collection letter.",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, two adults dan and zoe standing side by side each holding an identical official debt collection envelope, neutral expressions, simple apartment background, kids comic book illustration"
    },
    {
      "id": 3,
      "narration": "Dan tosses the letter in the trash, ignores three more, and never responds — he thinks if he hides long enough the debt will just disappear.",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, man dan casually tossing an official envelope into an overflowing trash can, a pile of unopened letters on the floor behind him, kids comic book illustration"
    },
    {
      "id": 4,
      "narration": "Zoe opens every letter, calls the debt collector, and negotiates the eight thousand down to four thousand five hundred with a written payment agreement.",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, woman zoe sitting at a kitchen table on the phone with a notepad writing down numbers, a signed agreement document in front of her, calm focused expression, kids comic book illustration"
    },
    {
      "id": 5,
      "narration": "Two years later Dan gets served a court summons — the collector sued him and a judge ordered his wages garnished at twenty five percent every paycheck.",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, shocked man dan receiving a court summons from a process server at his front door, giant gavel shadow looming over him, kids comic book illustration"
    },
    {
      "id": 6,
      "narration": "Zoe paid off her negotiated balance in eighteen months, saved thirty five hundred dollars, and her credit score jumped one hundred and forty points.",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, split scene, left side woman zoe celebrating holding a zero balance letter with a rising credit score meter, right side dan sitting in a courtroom looking defeated next to a lawyer, kids comic book illustration"
    },
    {
      "id": 7,
      "narration": "Never ignore a debt letter — silence gives collectors the right to sue you. Respond, negotiate, and get everything in writing. Court dismissed!",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, cartoon woman named judge vera, silver hair in a neat bun, sharp dark eyes, black judge robes with a gold gavel badge, banging gavel with one hand and holding up a negotiation checklist with the other, kids comic book illustration"
    }
  ]
}
```

That's it. Drop the file in `scripts/`, commit, push. The next daily run will pick it up.

## Schema reference

### Required top-level fields

| Field | Type | Notes |
|---|---|---|
| `video_id` | string | URL-safe slug. Format: `verdict-<name1>-vs-<name2>-<topic-slug>-NNN`. Used as the filename for outputs and the YouTube upload key. Must be unique across the queue + archive. |
| `character` | string | Always `"judge_vera"`. (Single-host channel.) |
| `topic` | string | Short human-readable topic. May include `"(Name1 vs Name2)"`. Recorded in `outputs/used_topics.json` for 30-day cooldown. |
| `scenes` | array | **Exactly 7** scene objects. Fewer or more will fail. |

### Optional top-level fields

| Field | Type | Default if omitted |
|---|---|---|
| `title` | string | Auto-generated by [`pipeline/metadata.py`](../pipeline/metadata.py) from the topic + first scene's narration. Override if you want a hand-tuned clickbait title. |
| `description` | string | Auto-generated. |
| `tags` | array of strings | Auto-generated based on character + topic keywords. |
| `voice` | string | Falls back to `voiceover.CHARACTER_VOICES["judge_vera"]` (`en-US-AriaNeural`). Override only if you want a non-canonical voice for a specific video. |

### Per-scene fields

| Field | Type | Notes |
|---|---|---|
| `id` | int | 1 through 7. |
| `narration` | string | What Judge Vera says. See narration rules below. |
| `image_prompt` | string | Pollinations prompt for the scene illustration. See prompt rules below. |

## Narration rules

- **8th-grade reading level.** Short, punchy sentences.
- **No quote marks** anywhere in the text — captions strip them and TTS reads them awkwardly. Use commas or sentence breaks instead.
- **Spell numbers in words** — `"eight thousand dollars"` not `"$8,000"`. The TTS engine mispronounces digits and dollar signs.
- **Allowed punctuation:** letters, digits, spaces, periods, commas, `!`, `?`. Anything else gets stripped from the burnt-in captions.
- **Scene 1 must lead with a shocker** — a surprising number or counterintuitive fact in the first 3 seconds — then transition into Judge Vera's intro ending with `"Court is in session!"`
- **Scene 7 is the verdict** — 1–2 punchy lesson sentences + actionable rule + `"Court dismissed!"`
- **6–9 seconds of narration per scene.** Around 14–22 words.

## Image-prompt rules

- **Always start with this exact phrase:**
  > `kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines`
- **Always end with:** `kids comic book illustration`
- **Judge Vera's canonical look** — copy verbatim every time she's in frame:
  > `cartoon woman named judge vera, silver hair in a neat bun, sharp dark eyes, black judge robes with a gold gavel badge, holding wooden gavel`
- **Use comic conventions:** motion lines, sparkles, comic burst banners (e.g. `BIG BOLD GAVEL COMIC BANNER`), thought bubbles, gavel shadows, dramatic dollar-amount lettering. These read like a graphic novel page, not a flat illustration.
- **For comparison panels** (side-by-side litigants): describe each litigant's left/right position, pose, and contrasting facial expression.
- **Scene 1 should visualize the shocker + courtroom** — Judge Vera at the bench, pointing her gavel forward, with comic burst dollar amounts.
- **Scene 7 should visualize the verdict** — Judge Vera banging her gavel, holding up an evidence/checklist document.

## Title rules (only if you override)

If you write a custom `title` field:
- **Lead with a $ amount or shocking number** — quantify the hook
- **Include 1–2 emoji** from this set: ⚖️ 🔨 💸 😱 💰 📉
- **≤ 75 characters total**
- **End with** ` | Money Court #shorts`

Examples:
- `Sued for $8,000?! ⚖️😱 Dan vs Zoe | Money Court #shorts`
- `Wages Garnished 25% 🔨 Dan vs Zoe | Money Court #shorts`
- `She Saved $3,500 by Calling 💰 Dan vs Zoe | Money Court #shorts`

## The winning verdict format

This is the format that's been validated against past performance — every script should follow it:

| Scene | Beat | Example |
|---|---|---|
| 1 | **Shocker hook + courtroom intro** | "I'm Judge Vera, and today's case is one I see every single day — two people, same debt, completely different outcomes. Court is in session!" |
| 2 | **Setup — introduce two named litigants on equal footing** | "Dan and Zoe are both thirty years old, both owe eight thousand dollars..." |
| 3 | **Divergence A — what one party does wrong** | "Dan tosses the letter in the trash, ignores three more..." |
| 4 | **Divergence B — what the other party does right** | "Zoe opens every letter, calls the debt collector, and negotiates..." |
| 5 | **Time-jump — the consequence catches up** | "Two years later Dan gets served a court summons..." |
| 6 | **Reveal — the dramatic outcome with numbers** | "Zoe paid off her balance in eighteen months, saved thirty five hundred dollars..." |
| 7 | **Verdict + CTA + "Court dismissed!"** | "Never ignore a debt letter — silence gives collectors the right to sue you. Respond, negotiate, and get everything in writing. Court dismissed!" |

Names rule: **never reuse Name1/Name2 across scripts.** The audience clocks repeats. The archive folder is a good place to scan for already-used names before picking new ones.

## Testing a script before queuing

Render and upload privately first to sanity-check:

```bash
./venv/bin/python make_video.py scripts/my_new_verdict.json
# Watch outputs/final/<video_id>.mp4 to verify it looks/sounds right
./venv/bin/python make_video.py scripts/my_new_verdict.json --upload --privacy=private
# Now you can preview it in YouTube Studio before committing it to the queue
```

If it's good, just leave it in `scripts/` and commit — the daily workflow will pick it up.

## What gets generated (and what does NOT)

You only write the JSON. The pipeline handles:

- **Images** (Pollinations.ai → upscaled to 1080×1920)
- **Voiceover** (edge-tts in Judge Vera's canonical voice)
- **Captions** (auto-burned in from word-timed TTS output)
- **Ken Burns motion** (cycled across 7 motion presets)
- **YouTube title/description/tags** (unless you override them in the JSON)
- **Scheduled publish time** (random PKT slot, set by `daily_pipeline.py`)
