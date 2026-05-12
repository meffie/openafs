import tarfile
from pathlib import Path


def test_source_not_found(cmd, makesrpm):
    """
    Test that makesrpm.pl dies if the source tarball does not exist.
    """
    result = cmd.run(makesrpm, "--source", "nonexistent.tar.bz2")
    assert result.returncode != 0
    assert cmd.in_stderr("Source archive not found")


def test_doc_not_found(cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if the doc tarball does not exist.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--doc", "nonexistent.tar.bz2")
    assert result.returncode != 0
    assert cmd.in_stderr("Unable to copy nonexistent.tar.bz2 into position")


def test_relnotes_not_found(cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if the relnotes file does not exist.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--relnotes", "nonexistent")
    assert result.returncode != 0
    assert cmd.in_stderr("Unable to copy nonexistent into position")


def test_changelog_not_found(cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if the changelog file does not exist.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--changelog", "nonexistent")
    assert result.returncode != 0
    assert cmd.in_stderr("Unable to copy nonexistent into position")


def test_cellservdb_not_found(cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if the cellservdb file does not exist.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--cellservdb", "nonexistent")
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"Unable to copy nonexistent to .*")


def test_invalid_source_tarball(in_tmp_dir, cmd, makesrpm):
    """
    Test that makesrpm.pl dies if the source tarball is not a valid tarball.
    """
    invalid_tarball = in_tmp_dir / "invalid.tar.bz2"
    invalid_tarball.write_text("this is not a tarball")
    result = cmd.run(makesrpm, "--source", invalid_tarball)
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"'tar .*' exited with code 2")


def test_source_tarball_no_toplevel(in_tmp_dir, cmd, makesrpm):
    """
    Test that makesrpm.pl dies if the source tarball does not have the expected
    directory structure.
    """
    tarball = in_tmp_dir / "no_toplevel.tar.bz2"
    with tarfile.open(tarball, "w:bz2") as tar:
        dummy_file = in_tmp_dir / "dummy_file.txt"
        dummy_file.write_text("dummy content")
        tar.add(dummy_file, arcname="dummy_file.txt")
    assert tarball.is_file()

    result = cmd.run(makesrpm, "--source", tarball)
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"'tar .*' exited with code 2")


def test_missing_packaging_dir(in_tmp_dir, src_tarball, cmd, makesrpm):
    """
    Test that makesrpm.pl dies if the source tarball is missing the packaging directory.
    """
    src_tarball.include_packaging = False
    tarball = src_tarball.build()
    assert tarball.is_file()
    result = cmd.run(makesrpm, "--source", tarball)
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"'tar .*' exited with code 2")

def test_missing_csdb_source_directive(in_tmp_dir, src_tarball, cmd, makesrpm):
    """
    Test that makesrpm.pl dies if the spec file is missing the Source20 directive.
    """
    spec = Path("dummy.spec")
    spec.write_text("dummy")
    src_tarball.spec = spec
    tarball = src_tarball.build()
    assert tarball.is_file()
    result = cmd.run(makesrpm, "--source", tarball)
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"Unable to find CellServDB source directive in .*openafs\.spec.*")


def test_wget_fails(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if wget fails to download CellServDB.
    """
    f = files_devel
    cmd.env["WGET_FAIL"] = "1"
    result = cmd.run(makesrpm, "--source", f.srcball)
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"'wget .*' exited with code 1")


def test_rpmbuild_fails(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if rpmbuild fails.
    """
    f = files_devel
    cmd.env["RPMBUILD_FAIL"] = "1"
    result = cmd.run(makesrpm, "--source", f.srcball)
    assert result.returncode != 0
    assert cmd.in_stderr(r"rpmbuild failed")


def test_output_dir_not_writable(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if the output directory is not writable.
    """
    f = files_devel
    output_dir = in_tmp_dir / "output"
    output_dir.mkdir()
    output_dir.chmod(0o555)
    try:
        result = cmd.run(makesrpm, "--source", f.srcball, "--output", output_dir)
        assert result.returncode != 0
        assert cmd.re_in_stderr(r"Failed to copy '.*' to '.*': Permission denied")
    finally:
        output_dir.chmod(0o755)
