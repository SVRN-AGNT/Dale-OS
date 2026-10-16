# Install Dale OS skills

Dale OS is modular. Install the smallest skill set that solves the failure class in front of you.

## Claude Code plugins

This repository is a Claude Code plugin marketplace named `dale-os` (`.claude-plugin/marketplace.json`). It ships two plugins, one per skill family:

```bash
claude plugin marketplace add SVRN-AGNT/Dale-OS
claude plugin install dale-os-operator@dale-os
claude plugin install dale-os-financial-truth@dale-os
```

Inside a session, `/plugin install dale-os-operator --marketplace SVRN-AGNT/Dale-OS` does both steps at once (Claude Code 2.1.275 or later). Skills load namespaced, for example `dale-os-operator:systemic-bug-instinct`. Pin with `claude plugin marketplace add SVRN-AGNT/Dale-OS@<TAG>` when you need reproducible behavior.

## Other Agent Skills hosts

```bash
npx skills add SVRN-AGNT/Dale-OS            # list and pick skills interactively
npx skills add SVRN-AGNT/Dale-OS --skill truth-boundary
```

## Inspect before installing

With GitHub CLI 2.90.0 or newer:

```bash
gh skill preview SVRN-AGNT/Dale-OS execution-charter
```

Preview is the default trust posture. Skills can contain instructions and executable scripts; inspect the tree and `SKILL.md` before installation.

## Install one skill

```bash
gh skill install SVRN-AGNT/Dale-OS execution-charter
```

Choose a host explicitly when useful:

```bash
gh skill install SVRN-AGNT/Dale-OS systemic-bug-instinct --agent claude-code --scope user
gh skill install SVRN-AGNT/Dale-OS truth-boundary --agent codex --scope project
```

For the fastest unambiguous lookup, install by exact path:

```bash
gh skill install SVRN-AGNT/Dale-OS skills/operator/systemic-bug-instinct
```

## Install every canonical skill

GitHub CLI 2.93.0 installs named skills individually. To install the full current catalog from a local checkout, derive the names from the canonical manifest rather than maintaining a second list:

```bash
python - <<'PY' > /tmp/dale-skill-names
import json
for skill in json.load(open('manifest.json'))['skills']:
    print(skill['name'])
PY

while IFS= read -r skill; do
  gh skill install . "$skill" --from-local
done < /tmp/dale-skill-names
```

The v0.1.0 release candidate exercised this pattern against its then-current 20-skill catalog. A future release must re-run installation proof against the catalog it ships. For production agents, prefer the smallest set that matches the workflow so activation remains legible.

## Pin consequential workflows

For reproducible agent behavior, pin a release tag or commit SHA:

```bash
gh skill install SVRN-AGNT/Dale-OS systemic-bug-instinct --pin <TAG_OR_SHA>
```

Then inspect updates before accepting them:

```bash
gh skill update --dry-run
```

## Find the right module first

If you know the failure class:

```bash
python scripts/dale.py resolve symptom-patch
python scripts/dale.py resolve false-certainty --json
```

If the task spans multiple modules:

```bash
python scripts/dale.py compositions
python scripts/dale.py composition safe-bug-fix --json
```

Machine-readable routing lives in:

- `machine/failure-classes.json`
- `machine/compositions.json`
- `manifest.json`

## Canonical-source rule

Install canonical directories under `skills/`. Host adapters are distributions or integration guidance, not a second source of truth.

## Maintainer validation

Before a public skill release, validate both Dale OS invariants and the host ecosystem contract:

```bash
python scripts/dale.py doctor
gh skill publish --dry-run
```

`gh skill` is a versioned external interface. The release candidate was verified with GitHub CLI 2.93.0; revalidate installation behavior when changing the supported CLI baseline.
