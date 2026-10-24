# Frozen artifact protection

Before/after: record exact root, Git status/HEAD and manifest hashes. Stream SHA256
over declared files only; reject traversal, absolute manifest paths and linked/junction
components. Never follow private/raw references or deserialize checkpoints. Report
missing/mismatching files individually, and distinguish historical drift from changes
during this audit. An empty or malformed manifest is an error, not a vacuous PASS.

Manifest formats supported: Markdown `| relative-path | sha256 |`; flat JSON mapping;
or an explicitly selected JSON key containing that mapping. Do not silently select
among historical and current-release manifests. Do not execute a verifier that opens
private data or recomputes performance. Review it first.

Report stdout by default. If writing is separately authorized, use the project's
reviewed runtime guard, an allowed fresh staging/reproduction run, exclusive file
creation and no cleanup-on-error. No output flag in a helper can broaden permission.
Path checks alone do not provide OS sandboxing or eliminate concurrent TOCTOU attacks.

Synthetic tests may use their own TemporaryDirectory. Real symlink tests skipped for
Windows privilege 1314 remain skipped, not integration PASS. No installation to fix it.
