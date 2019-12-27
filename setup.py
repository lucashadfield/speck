from setuptools import setup, find_packages

setup(
    name='speck',
    version='0.1.0',
    author='Lucas Hadfield',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'pillow', 'opencv-python'],
    include_package_data=True,
)
