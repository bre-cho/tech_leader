URL | HTTP Code | Body Preview
---|---|---
http://localhost:3000/api/v1/creative-os/provider-profiles | 000Connection Refused | 
http://localhost:3000/api/v1/creative-os/projects/demo-project/plan-storyboard (POST) | 000Connection Refused | 
http://localhost:3000/api/v1/creative-os/projects/demo-project/render-steps | 000Connection Refused | 
http://localhost:8000/api/v1/creative-os/provider-profiles | 200 | {"veo":{"provider":"veo","recommended_duration_per_scene":8.0,"max_duration_per_scene":10.0,"default
http://localhost:8000/api/v1/creative-os/projects/demo-project/plan-storyboard (POST) | 200 | {"project_id":"demo-project","image_source":"upload","image_url":"/uploads/demo.png","target_video_d
http://localhost:8000/api/v1/creative-os/projects/demo-project/render-steps | 200 | [{"batch_index":1,"scene_index":1,"status":"queued","max_concurrent_render":1,"execution_mode":"sequ
