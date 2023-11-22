from setuptools import setup

setup(
    name='ipums_scraper',
    version='0.1.0',    
    description='A package for downloading IPUMS data',
    url='https://github.com/katrbrow/IPUMS_Data_Scraper',
    author='Katrina Brown',
    author_email='katrinabrown@college.harvard.edu',
    license='BSD 2-clause',
    packages=['ipums_scraper'],
    install_requires=['ipumspy>=0.4.1',
                      'pandas',         
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)