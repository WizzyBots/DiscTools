from setuptools import setup
import disctools

with open("README.md", "r") as ReadHead:
    long_description = ReadHead.read()

setup(
    name="DiscTools",
    version="0.1.0",
    author="teen_boom",
    author_email="ojasscoding@gmail.com",
    description="discord.py helper classes, functions & alternatives",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    license='MIT',
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
    extra_requires={
        "docs": [
            "Sphinx~=3.1.2",
            "sphinx-rtd-theme~=0.5.0"
        ]
    }
)