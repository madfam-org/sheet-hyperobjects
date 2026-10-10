# Security

> Boundary checkpoint (2026-10-10): public policy. Report privately; never post a vulnerability in
> a public issue.

Report vulnerabilities through GitHub's private vulnerability reporting for this repository:
<https://github.com/madfam-org/sheet-hyperobjects/security/advisories/new>. We acknowledge reports
within three business days.

In a commons of generator scripts, the highest-severity issues are:

- **A cartridge that escapes its sandbox** — a `main.py` that reads files, opens the network, spawns
  processes or exhausts resources when Pliego or CI runs it.
- **Content injection** — script or markup in a manifest, label or article that executes in the
  studio or the encyclopaedia.
- **A secret or personal data** committed in any file or commit message.

Attribution and licensing disputes are not security reports; open an issue.
