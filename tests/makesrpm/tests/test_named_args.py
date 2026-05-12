from pathlib import Path


def test_release_sd(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with --source and --doc.
    """
    f = files_release
    result = cmd.run(makesrpm, "--source", f.srcball, "--doc", f.docball)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_release_sdr(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with --source, --doc, and --relnotes.
    """
    f = files_release
    result = cmd.run(makesrpm, "--source", f.srcball, "--doc", f.docball, "--relnotes", f.relnotes)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_release_sdrl(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with --source, --doc, --relnotes, and --changelog.
    """
    f = files_release
    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--doc",
        f.docball,
        "--relnotes",
        f.relnotes,
        "--changelog",
        f.changelog,
    )
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_release_sdrlc(in_tmp_dir, cmd, makesrpm, files_release):
    """
    Test creating a release SRPM with all named arguments.
    """
    f = files_release
    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--doc",
        f.docball,
        "--relnotes",
        f.relnotes,
        "--changelog",
        f.changelog,
        "--cellservdb",
        f.cellservdb,
    )
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert not cmd.re_in_stderr("Connecting to www.central.org .*")
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_sd(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with --source and --doc.
    """
    f = files_prerelease
    result = cmd.run(makesrpm, "--source", f.srcball, "--doc", f.docball)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_sdr(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with --source, --doc, and --relnotes.
    """
    f = files_prerelease
    result = cmd.run(makesrpm, "--source", f.srcball, "--doc", f.docball, "--relnotes", f.relnotes)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_sdrl(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with --source, --doc, --relnotes, and --changelog.
    """
    f = files_prerelease
    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--doc",
        f.docball,
        "--relnotes",
        f.relnotes,
        "--changelog",
        f.changelog,
    )
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_prerelease_sdrlc(in_tmp_dir, cmd, makesrpm, files_prerelease):
    """
    Test creating a pre-release SRPM with all named arguments.
    """
    f = files_prerelease
    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--doc",
        f.docball,
        "--relnotes",
        f.relnotes,
        "--changelog",
        f.changelog,
        "--cellservdb",
        f.cellservdb,
    )
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert not cmd.re_in_stderr("Connecting to www.central.org .*")
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_s(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with --source.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_sr(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with --source and --relnotes.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--relnotes", f.relnotes)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_srl(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with --source, --relnotes, and --changelog.
    """
    f = files_devel
    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--relnotes",
        f.relnotes,
        "--changelog",
        f.changelog,
    )
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert cmd.re_in_stderr("Connecting to www.central.org .*"), cmd.msg
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_srlc(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with all named arguments.
    """
    f = files_devel
    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--relnotes",
        f.relnotes,
        "--changelog",
        f.changelog,
        "--cellservdb",
        f.cellservdb,
    )
    assert result.returncode == 0
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert not cmd.re_in_stderr("Connecting to www.central.org .*")
    assert Path(f"{f.nvr}.src.rpm").is_file()


def test_devel_sc(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test creating a development SRPM with --source and --cellservdb.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--cellservdb", f.cellservdb)
    assert result.returncode == 0
    assert cmd.in_stdout("WARNING: No release notes provided. Using empty file"), cmd.msg
    assert cmd.in_stdout("WARNING: No changelog provided. Using empty file"), cmd.msg
    assert cmd.in_stdout(f"SRPM is {in_tmp_dir}/{f.nvr}.src.rpm"), cmd.msg
    assert not cmd.re_in_stderr("Connecting to www.central.org .*")
    assert Path(f"{f.nvr}.src.rpm").is_file()
