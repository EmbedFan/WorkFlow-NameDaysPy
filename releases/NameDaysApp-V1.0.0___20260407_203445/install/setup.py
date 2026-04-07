"""
Setup configuration for Name Days Monitoring App package.

Install with: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path, "r", encoding="utf-8") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

# Read README
readme_path = Path(__file__).parent / "README.md"
readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="namedays-monitoring-app",
    version="1.0.0",
    description="Windows desktop application for monitoring contact namedays",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Development Team",
    author_email="dev@example.com",
    url="https://github.com/yourusername/namedays-monitoring-app",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "namedays-app=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": [
            "resources/**/*",
            "i18n/**/*.json",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Natural Language :: Hungarian",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Communications",
    ],
    keywords="namedays notifications windows desktop calendar",
)
