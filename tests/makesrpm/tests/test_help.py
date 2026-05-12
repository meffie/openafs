import re


def test_short_help(cmd, makesrpm):
    """
    Test that the --help option displays the short help message.
    """
    result = cmd.run(makesrpm, "--help")
    assert result.returncode == 0
    assert cmd.in_stdout("Usage:"), cmd.msg


def test_short_help_alias(cmd, makesrpm):
    """
    Test that the -? alias for --help displays the short help message.
    """
    result = cmd.run(makesrpm, "-?")
    assert result.returncode == 0
    assert cmd.in_stdout("Usage:"), cmd.msg


def test_long_help(cmd, makesrpm):
    """
    Test that the --man option displays the long help message (man page).
    """
    result = cmd.run(makesrpm, "--man")
    assert result.returncode == 0
    assert cmd.in_stdout("SYNOPSIS"), cmd.msg
    assert cmd.in_stdout("DESCRIPTION"), cmd.msg
    assert cmd.in_stdout("OPTIONS"), cmd.msg
