"""Setup configuration for desafio-ibge package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="desafio-ibge",
    version="1.0.0",
    author="Leandro Marques",
    author_email="seu_email@exemplo.com",
    description="Desafio técnico - Integração IBGE com Supabase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/desafio-ibge",
    packages=find_packages(where="src"),
    py_modules=["main", "auth", "ibge_client", "processor", "stats", "submitter"],
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "desafio-ibge=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
