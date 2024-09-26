from setuptools import setup, find_packages

setup(
    name='aiutils',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'tiktoken', 'requests', 'openai', 'datetime'  # Add your package dependencies here
    ],
    description='Utility functions for token counting and pricing checks for OpenAI models.',
    author='Aidan Coughlan',
    author_email='aidan@farfromavocados.com',
    url='https://github.com/farfromavocaido/ai_utils',
    license='MIT',
    package_data={
        '': ['pricing.json'],  # Ensure pricing.json is included
    },
)