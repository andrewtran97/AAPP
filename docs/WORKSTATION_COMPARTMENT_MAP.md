# Workstation Compartment Map

| Compartment | Purpose | Allowed | Forbidden |
|---|---|---|---|
| C0-HOST-BASELINE | Git, signing, hooks | repo operations, signed commits, signed tags | raw secrets, exploit material |
| C1-SCOPE-CONTROL | written scope | scope JSON, authorization notes | credentials, private keys |
| C2-RESEARCH-SANDBOX | local research | fixtures, fake targets, synthetic traces | live target scanning |
| C3-AAPP-TRACE | trace generation | trace.jsonl, verification output | raw secrets, production private keys |
| C4-EVIDENCE-BUNDLE | bundle creation | manifest, hashes, verification result | unredacted exploit steps |
| C5-REDACTION | sanitization | redaction log, field list | raw secrets in final notes |
| C6-DISCLOSURE | private report | maintainer report, timeline | coercion, extortion |
| C7-PUBLISHABLE | public-safe release | sanitized demo, limitations | secrets, unsupported claims |
| C8-KEY-REFERENCE | key references | fingerprint, key ID | private keys, tokens |
