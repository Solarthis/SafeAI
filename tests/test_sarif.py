import json

import pytest

from safeai.report.sarif import write_sarif


def test_sarif_structure(tmp_path):
    report = {
        "findings": [
            {
                "rule_id": "TEST",
                "message": "msg",
                "file": "a.py",
                "line": 1,
                "severity": "low",
                "owasp_llm": "LLM01",
            }
        ],
        "counts": {},
    }

    out = tmp_path / "out.sarif"
    write_sarif(report, str(out))

    data = json.loads(out.read_text())
    assert data["version"] == "2.1.0"
    assert "runs" in data


def render_result(tmp_path, **overrides):
    finding = {"rule_id": "TEST", "message": "msg", "file": "a.py", "line": 1, "severity": "low"}
    finding.update(overrides)
    out = tmp_path / "out.sarif"
    write_sarif({"findings": [finding]}, str(out))
    return json.loads(out.read_text())["runs"][0]["results"][0]


@pytest.mark.parametrize("line", [0, -1, None, True, "3"])
def test_unknown_line_does_not_invent_invalid_region(tmp_path, line):
    result = render_result(tmp_path, line=line)
    assert "region" not in result["locations"][0]["physicalLocation"]


def test_missing_file_has_no_fabricated_location(tmp_path):
    assert "locations" not in render_result(tmp_path, file=None)


def test_file_path_reserved_characters_are_uri_encoded(tmp_path):
    result = render_result(tmp_path, file="src/a b#c%?.py")
    assert result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "src/a%20b%23c%25%3F.py"


@pytest.mark.parametrize("severity,level", [("critical", "error"), ("high", "error"), ("medium", "warning"), ("low", "note"), ("info", "note")])
def test_finding_severity_is_preserved(tmp_path, severity, level):
    result = render_result(tmp_path, severity=severity)
    assert result["level"] == level
    assert result["properties"]["severity"] == severity


def test_positive_line_is_preserved(tmp_path):
    result = render_result(tmp_path, line=42)
    assert result["locations"][0]["physicalLocation"]["region"] == {"startLine": 42}


@pytest.mark.parametrize("path,uri", [
    ("/tmp/a b.py", "file:///tmp/a%20b.py"),
    ("C:\\src\\a b.py", "file:///C:/src/a%20b.py"),
    ("src/é.py", "src/%C3%A9.py"),
    ("src\\file.py", "src/file.py"),
])
def test_cross_platform_file_uris(tmp_path, path, uri):
    result = render_result(tmp_path, file=path)
    assert result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == uri


def test_unknown_severity_keeps_warning_default(tmp_path):
    result = render_result(tmp_path, severity="unknown")
    assert result["level"] == "warning"
    assert result["properties"]["severity"] == "unknown"
