def test_mix_named_doc_and_pos_source(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that mixing named and positional arguments is allowed when there is no ambiguity.
    """
    result = cmd.run(makesrpm, "--doc", files_devel.docball, files_devel.srcball)
    assert result.returncode == 0


def test_ambiguous_source(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test for error when both --source and a positional source are given.
    """
    result = cmd.run(makesrpm, "--source", files_devel.srcball, files_devel.srcball)
    assert result.returncode != 0
    assert cmd.in_stdout("--source and positional argument 1 are exclusive")


def test_ambiguous_doc(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test for error when both --doc and a positional doc are given.
    """
    result = cmd.run(makesrpm, files_devel.srcball, "--doc", files_devel.docball, files_devel.docball)
    assert result.returncode != 0
    assert cmd.in_stdout("--doc and positional argument 2 are exclusive")


def test_ambiguous_relnotes(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test for error when both --relnotes and a positional relnotes are given.
    """
    result = cmd.run(
        makesrpm,
        "--relnotes", files_devel.relnotes,
        files_devel.srcball,
        files_devel.docball,
        files_devel.relnotes,
    )
    assert result.returncode != 0
    assert cmd.in_stdout("--relnotes and positional argument 3 are exclusive")


def test_ambiguous_changelog(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test for error when both --changelog and a positional changelog are given.
    """
    result = cmd.run(
        makesrpm,
        "--changelog", files_devel.changelog,
        files_devel.srcball,
        files_devel.docball,
        files_devel.relnotes,
        files_devel.changelog,
    )
    assert result.returncode != 0
    assert cmd.in_stdout("--changelog and positional argument 4 are exclusive")


def test_ambiguous_cellservdb(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test for error when both --cellservdb and a positional cellservdb are given.
    """
    result = cmd.run(
        makesrpm,
        "--cellservdb", files_devel.cellservdb,
        files_devel.srcball,
        files_devel.docball,
        files_devel.relnotes,
        files_devel.changelog,
        files_devel.cellservdb,
    )
    assert result.returncode != 0
    assert cmd.in_stdout("--cellservdb and positional argument 5 are exclusive")
