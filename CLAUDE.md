# CLAUDE.md

Project guidance for Claude Code when working in this repository. See
[`docs/family_financial_platform_master_plan.md`](docs/family_financial_platform_master_plan.md)
for the full product/technical plan and [`docs/phase0-setup.md`](docs/phase0-setup.md)
for manual cloud/OAuth follow-up steps.

## Git Workflow

After completing every implementation task:

- Never work directly on `main`.
- Create a short-lived feature branch for every task.
- Use clear branch names such as:
  - `feat/google-auth`
  - `feat/household-model`
  - `fix/duplicate-detection`
  - `chore/ci`
- Run all relevant quality checks before committing.
- Never commit secrets or `.env` files.
- Review the diff before committing.
- Commit completed work using Conventional Commits.
- Push the feature branch to `origin`.
- Open a Pull Request targeting `main`.
- The Pull Request must include:
  - a concise summary of the changes
  - tests/checks that were run
  - migrations added, if any
  - environment variable changes, if any
  - deployment implications, if any
- Verify that GitHub Actions starts successfully on the Pull Request.
- If CI fails, investigate, fix the issue on the same branch, commit, and push again.
- Never merge the Pull Request automatically.
- Never push directly to `main`.
- Wait for the user to review and approve the Pull Request.
- Do not report the task as complete until:
  - the feature branch is pushed
  - the Pull Request is open
  - CI has completed successfully
