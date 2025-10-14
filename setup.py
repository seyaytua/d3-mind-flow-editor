#!/usr/bin/env python3
"""
D3-Mind-Flow-Editor Setup Script
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="d3-mind-flow-editor",
    version="1.0.0",
    author="seyaytua",
    author_email="",
    description="D3.js powered Mind Map, Flow Chart, and Gantt Chart Desktop Editor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seyaytua/d3-mind-flow-editor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: JavaScript",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "d3-mind-flow-editor=src.main:main",
        ],
    },
    package_data={
        "src": [
            "assets/**/*",
        ],
    },
    include_package_data=True,
)