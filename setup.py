from setuptools import setup, find_packages

setup(
    name="smart-service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "grpcio",
        "grpcio-tools",
        "sqlalchemy",
        "psycopg2-binary",
        "python-dotenv",
    ],
)