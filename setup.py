from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

long_description = ''

install_requires = [
    'luigi>=1.3',
    'slackclient>=1.0,<1.1'
]

tests_require = [
    'pytest'
]

setup(
    name='luigi-slack',
    version='0.1.6',
    description='Send Slack notifications to report on Luigi pipelines',
    long_description=long_description,
    author='Marco Bonzanini',
    author_email='marco.bonzanini@gmail.com',
    url='https://github.com/bonzanini',
    license='MIT',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass = {'test': PyTest},
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
    ],
)
