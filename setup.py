import os

from setuptools import find_packages, setup

if os.path.exists("README.md"):
    with open("README.md", "r") as f:
        readme = f.read()
else:
    readme = ""


setup(
    name="conda-souschef",
    packages=find_packages(where="src"),
    use_scm_version={"write_to": "src/souschef/_version.py"},
    setup_requires=["setuptools-scm", "setuptools>=30.3.0"],
    package_data={"": ["LICENSE", "AUTHORS"]},
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=["ruamel.yaml >=0.15.3", "ruamel.yaml.jinja2"],
    extras_require={"testing": ["pytest", "mock", "pytest-cov"]},
    url="https://github.com/marcelotrevisani/souschef",
    license="Apache-2.0",
    author="Marcelo Duarte Trevisani",
    author_email="marceloduartetrevisani@gmail.com",
    description="Project to handle conda recipes",
    long_description_content_type="text/markdown",
    long_description=readme,
    project_urls={"Source": "https://github.com/marcelotrevisani/souschef"},
)
