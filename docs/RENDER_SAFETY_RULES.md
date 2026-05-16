# RENDER SAFETY RULES

## Correct
Batch 01: Scene 01–06.
Render Scene 01 only. When Scene 01 completes, render Scene 02.

## Incorrect
Batch 01 has 6 scenes and all 6 scenes render at the same time.

## Pseudo code
```python
for batch in batches:
    for scene in batch.scenes:
        render_scene(scene)
        wait_until_completed(scene)
```
