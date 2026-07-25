from pathlib import Path


def test_build_archive(in_git_root, tmp_path, cmd, makesrpm):
    result = cmd.run(makesrpm, "--output-dir", tmp_path, "--ignore-dirty")
    assert result.returncode == 0
    assert cmd.re_in_stdout(r"SRPM is .*.src.rpm"), cmd.msg
    assert len(list(tmp_path.glob("openafs-*.src.rpm"))) == 1


def test_prepare_only(in_git_root, tmp_path, cmd, makesrpm):
    """
    When --prepare-only is specified, makesrpm should populate the rpm build
    directories but not build the SRPM.
    """
    rpm_build_dir = tmp_path / "rpmbuild"
    result = cmd.run(makesrpm, "--prepare-only", "--rpm-build-dir", rpm_build_dir, "--ignore-dirty")
    assert result.returncode == 0
    assert cmd.in_stdout("SRPM build skipped (--prepare-only specified)")
    assert (rpm_build_dir / "SPECS" / "openafs.spec").is_file()
    assert (rpm_build_dir / "SOURCES").is_dir()
    # Check for source tarball
    assert len(list((rpm_build_dir / "SOURCES").glob("openafs-*-src.tar.bz2"))) == 1
    # Check that no SRPM is created
    assert len(list(tmp_path.glob("*.src.rpm"))) == 0
    assert len(list((rpm_build_dir / "SRPMS").glob("*.src.rpm"))) == 0


def test_prepare_only_omit_source(in_git_root, tmp_path, cmd, makesrpm):
    """
    When --prepare-only and --omit-source are specified, makesrpm should
    populate the rpm build directories but not create a source archive.
    """
    rpm_build_dir = tmp_path / "rpmbuild"
    result = cmd.run(makesrpm, "--prepare-only", "--rpm-build-dir", rpm_build_dir,
                     "--omit-source", "--ignore-dirty")
    assert result.returncode == 0
    assert cmd.in_stdout("Skipping source archive creation (--omit-source specified)")
    assert (rpm_build_dir / "SPECS" / "openafs.spec").is_file()
    assert (rpm_build_dir / "SOURCES").is_dir()
    # Check that no source tarball is created
    assert len(list((rpm_build_dir / "SOURCES").glob("openafs-*-src.tar.bz2"))) == 0
    # Check that no SRPM is created
    assert len(list(tmp_path.glob("*.src.rpm"))) == 0
    assert len(list((rpm_build_dir / "SRPMS").glob("*.src.rpm"))) == 0



def test_override_package_version(in_git_root, tmp_path, cmd, makesrpm):
    """
    When --package-version and --package-release are specified, makesrpm should
    use them in the spec file.
    """
    rpm_build_dir = tmp_path / "rpmbuild"
    pkg_version = "4.5.6"
    pkg_release = "1.my.dist"
    result = cmd.run(makesrpm, "--prepare-only", "--rpm-build-dir", rpm_build_dir,
                     "--package-version", pkg_version,
                     "--package-release", pkg_release,
                     "--omit-source",
                     "--ignore-dirty")
    assert result.returncode == 0
    spec_path = rpm_build_dir / "SPECS" / "openafs.spec"
    assert spec_path.is_file()
    spec_content = spec_path.read_text()
    assert f"%define pkgvers {pkg_version}" in spec_content
    assert f"%define pkgrel {pkg_release}" in spec_content

