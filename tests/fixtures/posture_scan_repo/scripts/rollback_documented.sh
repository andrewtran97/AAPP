#!/usr/bin/env bash
set -euo pipefail

# rollback: restore previous deployment if this fails
kubectl apply -f deploy.yml
