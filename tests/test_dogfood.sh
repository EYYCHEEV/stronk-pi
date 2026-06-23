#!/bin/sh
set -eu

if [ "${STRONKPI_DOGFOOD:-0}" != "1" ]; then
  printf '%s\n' "dogfood skipped; set STRONKPI_DOGFOOD=1"
  exit 0
fi

setup_resolved=$(command -v stronkpi-setup)
case "$setup_resolved" in
  */stronk-pi/bin/stronkpi-setup|*/stronk-pi-setup/bin/stronkpi-setup|*/.local/bin/stronkpi-setup)
    ;;
  *)
    printf '%s\n' "unexpected stronkpi-setup path: $setup_resolved" >&2
    exit 1
    ;;
esac

STRONKPI_NO_NETWORK=1 stronkpi-setup validate

if [ "${STRONKPI_DOGFOOD_HARNESS:-0}" = "1" ]; then
  stronkpi --validate-only
fi
