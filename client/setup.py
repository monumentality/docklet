from setuptools import setup


setup(
    name = "docklet",
    version = "0.1",
    py_modules = ["client"],
    install_requires=[
        'click',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        docklet=client:main
    ''',
)
