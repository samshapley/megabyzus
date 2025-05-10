from setuptools import setup, find_packages

setup(
    name="megabyzus",
    version="0.1.0",
    description="Agent of Defence - NASA Technology Data Collection and Analysis",
    author="Megabyzus Team",
    packages=find_packages(),
    install_requires=[
        "requests",
        "tabulate",
        "matplotlib",
    ],
    python_requires=">=3.6",
)