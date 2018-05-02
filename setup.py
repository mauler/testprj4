import setuptools


setuptools.setup(
    install_requires=[
        'Django',
    ],

    setup_requires=[
        'Django',
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-django',
        'pytest-flakes',
        'pytest-pythonpath',
        'pytest-sugar',
    ],

    name='cards',
    version='0.0.1',

    author='Paulo R',
    author_email='proberto.macedo@gmail.com',

    description='Cards Issuer Project',
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(exclude='tests'),

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
