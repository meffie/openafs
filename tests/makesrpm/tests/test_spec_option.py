import pytest
import re
from pathlib import Path


def test_spec_option(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that the --spec option correctly uses the specified spec file.
    """
    f = files_devel
    rpm_build_dir = in_tmp_dir / "rpmbuild"
    custom_spec_path = in_tmp_dir / "custom.spec"
    spec_content = """
# This is a custom spec file.
%define pkgvers 0
%define pkgrel 0
Source20: http://example.com/CellServDB
"""
    custom_spec_path.write_text(spec_content)

    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--spec",
        custom_spec_path,
        "--prepare-only",
        "--rpm-build-dir",
        rpm_build_dir,
    )

    assert result.returncode == 0
    output_spec_path = rpm_build_dir / "SPECS" / "openafs.spec"
    assert output_spec_path.is_file()
    output_spec_content = output_spec_path.read_text()
    assert "# This is a custom spec file." in output_spec_content
    assert f"%define pkgvers {f.package_version}" in output_spec_content
    assert f"%define pkgrel {f.package_release}" in output_spec_content


def test_spec_not_found(cmd, makesrpm, files_devel):
    """
    Test that makesrpm.pl dies if the spec file does not exist.
    """
    f = files_devel
    result = cmd.run(makesrpm, "--source", f.srcball, "--spec", "nonexistent.spec")
    assert result.returncode != 0
    assert cmd.in_stderr("Unable to open nonexistent.spec: No such file or directory")


def test_spec_overrides_packaging(in_tmp_dir, cmd, makesrpm, files_devel):
    """
    Test that --spec takes precedence over the spec file in the packaging dir.
    """
    f = files_devel
    rpm_build_dir = in_tmp_dir / "rpmbuild"

    # Create a dummy packaging directory with a spec file and another file
    packaging_dir = in_tmp_dir / "custom_packaging"
    packaging_dir.mkdir()
    packaging_spec_path = packaging_dir / "openafs.spec.in"
    packaging_spec_path.write_text(
        """
# This is the spec from the packaging dir.
Source20: http://packaging.example.com/CellServDB
"""
    )
    dummy_packaging_file = packaging_dir / "dummy.file"
    dummy_packaging_file.write_text("dummy content")

    # Create a separate spec file to be used with --spec
    override_spec_path = in_tmp_dir / "override.spec"
    override_spec_path.write_text(
        """
# This is the override spec file.
Source20: http://override.example.com/CellServDB
"""
    )

    result = cmd.run(
        makesrpm,
        "--source",
        f.srcball,
        "--packaging",
        packaging_dir,
        "--spec",
        override_spec_path,
        "--prepare-only",
        "--rpm-build-dir",
        rpm_build_dir,
    )

    assert result.returncode == 0
    output_spec_path = rpm_build_dir / "SPECS" / "openafs.spec"
    assert output_spec_path.is_file()
    output_spec_content = output_spec_path.read_text()
    assert "# This is the override spec file." in output_spec_content
    assert "Source20: http://override.example.com/CellServDB" in output_spec_content
    assert "# This is the spec from the packaging dir." not in output_spec_content

    # Check that other files from the packaging dir are copied to SOURCES
    assert (rpm_build_dir / "SOURCES" / "dummy.file").is_file()

    output_spec_path = rpm_build_dir / "SPECS" / "openafs.spec"
    assert output_spec_path.is_file()
    output_spec_content = output_spec_path.read_text()
    assert "# This is the override spec file." in output_spec_content
    assert "# This is the spec from the packaging dir." not in output_spec_content

    # Check that other files from the packaging dir are copied to SOURCES
    assert (rpm_build_dir / "SOURCES" / "dummy.file").is_file()
