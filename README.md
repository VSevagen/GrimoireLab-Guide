# GrimoireLab Guide

This documentation was generated using Sphinx and the theme used is Furo. In order to view it, just visit the following link, https://vsevagen.github.io/Test-documentation/

In order to generate documentation for any component,

- Install sphinx <code>pip install -U sphinx</code>
- Go into your project directory and create a directory <code>docs</code>
- Run <code>sphinx-quickstart</code>. This will setup a source directory and a default <code>conf.py</code> with mininal required config.
- You'll see two files among others, <code>index.rst</code> and <code>conf.py</code>. The former is your landing page and the other is the configuration file.
- In order to generate documentation regarding your python source files, go into <code>conf.py</code> and uncomment the following code and update the project path.

```
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
```

- Run the following line the generate the documentation

```
sphinx-apidoc -f -o <path-to-output> <path-to-module>
```

where <code>path-to-output</code> refers to where the generated docs will be stored and <code>path-to-module</code> refers to module path in need of documentation.

- Finally run <code>make html</code> and everything will be built.

This will build all the required file in the<code>\_build/html</code> directory. Open <code>index.html</code>in your browser to see the docs
