from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='Pilot',
    version='0.0.1',
    description='BGP flowspec based SDN controller at home',
    license="Proprietary",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='James Swineson',
    author_email='pypi@public.swineson.me',
    url="https://github.com/Jamesits/Pilot",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'pilot_server=Pilot.__main__:main'
        ]
    }
)
