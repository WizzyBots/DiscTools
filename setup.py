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
    author="WizzyGeek",
    author_email="ojasscoding@gmail.com",
    description="discord.py helper classes, functions & alternatives",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/WizzyGeek/DiscTools",
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
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    python_requires='>=3.8',
    extras_require={
        "docs": [
            "Sphinx~=4.0.1",
            "sphinx-rtd-theme~=0.5"
            "sphinxcontrib-trio"
        ]
    }
)