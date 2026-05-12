from pathlib import Path


def test_prepare_only_with_topdir(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that --prepare-only with --topdir prepares the directory and exits.
    """
    topdir = in_tmp_dir / "my_topdir"
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--prepare-only", "--topdir", topdir)

    assert result.returncode == 0
    assert not Path(f"{f.nvr}.src.rpm").exists()
    assert cmd.in_stdout("SRPM build skipped"), cmd.msg

    assert (topdir / "SPECS" / "openafs.spec").is_file()
    assert (topdir / "SOURCES" / f"openafs-{f.version}-src.tar.bz2").is_file()


def test_prepare_only_without_topdir(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that --prepare-only without --topdir uses the default from 'rpm --eval'.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--prepare-only")
    mock_topdir = in_tmp_dir / "mock_topdir"

    assert result.returncode == 0
    assert not Path(f"{f.nvr}.src.rpm").exists()
    assert cmd.in_stdout("SRPM build skipped"), cmd.msg

    assert (mock_topdir / "SPECS" / "openafs.spec").is_file()
    assert (mock_topdir / "SOURCES" / f"openafs-{f.version}-src.tar.bz2").is_file()


def test_prepare_only_rpm_eval_fails(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that --prepare-only fails if 'rpm --eval' fails and --topdir is not given.
    """
    f = files_devel
    cmd.env["RPM_EVAL_FAIL"] = "1"
    result = cmd.run(makesrpm, "--source", f.srcball, "--prepare-only")

    assert result.returncode != 0
    assert cmd.re_in_stderr(r"makesrpm: Command 'rpm --eval %{_topdir}' failed with exit code 1"), cmd.msg
