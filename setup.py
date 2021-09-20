from setuptools import setup, find_packages

setup(
    name="minotaur",
    version="0.1",
    description="Escape the maze of instrumentation and analysis",
    url="http://github.com/csmith49/minotaur",
    author="Calvin Smith", 
    author_email="email@cjsmith.io",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "click",
        "hashids",
        "networkx",
        "rich"
    ],
    zip_safe=False,
    entry_points={
        "console_scripts" : [
            "minotaur = minotaur.scripts.cli:cli"
        ]
    }
)

