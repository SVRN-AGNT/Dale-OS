#!/usr/bin/env bash
# Copy this case's sample repository into the run's working directory.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd -P)
root=$(cd "$here/../../.." && pwd -P)
case "$(pwd -P)/" in
  "$root"/*) echo "refusing to scaffold inside the repository" >&2; exit 1 ;;
esac
cp -R "$here/repo/." .
