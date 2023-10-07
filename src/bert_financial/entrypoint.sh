#!/bin/bash

# Mount the GCS bucket
gcsfuse ac215_scraper_bucket /app/gcsbucket
#sudo gcsfuse -o allow_other -o uid=$(id -u appuser) -o gid=$(id -g appuser) ac215_scraper_bucket /app/gcsbucket


# Run the provided command or default to a shell
exec "$@"
