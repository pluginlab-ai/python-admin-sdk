from setuptools import setup, find_packages

setup(
    name='pluginlab_admin',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "pyjwt[crypto]>=2.8.0,<3.0.0"
    ],
)
