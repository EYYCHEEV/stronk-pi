## Summary

- 

## Verification

- [ ] `STRONKPI_NO_NETWORK=1 zsh tests/run_offline.zsh`
- [ ] `gitleaks detect --source . --no-git --config .gitleaks.toml --redact --verbose`

## Security Checklist

- [ ] No credentials, sessions, caches, or local runtime state added.
- [ ] Public command surface remains `stronkpi`.
- [ ] Manifest changes use immutable artifacts and checksums.

