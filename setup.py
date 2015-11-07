from setuptools import setup, find_packages

long_description = ''

setup(
    name='luigi-slack',
    version='0.1',
    description='Send Slack notifications to report on Luigi pipelines',
    long_description=long_description,
    author='Marco Bonzanini',
    author_email='marco.bonzanini@gmail.com',
    url='https://github.com/bonzanini',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
