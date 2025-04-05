from setuptools import setup
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='lavaplay.py',
    version='1.0.15a',
    description='Its a lavalink nodes manger to make a music bots for discord with python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HazemMeqdad/lavaplay.py',
    author='HazemMeqdad',
    author_email='hazemmeqdad@outlook.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
