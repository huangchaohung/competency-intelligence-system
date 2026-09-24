# Security boundaries — private trial

- Public STE data only. Internal frameworks and analysis belong in the approved government environment.
- `app.py` uses a shared admin password for edits/scans locally and in cloud; missing secrets fail closed to read-only. `cloud_app.py` delegates to the same entrypoint. Separately restrict platform access for viewers. This is not SSO, MFA, individual attribution or enterprise brute-force protection.
- All cloud viewers share results. TXT does not imply transfer approval. Public text can contain personal information, copyrighted content or prompt injection; treat it as untrusted data downstream.
- Editing URLs is privileged. HTTPS validation/basic export URL checks are **not comprehensive SSRF protection**. Private addresses, DNS rebinding and redirects need IT-managed egress controls before allowing untrusted configuration.
- No CAPTCHA/access-control bypass, authentication-cookie sharing or TLS-verification disabling.
- Keep secrets, databases, logs, evidence and backups out of Git. Old databases may still contain sensitive framework/recommendation/chat data.
- Cloud storage is temporary; locking is single-instance. Review dependency updates, browser sandboxing, resource quotas and hosting approval before production.

Report suspected vulnerabilities privately to the repository owner through an established team channel. Stop affected sharing, retain sanitized diagnostics and rotate exposed secrets. Do not post sensitive data or exploitable deployment details in public issues. Assign a security owner before operational rollout.
