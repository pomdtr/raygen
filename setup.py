from setuptools import setup, find_namespace_packages


setup(
    name="raygen",
    version="1.0",
    packages=find_namespace_packages(),
    entry_points={
        "console_scripts": [
            "raygen = raygen.cli:main",
        ]
    },
)
