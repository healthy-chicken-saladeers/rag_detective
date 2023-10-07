#!/bin/bash
    
# Create the directory if it doesn't exist
mkdir -p /app/gcsbucket

# Mount the GCS bucket
gcsfuse ac215_scraper_bucket /app/gcsbucket

# Run the provided command or default to a shell
exec "$@"
