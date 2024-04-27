from pathlib import Path
import re

MARKER_START = "<!-- BEGIN README INSERT -->"
MARKER_END = "<!-- END README INSERT -->"


def fix_markdown(data: str, doc_url: str) -> str:
    # quick & dirty way to fix markdown data
    # so that it is compatible with GitHub, PyPi, etc.

    # fix code blocks
    indentation = " " * 4
    lines = []
    in_code = False
    for line in data.split("\n"):
        if line.startswith(f"{indentation}:::python"):
            assert not in_code
            in_code = True
            lines.append("```python")
        elif in_code:
            if not line or line.startswith(indentation):
                lines.append(line.lstrip(indentation))
            else:
                in_code = False
                while not (last_line := lines.pop()):
                    pass
                lines.append(last_line)
                lines.append("```")
                lines.append("")
                lines.append(line)
        else:
            lines.append(line)
    assert not in_code
    data = "\n".join(lines)

    # fix links
    return re.sub(
        r"]\(([^.)]+)\.md(#[^)]+)?\)",
        rf"]({doc_url}/\1/\2)",
        data,
    )


def test_readme_content() -> None:
    test_path = Path(__file__).parent
    data_index = (test_path / "src" / "index.md").read_text()
    data_readme = (test_path / ".." / "README.md").read_text()
    doc_url = f"https://{(test_path / 'src' / 'CNAME').read_text().strip()}"

    assert MARKER_START in data_index
    assert MARKER_END in data_index
    assert MARKER_START in data_readme
    assert MARKER_END in data_readme

    data_readme_expected = (
        data_readme[: data_readme.find(MARKER_START)]
        + fix_markdown(
            data_index[
                data_index.find(MARKER_START) : data_index.rfind(MARKER_END)
                + len(MARKER_END)
            ],
            doc_url,
        )
        + data_readme[data_readme.rfind(MARKER_END) + len(MARKER_END) :]
    )

    needs_to_be_changed = data_readme != data_readme_expected

    if needs_to_be_changed:
        (test_path / ".." / "README.md").write_text(data_readme_expected)
        raise RuntimeError(
            "The test files have changed and have been updated accordingly. "
            "Please re-run the tests."
        )
