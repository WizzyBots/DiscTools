status_map = {
    "alpha": "a",
    "beta": "b",
    "release_candidate": "rc",
    "final": "f"
}

class last_modified:
    day = 11
    month = 5
    year = 2021

    @classmethod
    def date(cls):
        return f"{cls.year}.{cls.month}.{cls.day}"


# Major.minor.patch status serial .postN .devM + build
class VersionInfo:
    """Information regarding a version."""
    def __init__(self, *, major, minor, patch, status, serial = 0, post = 0, dev = 0, build = None):
        ver = str(major)
        if minor:
            ver += f".{minor}"

        if patch:
            if not minor:
                ver += f".0.{patch}"
            else:
                ver += f".{patch}"

        if status != "f":
            ver += f"{status}{serial}"

        if post:
            ver += f".post{post}"

        if dev:
            ver += f".dev{dev}"

        if build:
            ver += f"+{build}"

        self._ver = ver
        self.major = major
        self.minor = minor
        self.patch = patch
        self.status = status
        self.serial = serial
        self.post = post
        self.dev = dev
        self.build = build
        self.__cached_repr = f"<VersionInfo of '{self._ver}'>"

    def __str__(self) -> str:
        return self._ver

    def __repr__(self) -> str:
        return self.__cached_repr

version_info = VersionInfo(
    major = 0,
    minor = 4,
    patch = 1,
    status = status_map["alpha"],
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

Platform Info
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