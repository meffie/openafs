from pathlib import Path


def test_release_2_args(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with 2 positional arguments (source, doc).
    """
    f = files_release
    result = cmd.run(makesrpm, f.srcball, f.docball)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_release_3_args(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with 3 positional arguments (source, doc, relnotes).
    """
    f = files_release
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_release_4_args(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with 4 positional arguments (source, doc, relnotes, changelog).
    """
    f = files_release
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes, f.changelog)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_release_5_args(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with 5 positional arguments (all files).
    """
    f = files_release
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes, f.changelog, f.cellservdb)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert not cmd.re_in_stderr("Connecting to www.central.org .*")
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_2_args(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with 2 positional arguments (source, doc).
    """
    f = files_prerelease
    result = cmd.run(makesrpm, f.srcball, f.docball)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_3_args(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with 3 positional arguments (source, doc, relnotes).
    """
    f = files_prerelease
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_4_args(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with 4 positional arguments (source, doc, relnotes, changelog).
    """
    f = files_prerelease
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes, f.changelog)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_5_args(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with 5 positional arguments (all files).
    """
    f = files_prerelease
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes, f.changelog, f.cellservdb)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert not cmd.re_in_stderr("Connecting to www.central.org .*")
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_1_arg(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with 1 positional argument (source).
    """
    f = files_devel
    result = cmd.run(makesrpm, f.srcball)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_2_args(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with 2 positional arguments (source, doc).
    """
    f = files_devel
    result = cmd.run(makesrpm, f.srcball, f.docball)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_3_args(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with 3 positional arguments (source, doc, relnotes).
    """
    f = files_devel
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_4_args(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with 4 positional arguments (source, doc, relnotes, changelog).
    """
    f = files_devel
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes, f.changelog)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_5_args(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with 5 positional arguments (all files).
    """
    f = files_devel
    result = cmd.run(makesrpm, f.srcball, f.docball, f.relnotes, f.changelog, f.cellservdb)
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert not cmd.re_in_stderr("Connecting to www.central.org .*")
    assert Path(f"{f.nvr}.src.rpm").is_file()
