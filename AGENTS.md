# Agent Instructions

This project uses `bd` (beads) for issue tracking.

## Commands

```bash
bd ready                              # Find work with no blockers
bd show <id>                          # View issue details
bd list --status=open                 # All open issues
bd create --title="..." --type=task --priority=2
bd update <id> --status=in_progress   # Claim work
bd close <id>                         # Mark complete
bd close <id1> <id2>                  # Close multiple at once
bd dep add <issue> <depends-on>       # Add dependency
bd sync                               # Sync with git
```

## Key Concepts

- **Priority**: P0=critical, P1=high, P2=medium, P3=low, P4=backlog (use numbers)
- **Types**: task, bug, feature, epic, question, docs
- **Dependencies**: Issues can block other issues. `bd ready` shows only unblocked work.

## Session Completion

Before ending a session:

1. File issues for remaining work (`bd create`)
2. Run quality gates if code changed (tests, lint, build)
3. Update issue status (`bd close <id>`)
4. Commit and push:
   ```bash
   git status
   git add <files>
   bd sync
   git commit -m "..."
   git push
   ```
