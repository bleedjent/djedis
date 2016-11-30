from setuptools import setup, find_packages

setup(
    name='djedis',
    version='0.1',
    packages=find_packages(),
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
        'hiredis',
        'uhashring',
        'python-snappy',
    ]
)
