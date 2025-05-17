#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for Stock Management Application

This script helps with installing dependencies and packaging the application.
"""

from setuptools import setup, find_packages

setup(
    name="stock_manager",
    version="1.0.0",
    description="A production-ready stock management application",
    author="Stock Manager Team",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.4.0",
        "SQLAlchemy>=2.0.0",
        "alembic>=1.10.0",
        "pyqtchart>=0.1.4",
        "pandas>=1.5.0",
        "openpyxl>=3.0.10",
        "matplotlib>=3.6.0",
    ],
    entry_points={
        "console_scripts": [
            "stock-manager=main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Inventory",
    ],
)