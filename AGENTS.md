# Moltbot Repository Guidelines
- Repo: https://github.com/moltbot/moltbot
- Docs: https://docs.molt.bot

## Build, Test, and Development Commands
- **Install**: `pnpm install`
- **Build**: `pnpm build` (tsc + asset prep)
- **Lint/Format**: `pnpm lint` (oxlint), `pnpm format` (oxfmt). Run `pnpm lint:fix` to auto-resolve.
- **Run Tests**: `pnpm test` (parallel run)
- **Single Test**: `npx vitest <path/to/file.test.ts>`
- **Coverage**: `pnpm test:coverage`
- **E2E/Live Tests**: `pnpm test:e2e`, `pnpm test:live` (requires `CLAWDBOT_LIVE_TEST=1`)
- **Pre-commit**: `prek install` (CI-parity checks)
- **Runtime**: Node 22+ (ESM). Bun supported for scripts: `bun <file.ts>`.

## Coding Style & Patterns
- **Language**: TypeScript (ESM). Strict typing is mandatory. Avoid `any`.
- **Imports**: Named imports only. Use `node:` prefix for built-ins. Use relative paths for local modules.
  ```typescript
  import { randomUUID } from "node:crypto";
  import { loadConfig } from "./config/config.js";
  ```
- **Naming**:
  - Files: kebab-case (e.g., `session-manager.ts`).
  - Variables/Functions: camelCase.
  - Classes/Types/Interfaces: PascalCase.
  - Constants: UPPER_SNAKE_CASE (e.g., `CONFIG_DIR`).
- **File Length**: Aim for < 500 LOC. Refactor/split when exceeding this.
- **Error Handling**: Use standard `try-catch`. Create custom error classes for domain-specific failures.
  ```typescript
  export class WizardCancelledError extends Error { ... }
  ```
- **Dependency Injection**: Use `createDefaultDeps` patterns for CLI commands to facilitate testing.
- **Comments**: Brief comments for non-obvious logic. Use JSDoc for public API exports.

## Project Structure & Module Organization
- `src/`: Core source code.
  - `cli/`: CLI entry points and wiring.
  - `commands/`: CLI command implementations.
  - `infra/`: Low-level system/environment integration.
  - `media/`: Media pipeline (images, audio, video).
  - `channels/`: Messaging platform integrations (WhatsApp, Telegram, etc.).
- `extensions/`: Workspace packages for plugins.
- `docs/`: Mintlify documentation source.
- `dist/`: Build output.
- **Plugins**: Runtime deps must live in `dependencies`. Avoid `workspace:*` in `dependencies`.

## Docs & Communication
- **Docs**: Hosted on Mintlify (docs.molt.bot). Internal links are root-relative without extensions.
- **GitHub**: Use literal multiline strings or heredocs (`-F - <<'EOF'`) for real newlines in issues/comments.
- **Placeholders**: Use generic placeholders (e.g., `user@gateway-host`) in docs and examples.

## Security & Configuration
- **Credentials**: Stored in `~/.moltbot/credentials/` or `~/.clawdbot/credentials/`.
- **Environment**: Check `~/.profile` for relevant variables.
- **Privacy**: Never commit real phone numbers, videos, or live config values.

## Multi-Agent Safety & Workflow
- **Isolation**: Do not use `git stash` or `git worktree` unless explicitly requested.
- **Commit Scope**: Only stage and commit files related to your specific task.
- **Parallel Work**: Running multiple agents is encouraged; coordinate via session IDs.
- **Diagnostics**: Always run `oxlint` on changed files before reporting completion.
- **Verification**: Evidence (build/test success) is required before claiming a task is done.
- **Rebrand Note**: Use `moltbot` in new code/docs. `clawdbot` is for legacy compatibility only.
- **Mac App**: Rebuilds must be done directly on the Mac, not via SSH.

## Testing Guidelines
- **Framework**: Vitest.
- **Location**: Colocated with source (`*.test.ts`). E2E tests in `*.e2e.test.ts`.
- **Thresholds**: 70% coverage for lines/branches.
- **Real Devices**: Prefer real iOS/Android devices over simulators if connected.

## Commit & PR Workflow
- **Commits**: Use `scripts/committer "<msg>" <files...>` for scoped staging.
- **Changelog**: Update `CHANGELOG.md` with every PR. Reference issue numbers.
- **PRs**: Group related changes. Mention breaking changes or new flags clearly.
- **Merge**: Prefer `rebase` for clean history, `squash` for messy ones. Add PR authors as co-contributors if squashing.
- **Safety**: Never `git stash` or `git worktree` without explicit request. Scope commits to your changes only.

## Agent Guidelines
- **Multi-Agent Safety**: Assume other agents are active. Do not switch branches or modify unrelated files.
- **Diagnostics**: Run `oxlint` on changed files before completion.
- **Verification**: Evidence (build/test success) is required before claiming task completion.
- **Rebrand Note**: Moltbot replaces Clawdbot; `clawdbot` binary is a compatibility shim. Use `moltbot` in new code/docs.
- **Mac App**: Rebuilds must be done directly on the Mac, not via SSH.
