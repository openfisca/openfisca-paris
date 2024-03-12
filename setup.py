# -*- coding: utf-8 -*-
from setuptools import setup, find_namespace_packages

setup(
    name="Openfisca-Paris",
    version="5.5.2",
    author="OpenFisca Team",
    author_email="contact@openfisca.fr",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    description="Plugin OpenFisca pour les aides sociales de la mairie de Paris",
    long_description_content_type='text/markdown',
    keywords="benefit france paris microsimulation social tax",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",

    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=[
        'OpenFisca-Core >= 40.0.1, < 42',
        'OpenFisca-France >= 149.1.1, < 160',
    ],
    extras_require={
        'test': [
            'nose',
            'pytest >= 5.4.2'
        ]
    },
)
