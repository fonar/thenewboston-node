#!/usr/bin/env bash

set -e

# We need to collect static files to make WhiteNoise work (and we need to do it here)
# TODO(dmu) LOW: Collect static once, not on every run (we need to have named volume for it)
poetry run python -m thenewboston_node.manage collectstatic

# TODO(dmu) MEDIUM: We might reconsider using `daphne` after figuring out if we have IO-bound or
#                   CPU-bound application
poetry run daphne -b 0.0.0.0 -p 8555 thenewboston_node.project.asgi:application
