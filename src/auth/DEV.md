# DEV — engineering knowledge

> How this part of the system is built.

## Design decisions

- Authentication middleware is located in `src/auth/`.
- Token verification is separated from user lookup.
- Tokens are currently signed with HS256; plan to migrate to RS256 later.

## Patterns

- Use a `require_auth` decorator on all protected routes.
- The decorator reads the `Authorization: Bearer` header to obtain the token.

## Pitfalls
- Avoid logging the raw `Authorization` header as it contains secrets.
