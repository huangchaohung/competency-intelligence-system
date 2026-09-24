# Session collector security boundaries

- No in-app administrator panel. All approved visitors can scan/edit **their own temporary copy**, never the master. Use platform-level restricted sharing; the application is not hardened for arbitrary anonymous internet users.
- Session isolation is not enterprise authentication, secure memory erasure or an OS boundary. Scan evidence is not saved by the app to disk; hosting/browser/process diagnostics and caches are outside that guarantee.
- URL configuration is now available to visitors. HTTPS validation is **not comprehensive SSRF protection**: private IP ranges, redirects and DNS rebinding require an IT-managed egress policy before wider exposure. Do not deploy on an internal network with unrestricted access to internal services.
- Multiple scans can exhaust RAM/browser/network resources. There is no per-user quota or distributed queue. Restrict testers and load-test before production.
- Public STE data only; internal frameworks and AI analysis belong on approved government systems. Downloaded text can contain PII/copyrighted content/prompt injection. Treat it as untrusted data.
- Do not bypass robots/challenges, share authentication cookies or disable TLS verification.
- Keep legacy databases, logs, backups, evidence and secrets out of Git. Existing old disk files are not erased by this release and may need separately authorized cleanup.

Report vulnerabilities privately through an established team channel. Never post secrets/internal data in public issues. Assign a security owner before operational rollout.
