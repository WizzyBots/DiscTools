from typing import Dict, Literal, Optional, Protocol, Union
from string import ascii_letters, digits

valid_identifier_chars = ascii_letters + digits + "."

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
    day = 26
    month = 5
    year = 2021

    @classmethod
    def date(cls) -> str:
        """Returns date based version of format yyyy.[m]m.[d]d"""
        return f"{cls.year}.{cls.month}.{cls.day}"


# Major.minor.patch status serial .postN .devM + build
class VersionInfo:
    """Information regarding a version."""
    major: int
    minor: int
    patch: int
    status: Status
    serial: int
    post: Optional[int]
    dev: Optional[int]
    build: Optional[Stringable]

    def __init__(self, *, major: int,
                 minor: int,
                 patch: int,
                 status: Optional[Status],
                 serial: int = 0,
                 post: Optional[int] = None,
                 dev: Optional[int] = None,
                 build: Optional[Stringable] = None) -> None:
        ver = str(major)

        if status:
            if status not in status_map.values():
                raise ValueError(f"status can only be one of ('a', 'b', 'rc', 'f')")
        else:
            status = "f"

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

        if not post is None:
            ver += f".post{post}"

        if not dev is None:
            ver += f".dev{dev}"

        if build:
            build_s = str(build)
            for i in build_s:
                if i not in valid_identifier_chars:
                    raise ValueError(
                        f"build (Local Identifier) contains invalid character {i} at index {build_s.index(i)}")
            ver += f"+{build}"

        self._ver = ver.strip()
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
    patch = 4,
    status = status_map["final"]
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