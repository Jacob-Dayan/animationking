"""
Entrypoint for `python -m animationking`.

Runs `uv run animationking` and passes all args got via `sys.argv` as a subprocess,
then exits with the return code of the subprocess.

```bash
uv run animationking "$@"
```
"""

import subprocess
import sys

result = subprocess.run(["uv", "run", "animationking", *sys.argv[1:]])
sys.exit(result.returncode)
