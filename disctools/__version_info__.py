from typing import Dict, Literal, Optional, Protocol, Union

class HasStr(Protocol):
    def __str__(self) -> str:
        ...

class HasRepr(Protocol):
    def __repr__(self) -> str:
        ...

Stringable = Union[HasRepr, HasStr]
Status = Literal["a", "b", "rc", "f"]

status_map: Dict[str, Status] = {
    "alpha": "a",
    "beta": "b",
    "release_candidate": "rc",
    "rc": "rc",
    "final": "f"
}

class last_modified:
    day = 17
    month = 5
    year = 2021

    @classmethod
    def date(cls) -> str:
        return f"{cls.year}.{cls.month}.{cls.day}"


# Major.minor.patch status serial .postN .devM + build
class VersionInfo:
    """Information regarding a version."""
    major: int
    minor: int
    patch: int
    status: Status
    serial: int
    post: int
    dev: int
    build: Optional[Stringable]

    def __init__(self, *, major: int,
                 minor: int,
                 patch: int,
                 status: Status,
                 serial: int = 0,
                 post: int = 0,
                 dev: int = 0,
                 build: Optional[Stringable] = None) -> None:
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
        elif serial != 0:
            raise ValueError("Final release cannot have a serial number!, use post instead.")

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
    minor = 5,
    patch = 2,
    status = status_map["final"],
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