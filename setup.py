from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

# https://stackoverflow.com/a/50368460/2646069
with open('requirements.txt', 'r') as f:
    install_reqs = [
        s for s in [
            line.split('#', 1)[0].strip(' \t\n') for line in f
        ] if s != ''
    ]

packages = find_packages()
print(packages)

setup(
    name='pilot',
    version='0.0.1',
    description='BGP flowspec based SDN controller at home',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='James Swineson',
    author_email='pypi@public.swineson.me',
    url="https://github.com/Jamesits/Pilot",
    packages=packages,
    install_requires=install_reqs,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pilot_server=pilot.__main__:main'
        ]
    },
    python_requires='>=3.7',
    include_package_data=True,
)
