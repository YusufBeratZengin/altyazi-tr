## Description

Brief summary of changes made and motivation behind them.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Documentation update
- [ ] Performance improvement or refactoring
- [ ] CI or release automation

## Verification and Checks

Commands run and test results:
- [ ] `python -m pytest -q` passes without network access or downloading models
- [ ] `python -m ruff check .` passes
- [ ] `python -m ruff format --check .` passes
- [ ] `python -m mypy` passes with strict typing
- [ ] `python -m build && python -m twine check dist/*` passes

## Privacy and Guidelines Checklist

- [ ] No real personal data, identity numbers, phone numbers, or private audio/video files are included
- [ ] No credentials, tokens, or private keys are staged
- [ ] Documentation changes are reflected in both `README.md` and `README.tr.md`
