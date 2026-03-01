"""
URE MVP - Unified Rural Ecosystem
Setup configuration for Python package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements from requirements.txt
def read_requirements(filename):
    """Read requirements from file"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#') and not line.startswith('-r')]

setup(
    name="ure-mvp",
    version="0.1.0",
    author="URE Development Team",
    author_email="team@ure-project.com",
    description="Unified Rural Ecosystem - AI-powered platform for rural communities in India",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandeepudeg/Assembler_URE_Rural",
    project_urls={
        "Bug Tracker": "https://github.com/sandeepudeg/Assembler_URE_Rural/issues",
        "Documentation": "https://github.com/sandeepudeg/Assembler_URE_Rural/wiki",
        "Source Code": "https://github.com/sandeepudeg/Assembler_URE_Rural",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "lambda": read_requirements("requirements-lambda.txt"),
    },
    entry_points={
        "console_scripts": [
            "ure-cli=ure.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ure": [
            "config/*.json",
            "config/*.yaml",
            "data/*.csv",
            "data/*.json",
        ],
    },
    zip_safe=False,
)
