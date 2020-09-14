import setuptools

from tmval.constants import BUILD_VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tmval",
    version=BUILD_VERSION,
    author="Gene Dan",
    author_email="genedan@gmail.com",
    description="Time Value of Money",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/genedan/TmVal",
    project_urls={
        "Documentation": "https://genedan.com/tmval/docs"
    },
    install_requires=['numpy', 'scipy', 'dateutil'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6.0',
)
