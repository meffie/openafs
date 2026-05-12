
def test_unknown_option(cmd, makesrpm):
    """
    Test that an unknown command line option causes an error.
    """
    result = cmd.run(makesrpm, "--unknown-option")
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"Unknown option: unknown-option")


def test_option_with_missing_value(cmd, makesrpm):
    """
    Test that an option requiring a value causes an error if none is provided.
    """
    result = cmd.run(makesrpm, "--source")
    assert result.returncode != 0
    assert cmd.re_in_stderr(r"Option source requires an argument")
