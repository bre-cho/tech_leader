# RENDER SAFETY RULES

## Đúng
Batch 01 gồm 6 cảnh nhưng render tuần tự:
Scene 01 completed → Scene 02 starts → Scene 03 starts...

## Sai
Batch 01 gồm 6 cảnh → render cả 6 cảnh cùng lúc.

## Pseudo code
```python
for batch in batches:
    for scene in batch.scenes:
        render_scene(scene)
        wait_until_completed(scene)
        if scene.failed:
            retry_scene(scene)
```
