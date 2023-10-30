from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = ["wandb==0.15.11", "transformers==4.34.1", "chardet==5.2.0"]

setup(
    name="mushroom-app-trainer",
    version="0.0.1",
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    description="Mushroom App Trainer Application",
)
