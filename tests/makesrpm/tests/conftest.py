import os
import re
import shutil
import subprocess
import sys
import threading
import tarfile

from pathlib import Path

import pytest


@pytest.fixture
def in_tmp_dir(tmp_path):
    """
    Run test in a temporary directory.
    """
    old_dir = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_dir)


@pytest.fixture
def in_git_root(git_root):
    """
    Run test in a the git root directory.
    """
    old_dir = Path.cwd()
    os.chdir(git_root)
    yield git_root
    os.chdir(old_dir)


@pytest.fixture
def test_root():
    """Returns the absolute path to test root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def data_root(test_root):
    """Returns the absolute path to the data directory."""
    xdg_data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    data_root = (xdg_data_home / "openafs/tests/makesrpm").resolve()
    assert data_root.is_dir(), f"Data root {data_root} is missing; Try bin/setup.sh to create it."
    return data_root


@pytest.fixture
def git_root(test_root):
    """Returns the absolute path to git top-level directory."""
    return test_root.parent.parent


@pytest.fixture
def makesrpm(git_root):
    """Returns the abolute path to the makesrpm script."""
    packaging = Path("src/packaging/RedHat")
    return git_root / packaging / "makesrpm.pl"


@pytest.fixture
def files_release(data_root):
    """
    Provides a TestData object with paths to release-specific files.
    """
    tarballs = data_root / "1.8.15"

    class TestData:
        srcball = tarballs / "openafs-1.8.15-src.tar.bz2"
        docball = tarballs / "openafs-1.8.15-doc.tar.bz2"
        relnotes = tarballs / "RELNOTES-1.8.15"
        changelog = tarballs / "ChangeLog"
        cellservdb = tarballs / "CellServDB.2025-08-16"
        package_name = "openafs"
        package_version = "1.8.15"
        package_release = "1"
        nvr = f"{package_name}-{package_version}-{package_release}"

    return TestData()


@pytest.fixture
def files_prerelease(data_root):
    """
    Provides a TestData object with paths to pre-release-specific files.
    """
    tarballs = data_root / "1.8.16pre1"

    class TestData:
        srcball = tarballs / "openafs-1.8.16pre1-src.tar.bz2"
        docball = tarballs / "openafs-1.8.16pre1-doc.tar.bz2"
        relnotes = tarballs / "RELNOTES-1.8.16pre1"
        changelog = tarballs / "ChangeLog"
        cellservdb = tarballs / "CellServDB.2025-08-16"
        package_name = "openafs"
        package_version = "1.8.16"
        package_release = "0.pre1"
        nvr = f"{package_name}-{package_version}-{package_release}"

    return TestData()


@pytest.fixture
def files_devel(data_root):
    """
    Provides a TestData object with paths to development-specific files.
    """
    tarballs = data_root / "master"

    class TestData:
        version = "1.9.2-472-gd5103"  # Depends on commit sha1 used in setup.sh.
        srcball = tarballs / f"openafs-{version}-src.tar.bz2"
        docball = tarballs / f"openafs-{version}-doc.tar.bz2"
        relnotes = tarballs / "NEWS"
        changelog = tarballs / "ChangeLog"
        cellservdb = tarballs / "CellServDB.2025-08-16"
        package_name = "openafs"
        package_version = "1.9.2"
        package_release = "1.472.gd5103"
        nvr = f"{package_name}-{package_version}-{package_release}"

    return TestData()


class SourceTarball:
    """
    Generate fake source tarballs for testing error cases.
    """

    def __init__(self, git_root, tmp_path):
        self.git_root = git_root
        self.tmp_path = tmp_path
        self.name = "fake"
        self.version = "openafs-stable-1_2_3"
        self.spec = None
        self.include_version = True
        self.include_tools = True
        self.include_packaging = True

    def _prep_dot_version(self):
        (self.src_dir / "configure.ac").write_text("dummy")
        (self.src_dir / ".version").write_text(self.version)

    def _prep_build_tools(self):
        build_tools = self.src_dir / "build-tools"
        build_tools.mkdir()
        git_version_src = self.git_root / "build-tools/git-version"
        git_version_dest = build_tools / "git-version"
        shutil.copy(git_version_src, git_version_dest)
        git_version_dest.chmod(0o755)

    def _prep_packaging_old_style(self):
        packaging_dir = self.src_dir / "src/packaging/RedHat"
        packaging_dir.mkdir(parents=True)
        if self.spec is None:
            spec_src = self.git_root / "src/packaging/RedHat/openafs.spec.in"
        else:
            spec_src = self.spec
        spec_dest = packaging_dir / "openafs.spec.in"
        shutil.copy(spec_src, spec_dest)

    def _prep_packaging_new_style(self):
        packaging_dir = self.src_dir / "src/packaging/RedHat"
        (packaging_dir / "SPECS").mkdir(parents=True)
        (packaging_dir / "SOURCES").mkdir(parents=True)
        if self.spec is None:
            spec_src = self.git_root / "src/packaging/RedHat/SPECS/openafs.spec"
        else:
            spec_src = self.spec
        spec_dest = packaging_dir / "SPECS/openafs.spec"
        shutil.copy(spec_src, spec_dest)

    def build(self):
        self.src_dir = self.tmp_path / f"openafs-{self.version}"
        self.src_dir.mkdir()
        if self.include_version:
            self._prep_dot_version()
        if self.include_tools:
            self._prep_build_tools()
        if self.include_packaging:
            if (self.git_root / "src/packaging/RedHat/SPECS").exists():
                self._prep_packaging_new_style()
            else:
                self._prep_packaging_old_style()
        tarball = self.tmp_path / f"{self.name}.tar.bz2"
        with tarfile.open(tarball, "w:bz2") as tar:
            tar.add(self.src_dir, arcname=f"openafs-{self.version}")
        return tarball


@pytest.fixture
def src_tarball(git_root, tmp_path):
    return SourceTarball(git_root, tmp_path)


class Command:
    """
    A helper class for running external commands and capturing their output.
    """

    def __init__(self):
        self.msg = ""
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.captured_stdout = []
        self.captured_stderr = []
        self.env = {}

    def run(self, *args):
        """
        Executes a command and captures its stdout and stderr.
        """
        path = os.environ["PATH"]
        mock = Path(__file__).parent.parent / "mock"
        env = os.environ.copy()
        env.update(self.env)
        env["PATH"] = f"{mock}:{path}"

        cmd_str = " ".join(str(c) for c in list(args))
        print(f"RUNNING: {cmd_str}")
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout_thread = threading.Thread(
            target=self._read_stream, args=(p.stdout, self.captured_stdout, self.stdout)
        )
        stderr_thread = threading.Thread(
            target=self._read_stream, args=(p.stderr, self.captured_stderr, self.stderr)
        )
        stdout_thread.start()
        stderr_thread.start()
        stdout_thread.join()
        stderr_thread.join()
        p.wait()
        return p

    def _read_stream(self, source_stream, captured, output_stream):
        """
        Reads from a stream, capturing the output and printing it.
        """
        for line in iter(source_stream.readline, b""):
            decoded_line = line.decode("utf-8")
            output_stream.write(decoded_line)
            captured.append(decoded_line.rstrip("\n"))
        source_stream.close()

    def in_stdout(self, pattern):
        """
        Checks if a pattern exists in the captured stdout.
        """
        for line in self.captured_stdout:
            if pattern in line:
                return True
        self.msg = f"'{pattern}' not found in stdout."
        return False

    def in_stderr(self, pattern):
        """
        Checks if a pattern exists in the captured stderr.
        """
        for line in self.captured_stderr:
            if pattern in line:
                return True
        self.msg = f"'{pattern}' not found in stderr."
        return False

    def re_in_stdout(self, pattern):
        """
        Checks if a regex pattern matches any line in the captured stdout.
        """
        for line in self.captured_stdout:
            if re.search(pattern, line):
                return True
        self.msg = f"'{pattern}' not found in stdout."
        return False

    def re_in_stderr(self, pattern):
        """
        Checks if a regex pattern matches any line in the captured stderr.
        """
        for line in self.captured_stderr:
            if re.search(pattern, line):
                return True
        self.msg = f"'{pattern}' not found in stderr."
        return False


@pytest.fixture
def cmd():
    """
    Provides a Command object for running external commands.
    """
    return Command()
