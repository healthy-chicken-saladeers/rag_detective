# Test start up of Fast API  
uvicorn api.service:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"

# Access in browser at: http://0.0.0.0:9000/
