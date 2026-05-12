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
