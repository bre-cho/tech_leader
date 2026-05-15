# Local VideoFlow Integration

This folder vendors the VideoFlow source used by the tech leader MVP as a local reference implementation.

Primary usage in this MVP is through `lib/videoflow/*`, which converts storyboard/provider outputs into a renderer-neutral VideoFlow JSON contract. Keeping the upstream source here makes it easy to later switch from contract-only export to `@videoflow/core`, `@videoflow/renderer-dom`, or `@videoflow/renderer-server` without rewriting the creative pipeline.
