#!/bin/bash

# Mount the GCS bucket
sudo gcsfuse -o allow_other,default_permissions ac215_scraper_bucket /app/gcsbucket

# Run the provided command or default to a shell
exec "$@"
