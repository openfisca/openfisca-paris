# -*- coding: utf-8 -*-
from setuptools import setup, find_namespace_packages

setup(
    name="Openfisca-Paris",
    version="5.6.0",
    author="OpenFisca Team",
    author_email="contact@openfisca.fr",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    description="Plugin OpenFisca pour les aides sociales de la mairie de Paris",
    long_description_content_type='text/markdown',
    keywords="benefit france paris microsimulation social tax",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",

    python_requires='>= 3.11',
    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=[
        'OpenFisca-Core >= 43, < 47',
        'OpenFisca-France >= 169.0.0, < 177.0.0',
    ],
    extras_require={
        'test': [
            'nose',
            'pytest >= 5.4.2'
        ]
    },
)
