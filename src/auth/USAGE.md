# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

- For local development, set environment variable `AUTH_SECRET=dev-only` before running the server with uvicorn.

## Common commands

- Run tests with `pytest tests/auth -q`.
- Start the development server with `uvicorn app.main:app --reload --port 8000`.

## Debugging

- If receiving a 401 on a valid token, check for clock skew and verify that the `AUTH_SECRET` matches the issuer.

## Troubleshooting
