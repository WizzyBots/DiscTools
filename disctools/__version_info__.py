status_map = {
    "alpha": "a",
    "beta": "b",
    "release_candidate": "rc",
    "final": "f"
}

class last_modified:
    day = 26
    month = 8
    year = 2020

    @classmethod
    def date(cls):
        return f"{year}.{month}.{day}"

class VersionInfo:# Major.minor.patch status serial + build
    """Information regarding a version."""
    def __init__(self, *, major, minor, patch, status, serial = 0, build = None):
        ver = f"{major}.{minor}.{patch}{status}{serial}"

        if build:
            ver += f"+{build}"

        self._semver = ver
        self.major = major
        self.minor = minor
        self.patch = patch
        self.status = status
        self.serial = serial
        self.build = build
        self.__cached_repr = f"<VersionInfo of '{self._semver}'>"
    
    def __str__(self) -> str:
        return self._semver

    def __repr__(self) -> str:
        return self.__cached_repr

version_info = VersionInfo(
    major = 0,
    minor = 2,
    patch = 0,
    status = status_map["final"],
    serial = 0
)

__version__ = str(version_info)

def main() -> None:
    import platform
    print(
        f"""
DiscTools
=========
Version: {__version__}

Python Info
===========
Version: {platform.python_version()}
Implementation: {platform.python_implementation()}

Hardware Info
=============
System: {platform.system()}
Machine: {platform.machine()}
Release: {platform.release()}
        """
    )

if __name__ == "__main__":
    import pathlib
    (pathlib.Path(__file__).parents[1] / "version.num").write_text(__version__)
    main()
