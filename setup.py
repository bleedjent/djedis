from setuptools import setup

setup(
    name='djedis',
    version='0.1',
    packages=['cache',],
    url='',
    license='',
    author='Yura Revutskiy',
    author_email='dr.bleedjent@gmail.com',
    description='Another light django redis backend',

    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
        'redis',
        'django',
    ]
)
