# SARIF export review

Four interoperability fixes:

- Omit a region when the finding has no positive integer source line; do not invent line 1 or serialize null/zero/bool as a source line.
- Omit physical locations when the finding has no file.
- Encode file paths as URI references, including reserved characters, Unicode and Windows/Unix absolute paths.
- Preserve the original severity in properties and map critical/high to error, medium to warning, low/info to note. Unknown values retain SARIF's warning default.

Reference: [OASIS SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html), artifactLocation, region and result level definitions. Mapping SafeAI's five severities to SARIF's levels is the exporter's policy; the original severity remains available.

Nineteen focused SARIF tests pass; twelve new cases failed on the initial code. Ruff passes. The first complete test run had 617 passes, one skip and 12 telemetry failures because the test environment's home directory is read-only. An isolated temporary HOME is used for the full rerun so telemetry fixture state cannot reach an existing user's configuration. No model/provider is used. Native GitHub/Azure SARIF upload and UI behavior remain unverified. Draft proposal in this fork only; no upstream submission or release.

Final isolated-HOME full suite: **629 passed, 1 skipped** on Python 3.12. Ruff and git diff whitespace checks pass. The skipped test is retained as an existing suite skip, not counted as a pass.
