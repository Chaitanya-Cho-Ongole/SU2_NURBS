<p align="center">
<img width="300" height="300" src="Docs/logo.png">
</p>


# SU2-CalculiX (ver. 1.0.1 "Columbia"): Open-Source CFD-CSD Code

Achieving environmental sustainability in the aviation sector requires a holistic approach that combines technological innovation, seamless integration of key aircraft components—particularly airframes and propulsion systems—into synergistic designs, and transformative advancements in operations and energy sources.

This repository hosts a high-fidelity aero-structural optimization framework built on a customized SU2 fork. It integrates SU2 with CalculiX to enhance its capabilities, enabling the solution of advanced aeroelastic topology optimization problems.


For an overview of the technical details in SU2, please see the following AIAA Journal article:

"SU2: An open-source suite for multiphysics simulation and design," AIAA Journal, 54(3):828-846, 2016. <http://arc.aiaa.org/doi/10.2514/1.J053813>

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

Continuous Integration:<br/>
[![Regression Testing](https://github.com/su2code/SU2/workflows/Regression%20Testing/badge.svg?branch=develop)](https://github.com/su2code/SU2/actions)
[![Release](https://github.com/su2code/SU2/workflows/Release%20Management/badge.svg?branch=develop)](https://github.com/su2code/SU2/actions)

Code Quality:<br/>
[![CodeFactor](https://www.codefactor.io/repository/github/su2code/su2/badge)](https://www.codefactor.io/repository/github/su2code/su2)

# SU2 Introduction

SU2 is a suite of open-source software tools written in C++ for the numerical solution of partial differential equations (PDE) and performing PDE constrained optimization.

The primary applications are computational fluid dynamics and aerodynamic shape optimization, but has been extended to treat more general equations such as electrodynamics and chemically reacting flows.

You will find more information and the latest news in:

- SU2 Home Page: <https://su2code.github.io>
- GitHub repository: <https://github.com/su2code>
- CFD Online: <http://www.cfd-online.com/Forums/su2/>
- Twitter: <https://twitter.com/su2code>
- Facebook: <https://www.facebook.com/su2code>

# CalculiX Introduction

CalculiX is an open-source finite element analysis (FEA) software suite designed for solving complex structural mechanics problems with high efficiency and accuracy. 

The current implementation of CalculiX extendes wiith element-based density definition and filtering methods to solve topology optimization across structured and un-structured domains. 

# SU2 Installation

## Precompiled binaries for Linux, MacOS, Windows

You can find precompiled binaries of the latest version on our [download page](https://su2code.github.io/download.html) or under [releases](https://github.com/su2code/SU2/releases).

## Build SU2

The build system of SU2 is based on a combination of [meson](http://mesonbuild.com/) (as the front-end) and [ninja](https://ninja-build.org/) (as the back-end). Meson is an open source build system meant to be both extremely fast, and, even more importantly, as user friendly as possible. Ninja is a small low-level build system with a focus on speed.

Short summary of the minimal requirements:

- C/C++ compiler
- Python 3

**Note:** all other necessary build tools and dependencies are shipped with the source code or are downloaded automatically.

If you have these tools installed, you can create a configuration using the `meson.py` found in the root source code folder:

```
./meson.py build
```

Use `ninja` to compile and install the code

```
./ninja -C build install
```

For more information on how to install and build SU2 on Linux, MacOS or Windows, have a look at the [documentation](https://su2code.github.io/docs_v7/).

## SU2 Path setup

When installation is complete, please be sure to add the `$SU2_HOME` and `$SU2_RUN` environment variables, and update your `$PATH` with `$SU2_RUN`.

For example, add these lines to your `.bashrc` file:

```
export SU2_RUN="your_prefix/bin"
export SU2_HOME="/path/to/SU2vX.X.X/"
export PATH=$PATH:$SU2_RUN
export PYTHONPATH=$SU2_RUN:$PYTHONPATH
```

`$SU2_RUN` should point to the folder where all binaries and python scripts were installed. This is the prefix you set with the --prefix option to meson. Note that the bin/ directory is automatically added to your prefix path.

`$SU2_HOME` should point to the root directory of the source code distribution, i.e., `/path/to/SU2vX.X.X/`.

Thanks for building, and happy optimizing!

- The SU2 Development Team

# SU2 Developers

We follow the popular "GitFlow" branching model for scalable development. In the SU2 repository, the master branch represents the latest stable major or minor release (7.0, 6.2.0, etc.), it should only be modified during version releases. Work that is staged for release is put into the develop branch via Pull Requests on GitHub from various "feature" branches where folks do their day-to-day work on the code. At release time, the work that has been merged into the develop branch is pushed to the master branch and tagged as a release.

SU2 is being developed by individuals and organized teams all around the world.

A list of current contributors can be found in the AUTHORS.md file.

## Documentation

Code documentation can be generated by calling doxygen from the root of the project, then open Docs/html/index.html in a browser to consult the documentation.
