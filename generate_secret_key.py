#!/usr/bin/env python3
"""
Generate a cryptographically secure SECRET_KEY for production use
"""

import secrets

print("=" * 60)
print("SECRET KEY GENERATOR")
print("=" * 60)
print()
print("Generating a cryptographically secure secret key...")
print()

# Generate a secure random key
secret_key = secrets.token_urlsafe(32)

print("Your new SECRET_KEY:")
print("-" * 60)
print(secret_key)
print("-" * 60)
print()
print("✅ Copy this key to your .env file:")
print(f'SECRET_KEY="{secret_key}"')
print()
print("⚠️  IMPORTANT:")
print("  - Never commit this key to git")
print("  - Never share this key publicly")
print("  - Use different keys for dev/staging/production")
print("  - Store securely (use secrets manager in production)")
print()
print("=" * 60)
