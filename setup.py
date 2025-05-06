from setuptools import setup
import pathlib
import re


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

version = ''

with open('lavaplay/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set')


setup(
    name='lavaplay.py',
    version=version,
    description='Its a lavalink nodes manger to make a music bots for discord with python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HazemMeqdad/lavaplay.py',
    author='HazemMeqdad',
    author_email='hazemmeqdad@outlook.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='lavalink, discord, discord-lavalink, lavaplay, lavaplay.py',
    packages=["lavaplay"],
    install_requires=["aiohttp"],
    project_urls={
        'Bug Reports': 'https://github.com/HazemMeqdad/lavaplay.py/issues',
        'Source': 'https://github.com/HazemMeqdad/lavaplay.py/',
        'Documentation': 'https://lavaplay.readthedocs.io/en/latest'
    },
)
