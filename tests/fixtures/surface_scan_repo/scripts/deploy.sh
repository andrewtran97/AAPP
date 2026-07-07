#!/usr/bin/env bash
set -euo pipefail

terraform apply -auto-approve
kubectl apply -f deploy.yml
aws s3 cp report.json s3://example-bucket/report.json
