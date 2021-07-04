from setuptools import find_namespace_packages, setup

setup(
    name="raygen",
    version="1.0",
    packages=find_namespace_packages(),
    install_requires=["dataclasses-json"],
    entry_points={
        "console_scripts": [
            "raygen = raygen.cli:main",
        ]
    },
)
