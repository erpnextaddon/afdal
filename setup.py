from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in afdal_management/__init__.py
from afdal_management import __version__ as version

setup(
	name="afdal_management",
	version=version,
	description="Afdal",
	author="Afdal",
	author_email="hafeesk@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
