import re
from pathlib import Path


def test_csdb_url(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that the --cellservdb-url option correctly downloads the CellServDB file.
    """
    f = files_devel
    url = "https://www.example.com/CellServDB"
    result = cmd.run(makesrpm, "--source", f.srcball, "--cellservdb-url", url)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.example.com .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_csdb_url_does_not_skip_required_doc_archive(in_git_root, tmp_path, cmd, makesrpm):
    """
    Regression test: --cellservdb-url must not disable the scan for whether
    the spec file requires a separate doc archive (Source1). That scan
    currently lives in the same code path that only runs when
    --cellservdb-url is *not* given, so specifying --cellservdb-url against
    an old-style spec silently skips building the doc archive it needs.
    """
    spec_src = (in_git_root / "src/packaging/RedHat/openafs.spec.in").read_text()
    m = re.search(r"^Source0:.*\n", spec_src, re.MULTILINE)
    assert m, "Source0 directive not found; adjust the test fixture"
    needle = m.group(0)
    old_style_spec = spec_src.replace(
        needle,
        needle + "Source1: http://www.openafs.org/dl/openafs/%{afsvers}/openafs-%{afsvers}-doc.tar.bz2\n",
    )
    custom_spec = tmp_path / "openafs.spec.in"
    custom_spec.write_text(old_style_spec)

    rpm_build_dir = tmp_path / "rpmbuild"
    result = cmd.run(
        makesrpm, "--prepare-only", "--rpm-build-dir", rpm_build_dir, "--ignore-dirty",
        "--spec", custom_spec, "--cellservdb-url", "https://www.example.com/CellServDB",
    )
    assert result.returncode == 0, cmd.msg
    doc_archives = list((rpm_build_dir / "SOURCES").glob("openafs-*-doc.tar.bz2"))
    assert len(doc_archives) == 1, (
        "doc archive was not built even though the spec's Source1 requires one; "
        "--cellservdb-url likely suppressed the scan for it"
    )
