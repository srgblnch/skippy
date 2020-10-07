Skippy
======

This project starts to provide [tango](http://tango-controls.org) access to instruments that supports [scpi](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments) communications like _scopes_, _function generators_, _spectrum analyzers_, among others. It has been splitted in a python module and a tango device server that uses this module. So it can be used from python without the tango infrastructure (but with [PyTango](https://pytango.readthedocs.io/en/stable/) installed because it uses mainly states and other constants from it). 

![license GPLv3+](https://img.shields.io/badge/license-GPLv3+-green.svg)

Current version is `1.5.6`.

There is a brother project called [scpilib](https://github.com/srgblnch/python-scpilib) also written in python and it is used in the tests. It is the server side of this project, so one can include scpi support to an instrument to later control it using the skippy client side. 

## Development guide

For any contribution, as well as for any user, to understand the versioning tags one has to know has the flow being thought.

The base is the [GitHubFlow](https://guides.github.com/introduction/flow/) (much simpler than [GitFlow](https://datasift.github.io/gitflow/IntroducingGitFlow.html)) and for that it has been setup the [bumpversion](https://github.com/peritus/bumpversion).

See the guide for the [versioning](https://github.com/srgblnch/skippy/wiki/versioning-rules). 
