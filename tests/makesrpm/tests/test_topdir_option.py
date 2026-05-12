from pathlib import Path


def test_topdir_option(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that the --topdir option correctly uses the specified directory for
    rpmbuild.
    """
    topdir = in_tmp_dir / "my_topdir"
    topdir.mkdir()
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--topdir", topdir)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()

    specs_dir = topdir / "SPECS"
    sources_dir = topdir / "SOURCES"
    assert specs_dir.is_dir()
    assert sources_dir.is_dir()
    assert (topdir / "SRPMS").is_dir()

    assert (specs_dir / "openafs.spec").is_file()
    assert (sources_dir / f"openafs-{f.version}-src.tar.bz2").is_file()
    assert (sources_dir / "CellServDB.2025-08-16").is_file()
    assert (sources_dir / f"RELNOTES-{f.version}").is_file()
    assert (sources_dir / "ChangeLog").is_file()


def test_rpm_build_dir_option(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that the --rpm-build-dir option correctly uses the specified directory for
    rpmbuild.
    """
    topdir = in_tmp_dir / "my_topdir"
    topdir.mkdir()
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--rpm-build-dir", topdir)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()

    specs_dir = topdir / "SPECS"
    sources_dir = topdir / "SOURCES"
    assert specs_dir.is_dir()
    assert sources_dir.is_dir()
    assert (topdir / "SRPMS").is_dir()

    assert (specs_dir / "openafs.spec").is_file()
    assert (sources_dir / f"openafs-{f.version}-src.tar.bz2").is_file()
    assert (sources_dir / "CellServDB.2025-08-16").is_file()
    assert (sources_dir / f"RELNOTES-{f.version}").is_file()
    assert (sources_dir / "ChangeLog").is_file()


def test_topdir_with_output_option(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that --topdir works correctly with the --output option.
    """
    topdir = in_tmp_dir / "my_topdir"
    topdir.mkdir()
    output = in_tmp_dir / "output"
    output.mkdir()
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--topdir", topdir, "--output", output)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {output}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"output/{f.nvr}.src.rpm").is_file()

    specs_dir = topdir / "SPECS"
    sources_dir = topdir / "SOURCES"
    assert specs_dir.is_dir()
    assert sources_dir.is_dir()
    assert (topdir / "SRPMS").is_dir()

    assert (specs_dir / "openafs.spec").is_file()
    assert (sources_dir / f"openafs-{f.version}-src.tar.bz2").is_file()
    assert (sources_dir / "CellServDB.2025-08-16").is_file()
    assert (sources_dir / f"RELNOTES-{f.version}").is_file()
    assert (sources_dir / "ChangeLog").is_file()


def test_topdir_not_writable(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if the topdir is not writable.
    """
    topdir = in_tmp_dir / "my_topdir"
    topdir.mkdir()
    topdir.chmod(0o555)  # Make it read-only
    f = files_devel
    try:
        result = cmd.run(makesrpm, "--source", f.srcball, "--topdir", topdir)
        assert result.returncode != 0
        assert cmd.re_in_stderr(r".*/my_topdir/SPECS: Permission denied.*")
    finally:
        topdir.chmod(0o755)
