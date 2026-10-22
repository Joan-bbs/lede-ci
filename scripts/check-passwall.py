#!/usr/bin/env python3
"""Fail closed on wrong feed revisions, package selection or firmware versions."""
import argparse
import os
from pathlib import Path
import re
import subprocess


LOCKS = {
    "passwall": ("26.1.13-1", "1f589523b33bd312b9cf38394c72493e0fde64ea"),
    "passwall2": ("25.11.18-1", "dbf48fb5bd9f6e68824800cf418265b42c943c7d"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def package_versions(version):
    # Newer luci.mk spells the same release as -r1 instead of -1.
    upstream, release = version.rsplit("-", 1)
    return (version, f"{upstream}-r{release}")


def source(root):
    for feed, (version, revision) in LOCKS.items():
        package = f"luci-app-{feed}"
        checkout = root / "feeds" / feed
        actual = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
        ).strip()
        require(actual == revision, f"{feed}: commit {actual} != {revision}")
        expected = checkout / package / "Makefile"
        text = expected.read_text()
        values = dict(re.findall(r"^(PKG_VERSION|PKG_RELEASE)\s*:=\s*(\S+)\s*$", text, re.M))
        actual_version = f"{values.get('PKG_VERSION')}-{values.get('PKG_RELEASE')}"
        require(actual_version == version, f"{package}: source version {actual_version} != {version}")
        # Scan the build-visible tree, including feed symlinks. Do not scan all
        # feeds directly: uninstalled copies there are harmless.
        candidates = []
        for directory, _, files in os.walk(root / "package", followlinks=True):
            if "Makefile" not in files:
                continue
            makefile = Path(directory) / "Makefile"
            if (Path(directory).name == package or re.search(
                rf"^PKG_NAME\s*:=\s*{re.escape(package)}\s*$", makefile.read_text(), re.M
            )):
                candidates.append(makefile)
        require(len(candidates) == 1, f"{package}: expected one installed source, found {candidates}")
        require(candidates[0].resolve() == expected.resolve(),
                f"{package}: wrong feed selected: {candidates[0].resolve()}")
        print(f"{package}: {version}; commit {revision}; source {candidates[0].relative_to(root)}")


def config(root):
    lines = (root / ".config").read_text().splitlines()
    for feed in LOCKS:
        package = f"luci-app-{feed}"
        require(f"CONFIG_PACKAGE_{package}=y" in lines,
                f"{package}: must be built into firmware (=y), not disabled or =m")
        print(f"{package}: selected in firmware")


def artifacts(root):
    manifests = sorted((root / "bin" / "targets").glob("*/*/*.manifest"))
    require(manifests, "No firmware manifest found; cannot verify installed versions")
    for manifest in manifests:
        packages = dict(re.findall(r"^(\S+) - (\S+)\s*$", manifest.read_text(), re.M))
        for feed, (version, _) in LOCKS.items():
            package = f"luci-app-{feed}"
            require(packages.get(package) in package_versions(version),
                    f"{manifest.name}: {package} = {packages.get(package)!r}, expected {version}")
            print(f"{manifest.name}: {package} {packages[package]} verified (upstream {version})")
    for feed, (version, _) in LOCKS.items():
        package = f"luci-app-{feed}"
        ipks = sorted((root / "bin" / "packages").glob(f"*/*/{package}_*.ipk"))
        require(ipks, f"No {package} IPK found")
        require(all(any(ipk.name.startswith(f"{package}_{v}_") for v in package_versions(version))
                    for ipk in ipks),
                f"Unexpected {package} IPK versions: {ipks}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("source", "config", "artifacts"))
    parser.add_argument("root", type=Path, help="OpenWrt build root")
    args = parser.parse_args()
    try:
        globals()[args.phase](args.root.resolve())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"PassWall version check failed: {exc}\n")


if __name__ == "__main__":
    main()
