#!/bin/bash

# Smart build script for Cloudflare Pages
# Only rebuilds if posts/ directory changed (remote CRUD)
# Skips build if site/ already updated (local push)

set -e  # Exit on error

echo "🔍 Checking if build is needed..."

# Check if this commit touched posts/ directory
POSTS_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | grep '^posts/' || true)

# Check if site/ was updated
SITE_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | grep '^site/' || true)

if [ -n "$POSTS_CHANGED" ] && [ -z "$SITE_CHANGED" ]; then
    echo "✅ Posts changed but site/ not updated - building..."
    python3 -m pip install -r requirements.txt
    python3 build.py
    echo "✅ Build complete"
elif [ -n "$SITE_CHANGED" ]; then
    echo "✅ Site already built locally - skipping build"
    echo "✅ Deploying pre-built site/"
else
    echo "✅ No relevant changes - deploying existing site/"
fi

echo "✅ Ready to deploy"
