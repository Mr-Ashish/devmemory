# Task

Extract **durable repository knowledge** from the development session below.
You already have enough context below — **do not explore the filesystem**.
Respond with **only** the JSON object (fence optional).

## Output contract (mandatory)

```json
{
  "summary": "1-3 sentences: what durable knowledge was found",
  "session_ids": ["{{SESSION_ID}}"],
  "units": [
    {
      "kind": "dev",
      "path": "src/auth",
      "action": "merge",
      "section": "Design decisions",
      "content": "- Bullet one\n- Bullet two",
      "evidence": ["short quote"],
      "confidence": "high"
    }
  ]
}
```

### Field rules
- `kind`: `"dev"` (architecture/decisions/patterns/pitfalls) or `"usage"` (commands/setup/debug)
- `path`: **must be one of the existing directories listed below** (or `"."`). Never invent paths.
- `section`: **must** be one of:
  - DEV: `Architecture` | `Design decisions` | `Patterns` | `Pitfalls`
  - USAGE: `Setup` | `Common commands` | `Debugging` | `Troubleshooting`
- `content`: markdown bullets only; concrete and non-duplicative of existing knowledge
- `confidence`: `high` | `medium` | `low`
- Prefer 1–6 units. When both design and commands appear, emit **both** kinds.
- **No secrets**. Never copy tokens, keys, or `.env` values.

## Session
- **id:** `{{SESSION_ID}}`
- **source:** `{{SESSION_SOURCE}}`

### Transcript

{{SESSION_TEXT}}

## Existing directories (allowed `path` values)

```
{{EXISTING_DIRS}}
```

## Repository snapshot

### git status
```
{{GIT_STATUS}}
```

### recent log
```
{{GIT_LOG}}
```

### tree (sample)
```
{{TREE}}
```

### git diff
```
{{GIT_DIFF}}
```

### existing knowledge (do not repeat these bullets)
{{EXISTING_KNOWLEDGE}}

## Final instruction
Return the JSON object now. If nothing durable is present, return `"units": []`.
