from setuptools import setup, find_packages

setup(
    name="trading-analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "aiohttp",
        "python-dotenv",
        "requests",
        "plotly",
        "fastapi",
        "uvicorn",
    ],
) 