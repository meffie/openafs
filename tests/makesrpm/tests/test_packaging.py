from pathlib import Path


def test_packaging_option(in_tmp_dir, cmd, makesrpm, files_devel, git_root):
    f = files_devel
    packaging = git_root / "src/packaging/RedHat"
    assert packaging.is_dir()
    result = cmd.run(makesrpm, "--source", f.srcball, "--packaging", packaging)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()
