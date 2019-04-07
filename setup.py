#!/usr/bin/env python3
# encoding: utf-8

from distutils.core import setup, Extension

rpygrating_module = Extension('_rpigratings', 
		sources = ['_rpigratings.c'],
                extra_compile_args = ['-O3'])

setup(name='_rpigratings',
      version='0.1.0',
      description='A drifting grating implimentation',
      ext_modules=[rpygrating_module])
