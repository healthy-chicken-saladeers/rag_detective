#!/bin/bash

# Mount the GCS bucket
gcsfuse ac215_scraper_bucket /app/gcsbucket

# Run the provided command or default to a shell
exec "$@"
