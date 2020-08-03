import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="log_parser",
    version="1.0.0",
    author="Ekaterina Bezverkhniaia",
    author_email="indefeneilydeepsea@gmail.com",
    description="Log parsing library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GGM03/log_parsing_test_task",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet :: Log Analysis"
    ],
    python_requires=">=3.6",
    install_requires=[],
    entry_points={
        'console_scripts': [
            'log_parser = log_parser.__main__:main',
        ],
    },
)
