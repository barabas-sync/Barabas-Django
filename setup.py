#!/usr/bin/env python

from distutils.core import setup
import glob

setup(name='Barabas DJango',
      version='0.1',
      description='Barabas DJango Application',
      author='Nathan Samson',
      author_email='nathan.samson@student.ua.ac.be',
      url='http://github.com/barabas-sync/Barabas-Server/',
      package_dir={'barabasdjango': 'src'},
      data_files=[('/usr/share/barabas/templates', ['templates/main.html']),
                  ('/usr/share/barabas/templates/barabas', glob.glob('templates/barabas/*')),
                  ('/usr/share/barabas/templates/users', glob.glob('templates/users/*')),
                  ('/usr/share/barabas/static', glob.glob('static/*'))],
      packages=['barabasdjango', 'barabasdjango.files', 'barabasdjango.users'],
      requires=["django(>=1.3)", "barabas(==0.1)"]
     )
