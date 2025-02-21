from setuptools import setup, find_packages

setup(
    name="neotuitive",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "astropy",
        "matplotlib",
        "plotly",
        "poliastro",
        "requests",
    ],
    author="Nikolaos Raptis",
    author_email="nikolaos.raptis83@gmail.com",
    description="A Python library for visualizing and analyzing Near-Earth Objects (NEOs) risk list",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/flyingraptor/neotuitive",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 