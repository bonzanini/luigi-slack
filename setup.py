from setuptools import setup, find_packages

long_description = ''

setup(
    name='luigi-slack',
    version='0.1.2',
    description='Send Slack notifications to report on Luigi pipelines',
    long_description=long_description,
    author='Marco Bonzanini',
    author_email='marco.bonzanini@gmail.com',
    url='https://github.com/bonzanini',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'luigi>=1.3',
        'slackclient>=0.16'
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Monitoring',
    ]
)
