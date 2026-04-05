#!/bin/bash

# Start Postgres
brew services start postgresql@15

# Run your project (adjust this line to whatever starts your pipeline)
python batch_runner.py --input-dir ./pdfs --output-dir ./extracted

# Stop Postgres when done
brew services stop postgresql@15