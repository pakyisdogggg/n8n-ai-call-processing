# Security and data handling

This is a sanitized example, not a live configuration.

- No account credentials, OAuth tokens, API keys, real client data or live spreadsheet identifiers should be committed.
- Never commit `.env`, execution logs, raw transcripts, screenshots with real user data, or n8n credential exports.
- Keep secrets in n8n Credentials or a managed secret store.
- Live enrichment endpoints and spreadsheet references have been replaced by placeholders.
- If an unredacted export was ever committed, remove it from repository history and **rotate any exposed secrets**.
- Obtain permission before publishing client-owned intellectual property; data sanitization alone is not a publication license.
