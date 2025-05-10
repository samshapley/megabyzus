from setuptools import setup, find_packages

setup(
    name="megabyzus",
    version="0.1.0",
    description="Agent of Defence - NASA Technology Data Collection and Analysis",
    author="Megabyzus Team",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests",
        "tabulate",
        "matplotlib",
        "fastapi",
        "uvicorn",
        "anthropic",
    ],
    python_requires=">=3.6",
)