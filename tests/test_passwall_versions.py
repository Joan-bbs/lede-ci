"""Regression checks for source shadowing and publishing incorrect firmware."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "checker", Path(__file__).resolve().parents[1] / "scripts/check-passwall.py"
)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class VersionChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for feed, (version, _) in checker.LOCKS.items():
            package = f"luci-app-{feed}"
            target = self.root / "feeds" / feed / package
            target.mkdir(parents=True)
            ver, release = version.rsplit("-", 1)
            (target / "Makefile").write_text(
                f"PKG_NAME:={package}\nPKG_VERSION:={ver}\nPKG_RELEASE:={release}\n"
            )
            link = self.root / "package" / "feeds" / feed / package
            link.parent.mkdir(parents=True)
            link.symlink_to(target, target_is_directory=True)
        self.git = patch.object(checker.subprocess, "check_output", side_effect=lambda cmd, **kw:
                                checker.LOCKS[Path(cmd[2]).name][1] + "\n")
        self.git.start()
        self.addCleanup(self.git.stop)

    def manifest(self):
        path = self.root / "bin/targets/x86/64/test.manifest"
        path.parent.mkdir(parents=True)
        path.write_text("".join(f"luci-app-{feed} - {version}\n"
                                for feed, (version, _) in checker.LOCKS.items()))
        for feed, (version, _) in checker.LOCKS.items():
            ipk = self.root / f"bin/packages/x86_64/{feed}/luci-app-{feed}_{version}_all.ipk"
            ipk.parent.mkdir(parents=True)
            ipk.touch()
        return path

    def test_pinned_source_selected(self):
        checker.source(self.root)

    def test_luci_source_shadowing_rejected(self):
        link = self.root / "package/feeds/passwall/luci-app-passwall"
        link.unlink()
        wrong = self.root / "feeds/luci/applications/luci-app-passwall"
        wrong.mkdir(parents=True)
        (wrong / "Makefile").write_text("PKG_NAME:=luci-app-passwall\n")
        link.symlink_to(wrong, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "wrong feed selected"):
            checker.source(self.root)

    def test_duplicate_source_rejected(self):
        duplicate = self.root / "package/other/luci-app-passwall"
        duplicate.mkdir(parents=True)
        (duplicate / "Makefile").write_text("PKG_NAME:=luci-app-passwall\n")
        with self.assertRaisesRegex(ValueError, "expected one installed source"):
            checker.source(self.root)

    def test_changed_revision_rejected(self):
        with patch.object(checker.subprocess, "check_output", return_value="bad-revision\n"):
            with self.assertRaisesRegex(ValueError, "commit"):
                checker.source(self.root)

    def test_changed_source_version_rejected(self):
        (self.root / "feeds/passwall/luci-app-passwall/Makefile").write_text(
            "PKG_VERSION:=99.1.1\nPKG_RELEASE:=1\n")
        with self.assertRaisesRegex(ValueError, "source version"):
            checker.source(self.root)

    def test_module_only_config_rejected(self):
        (self.root / ".config").write_text(
            "CONFIG_PACKAGE_luci-app-passwall=m\nCONFIG_PACKAGE_luci-app-passwall2=y\n")
        with self.assertRaisesRegex(ValueError, "must be built into firmware"):
            checker.config(self.root)

    def test_firmware_config_selected(self):
        (self.root / ".config").write_text(
            "CONFIG_PACKAGE_luci-app-passwall=y\nCONFIG_PACKAGE_luci-app-passwall2=y\n")
        checker.config(self.root)

    def test_verified_artifacts(self):
        self.manifest()
        checker.artifacts(self.root)

    def test_wrong_firmware_version_rejected(self):
        manifest = self.manifest()
        manifest.write_text(manifest.read_text().replace("26.1.13-1", "26.10.22-1"))
        with self.assertRaisesRegex(ValueError, "expected 26.1.13-1"):
            checker.artifacts(self.root)

    def test_luci_release_prefix_accepted(self):
        manifest = self.manifest()
        manifest.write_text(manifest.read_text().replace("-1", "-r1"))
        for ipk in (self.root / "bin/packages").glob("*/*/*.ipk"):
            ipk.rename(ipk.with_name(ipk.name.replace("-1_", "-r1_")))
        checker.artifacts(self.root)

    def test_wrong_cached_ipk_rejected(self):
        self.manifest()
        (self.root / "bin/packages/x86_64/passwall/luci-app-passwall_99.1.1-1_all.ipk").touch()
        with self.assertRaisesRegex(ValueError, "Unexpected.*IPK versions"):
            checker.artifacts(self.root)

    def test_missing_manifest_rejected(self):
        with self.assertRaisesRegex(ValueError, "No firmware manifest"):
            checker.artifacts(self.root)


if __name__ == "__main__":
    unittest.main()
