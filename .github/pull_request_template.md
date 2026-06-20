## Summary

- 

## Verification

- [ ] `STRONKPI_NO_NETWORK=1 sh tests/run_offline.sh`
- [ ] `gitleaks detect --source . --no-git --config .gitleaks.toml --redact --verbose`

## Security Checklist

- [ ] No credentials, sessions, caches, or local runtime state added.
- [ ] Setup command remains `stronkpi-setup`; harness command remains `stronkpi`.
- [ ] Manifest changes use immutable artifacts and checksums.
