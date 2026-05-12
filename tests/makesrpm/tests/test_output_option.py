from pathlib import Path


def test_output_option(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that the --output option correctly places the SRPM in the specified directory.
    """
    output = in_tmp_dir / "output"
    output.mkdir()
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--output", output)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {output}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"output/{f.nvr}.src.rpm").is_file()


def test_dir_alias(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that the --dir alias for --output works correctly.
    """
    output = in_tmp_dir / "output"
    output.mkdir()
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--dir", output)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {output}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"output/{f.nvr}.src.rpm").is_file()


def test_output_option_with_pos(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that --output works correctly with positional arguments.
    """
    output = in_tmp_dir / "output"
    output.mkdir()

    f = files_devel
    result = cmd.run(makesrpm, f.srcball, f.docball, "--output", output)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {output}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"output/{f.nvr}.src.rpm").is_file()


def test_dir_alias_with_pos(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that the --dir alias works correctly with positional arguments.
    """
    output = in_tmp_dir / "output"
    output.mkdir()

    f = files_devel
    result = cmd.run(makesrpm, f.srcball, f.docball, "--dir", output)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {output}/{f.nvr}.src.rpm"), cmd.msg
    assert Path(f"output/{f.nvr}.src.rpm").is_file()
