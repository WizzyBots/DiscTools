from setuptools import setup

with open("README.md", "r") as ReadHead:
    long_description = ReadHead.read()

requirements = []
with open("requirements.txt") as ReadHead:
  requirements = ReadHead.read().splitlines()

with open("version.num") as ReadHead:
    version = ReadHead.read()

setup(
    name="DiscTools",
    version=version,
    author="teen_boom",
    author_email="ojasscoding@gmail.com",
    description="discord.py helper classes, functions & alternatives",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/TEEN-BOOM/DiscTools",
    license='MIT',
    test_suite="tests",
    packages=[
        "disctools",
        "disctools.experimental"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    python_requires='>=3.6',
    extras_require={
        "docs": [
            "Sphinx~=3.1.2",
            "sphinx-rtd-theme~=0.5.0"
        ]
    },
    package_dir={"": "."}
)