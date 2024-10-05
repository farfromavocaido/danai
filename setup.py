from setuptools import setup, find_packages

setup(
    name='aiutils',
    version='0.3.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'tiktoken', 'requests', 'openai', 'datetime' # Add your package dependencies here
    ],
    description='Utility functions for token counting and pricing checks for OpenAI models.',
    author='Aidan Coughlan',
    author_email='aidan@farfromavocados.com',
    url='https://github.com/farfromavocaido/ai_utils',
    license='MIT',
    package_data={
        '': ['pricing.json'],  # Ensure pricing.json is included
    },
    entry_points={
        'console_scripts': [
            'aidan=aiutils.cli:main',  # Existing entry point
            'tcount=aiutils.cli:tokencount_cli',  # New entry point for tcount
        ],
    },
)