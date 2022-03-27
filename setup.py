from setuptools import setup
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='lavaplayer',
    version='1.0.8a',
    description='Its a lavalink nodes manger to make a music bots for discord with python.',
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
    install_requires=["aiohttp"],
    project_urls={
        'Bug Reports': 'https://github.com/HazemMeqdad/lavaplayer/issues',
        'Source': 'https://github.com/HazemMeqdad/lavaplayer/',
        'Documentation': 'https://lavaplayer.readthedocs.io/en/latest'
    },
)
