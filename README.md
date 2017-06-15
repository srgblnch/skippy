# Skippy [Tango](www.tango-controls.org) device server

*Skippy* is how is pronounced the **scpi** (acronim of *Standard Commands for Programmable Instruments*). This word has inspired the name of this [Tango](www.tango-controls.org) device server.

For further information about design, implementation and how to deploy, there is a [documentation file](doc/SkippyDeviceServer.pdf) in the *doc* directory.

## [Semantic version](semver.org)ing

This project is using [bumpversion](https://github.com/peritus/bumpversion) to manage the version numbering and with it, it is following the rules of *Semantic Version*. But a small clarification has been agreed between the developers.

* *MINOR* number is increased when a new functionality is included to the device and/or a new instrument has been included.
* *PATCH* number is increased for bugfixes of the devices and/or when new attributes are introduced to an existing instrument.

The detail here is that a new attribute to an existing instrument is not considered a new functionality, it is considered only a patch to the instrument.


## Quick deploy guide

**TODO**