import pytest
import os

# fmt: off
version_data = [
    # version                             afsvers                pkgvers        pkgrel
    # -----------------------------       ------------------     -----------    ------------
    ("openafs-stable-1_8_15",             "1.8.15",              "1.8.15",      "1"),
    ("openafs-stable-1_8_16pre1",         "1.8.16pre1",          "1.8.16",      "0.pre1"),
    ("openafs-devel-1_7_2",               "1.7.2",               "1.7.2",       "1"),
    #   should be?                        "1.7.2",               "1.7.2dev",    "0.dev"),
    ("openafs-devel-1_7_24a",             "1.7.24a",             "1.7.24a",     "1"),
    ("openafs-devel-1_9_2-472-gd5103",    "1.9.2-472-gd5103",    "1.9.2",       "1.472.gd5103"),
    #   should be?                        "1.9.2-472-gd5103",    "1.9.2dev",    "0.dev.472.gd5103"),
    ("openafs-devel-1_9_2dev-472-gd5103", "1.9.2dev-472-gd5103", "1.9.2",       "0.dev.472.gd5103"),
    ("v1.8.14-ab1",                       "v1.8.14-ab1",         "v1.8.14_ab1", "1"),
    #   should be?                        "v1.8.14-ab1",         "1.8.14_ab1",  "1"),
]
# fmt: on


@pytest.mark.parametrize(
    "version,afsvers,pkgvers,pkgrel", version_data, ids=[row[0] for row in version_data]
)
def test_version_parsing(in_tmp_dir, src_tarball, cmd, makesrpm, version, afsvers, pkgvers, pkgrel):
    """
    Test version string parsing.
    """
    src_tarball.version = version
    tarball = src_tarball.build()
    cooked_spec = in_tmp_dir / "openafs.spec.cooked"

    cmd.env["RPMBUILD_COPY_SPEC"] = cooked_spec
    cmd.env["RPMBUILD_SIMULATE"] = "1"
    cmd.run(makesrpm, "--source", tarball)
    assert cmd.in_stdout(f"Building version {afsvers}"), cmd.msg
    assert cmd.in_stdout(f"Package version is {pkgvers}"), cmd.msg
    assert cmd.in_stdout(f"Package release is {pkgrel}"), cmd.msg

    assert cooked_spec.is_file()
    spec = cooked_spec.read_text()
    assert f"%define afsvers {afsvers}" in spec
    assert f"%define pkgvers {pkgvers}" in spec
    assert f"%define pkgrel {pkgrel}" in spec
