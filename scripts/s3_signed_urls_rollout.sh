#!/bin/bash
#
# S3 Signed URLs Rollout Script
# Locks down the tieulgnu bucket so only presigned URLs work for downloads.
#
# REQUIRES: aws CLI configured with an account that has s3:PutBucketPolicy
#           permission (s3user may NOT have this — may need Eric's root/admin creds)
#
# Three phases, run manually one at a time:
#
#   Phase 1: DRY RUN   — verify presigned URLs work against a test prefix
#   Phase 2: FLIP      — remove public access, deploy signed URL code to prod
#   Phase 3: ROLLBACK  — restore public access if something breaks
#
# Usage:
#   ./s3_signed_urls_rollout.sh dry-run
#   ./s3_signed_urls_rollout.sh flip
#   ./s3_signed_urls_rollout.sh rollback

set -euo pipefail

BUCKET="tieulgnu"

# Save current policy for rollback
ORIGINAL_POLICY='{
  "Version": "2008-10-17",
  "Id": "http referer policy example",
  "Statement": [
    {
      "Sid": "readonly policy",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::tieulgnu/*"
    }
  ]
}'

case "${1:-help}" in

  dry-run)
    echo "=== PHASE 1: DRY RUN ==="
    echo ""
    echo "This verifies that presigned URLs work before we lock anything down."
    echo ""

    # Pick a known file to test with
    TEST_KEY="ebf/f0e0db70a7174a94ab9e551eaab8fc19.pdf"

    echo "1. Testing UNSIGNED access (should work — bucket is still public):"
    echo "   curl -s -o /dev/null -w '%{http_code}' https://${BUCKET}.s3.amazonaws.com/${TEST_KEY}"
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "https://${BUCKET}.s3.amazonaws.com/${TEST_KEY}")
    echo "   Result: HTTP ${HTTP_CODE}"
    echo ""

    echo "2. Generating presigned URL (5 min expiry):"
    SIGNED_URL=$(aws s3 presign "s3://${BUCKET}/${TEST_KEY}" --expires-in 300)
    echo "   ${SIGNED_URL}"
    echo ""

    echo "3. Testing SIGNED access (should also work):"
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "${SIGNED_URL}")
    echo "   Result: HTTP ${HTTP_CODE}"
    echo ""

    if [ "${HTTP_CODE}" = "200" ]; then
      echo "PASS: Presigned URLs work. Safe to proceed to 'flip' phase."
    else
      echo "FAIL: Presigned URL returned ${HTTP_CODE}. Do NOT proceed."
      exit 1
    fi
    ;;

  flip)
    echo "=== PHASE 2: FLIP — Remove public access ==="
    echo ""
    echo "WARNING: This will immediately break ALL unsigned S3 URLs."
    echo "         Production must be running signed-download-urls code FIRST."
    echo ""
    read -p "Has signed-download-urls been deployed to production? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Aborting. Deploy the code first, then run this."
      exit 1
    fi

    echo "Removing public access policy from ${BUCKET}..."
    aws s3api delete-bucket-policy --bucket "${BUCKET}"
    echo "Done. Bucket policy removed."
    echo ""

    echo "Enabling S3 Block Public Access (prevents accidental re-opening)..."
    aws s3api put-public-access-block --bucket "${BUCKET}" \
      --public-access-block-configuration \
      'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
    echo "Done."
    echo ""

    echo "=== VERIFY ==="
    TEST_KEY="ebf/f0e0db70a7174a94ab9e551eaab8fc19.pdf"

    echo "Unsigned access (should be 403 now):"
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "https://${BUCKET}.s3.amazonaws.com/${TEST_KEY}")
    echo "  HTTP ${HTTP_CODE}"

    echo "Signed access (should be 200):"
    SIGNED_URL=$(aws s3 presign "s3://${BUCKET}/${TEST_KEY}" --expires-in 300)
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "${SIGNED_URL}")
    echo "  HTTP ${HTTP_CODE}"

    if [ "${HTTP_CODE}" = "200" ]; then
      echo ""
      echo "SUCCESS: Bucket locked down. Signed URLs working."
      echo "Test downloads on https://unglue.it and https://test.unglue.it"
    else
      echo ""
      echo "PROBLEM: Signed URL returned ${HTTP_CODE}. Consider rollback."
    fi
    ;;

  rollback)
    echo "=== PHASE 3: ROLLBACK — Restore public access ==="
    echo ""
    echo "This restores the original bucket policy (public read for all objects)."
    echo ""
    read -p "Are you sure you want to make the bucket public again? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Aborting."
      exit 1
    fi

    echo "Removing Block Public Access..."
    aws s3api delete-public-access-block --bucket "${BUCKET}"

    echo "Restoring original bucket policy..."
    aws s3api put-bucket-policy --bucket "${BUCKET}" --policy "${ORIGINAL_POLICY}"

    echo "Done. Bucket is public again."
    echo ""
    echo "Verify unsigned access works:"
    TEST_KEY="ebf/f0e0db70a7174a94ab9e551eaab8fc19.pdf"
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "https://${BUCKET}.s3.amazonaws.com/${TEST_KEY}")
    echo "  HTTP ${HTTP_CODE}"
    ;;

  *)
    echo "Usage: $0 {dry-run|flip|rollback}"
    echo ""
    echo "  dry-run   — Verify presigned URLs work (safe, changes nothing)"
    echo "  flip      — Remove public access (BREAKS unsigned URLs)"
    echo "  rollback  — Restore public access (emergency undo)"
    exit 1
    ;;
esac
