from distutils.core import setup
setup(
  name = 'panivida',
  packages = ['panivida'],
  version = '0.2',
  license='MIT',
  description = 'Simple wrapper class for Gmail API to send and receive email',
  author = 'Vidura Dantanarayana',
  author_email = 'vidurada@gmail.com',
  url = 'https://github.com/Vidurada/panivida',
  download_url = '',
  keywords = ['Gmail', 'API', 'Mail', 'Email', 'Mail Client', 'Wrapper'],
  install_requires=[
          'httplib2',
          'apiclient',
          'oauth2client',
          'google-api-python-client',
          'google_auth_oauthlib',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',

  ],
)