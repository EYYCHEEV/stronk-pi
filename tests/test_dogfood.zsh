#!/usr/bin/env zsh
set -euo pipefail

if [[ "${STRONKPI_DOGFOOD:-0}" != "1" ]]; then
  print -r -- "dogfood skipped; set STRONKPI_DOGFOOD=1"
  exit 0
fi

resolved="$(command -v stronkpi)"
case "$resolved" in
  */stronk-pi-setup/bin/stronkpi|*/.local/bin/stronkpi)
    ;;
  *)
    print -r -- "unexpected stronkpi path: $resolved" >&2
    exit 1
    ;;
esac

STRONKPI_NO_NETWORK=1 stronkpi validate

