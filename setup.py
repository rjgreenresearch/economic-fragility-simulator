from setuptools import setup, find_packages
setup(
    name="economic-fragility-simulator",
    version="0.1.0",
    author="Robert J. Green",
    author_email="robert@rjgreenresearch.org",
    description="Compound Economic Fragility Simulator (MTS Pillar 4)",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["pandas>=2.0","numpy>=1.24","scipy>=1.10","matplotlib>=3.7","fredapi>=0.5.0","statsmodels>=0.14"],
)
