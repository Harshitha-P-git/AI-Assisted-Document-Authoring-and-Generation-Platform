#!/usr/bin/env python3
"""
Quick script to generate a secure SECRET_KEY for your .env file
Run: python generate_secret_key.py
"""
import secrets

def generate_secret_key():
    """Generate a secure random secret key"""
    key = secrets.token_urlsafe(32)
    print("\n" + "="*60)
    print("Generated SECRET_KEY:")
    print("="*60)
    print(key)
    print("="*60)
    print("\nCopy this key and paste it into your .env file as:")
    print(f"SECRET_KEY={key}")
    print("\n")
    return key

if __name__ == "__main__":
    generate_secret_key()

