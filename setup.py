from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

# https://github.com/tandemdude/hikari-lightbulb/blob/development/setup.py#L50
def parse_requirements_file(path):
    with open(path) as fp:
        dependencies = (d.strip() for d in fp.read().split("\n") if d.strip())
        return [d for d in dependencies if not d.startswith("#")]

setup(
    name='lavaplayer',
    version='1.0.4a',
    description='A sample Python project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HazemMeqdad/lavaplayer',
    author='HazemMeqdad',
    author_email='hazemmeqdad@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='lavalink, discord, discord-lavalink, lavaplayer',
    packages=["lavaplayer"],
    install_requires=parse_requirements_file("requirements.txt"),
    project_urls={
        'Bug Reports': 'https://github.com/HazemMeqdad/lavaplayer/issues',
        'Source': 'https://github.com/HazemMeqdad/lavaplayer/',
        'Documentation': 'https://lavaplayer.readthedocs.io/en/latest'
    },
)
