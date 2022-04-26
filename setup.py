from setuptools import setup

setup(
    name="redact-diag-info",
    version='0.0.1',
    author='Brendan Cicchi',
    description='Redact sensitive data from diagnostics such as passwords',
    python_requires='>=3.6',
    install_requires=[
        'click==7.0',
        'packaging==20.1',
        'ruamel.yaml==0.17.21',
    ],
    entry_points={
        'console_scripts': [
            'redact-diag = redact_sensitive_diag_info:remove_sensitive_info',
        ]
    }
)