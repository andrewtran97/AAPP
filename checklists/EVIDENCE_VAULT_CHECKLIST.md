# Evidence Vault Checklist

## Intake

- [ ] Written scope exists
- [ ] Scope JSON exists
- [ ] Scope allows actor type
- [ ] Scope allows tool type
- [ ] Raw intake triaged out of 00-INBOX

## Bundle

- [ ] AAPP bundle exists
- [ ] evidence.bundle.json exists
- [ ] hashes.txt exists
- [ ] verification_result.md exists
- [ ] trace.jsonl exists
- [ ] scope.json exists
- [ ] evidence.report.md exists

## Redaction

- [ ] Secret-like values scanned
- [ ] Raw credentials removed
- [ ] Private keys removed
- [ ] API tokens removed
- [ ] Personal data minimized
- [ ] Public-safe material separated

## Disclosure

- [ ] Maintainer report prepared
- [ ] Timeline prepared
- [ ] Embargo or patch window defined
- [ ] Public publication blocked until disclosure gate passes

## Audit

- [ ] Vault audit log updated
- [ ] Bundle movement logged
- [ ] Disclosure event logged
- [ ] Publication event logged if applicable
