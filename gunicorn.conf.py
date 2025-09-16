# Gunicorn config focused on low memory usage for small containers
# Adjust values as needed for your environment

workers = 1
threads = 1
worker_class = "gthread"

# Kill slow requests, avoid stuck workers
timeout = 60
graceful_timeout = 30

# Recycle workers periodically to avoid leaks
max_requests = 200
max_requests_jitter = 50

# Bind defaults are controlled by platform (Render), override if running locally
# bind = "0.0.0.0:8000"