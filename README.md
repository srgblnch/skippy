# Skippy [Tango](www.tango-controls.org) device server

*Skippy* is how is pronounced the **scpi** (acronim of *Standard Commands for Programmable Instruments*). This word has inspired the name of this [Tango](www.tango-controls.org) device server.

For further information about design, implementation and how to deploy, there is a [documentation file](doc/SkippyDeviceServer.pdf) in the *doc* directory.

## [Semantic version](semver.org)ing

This project is using [bumpversion](https://github.com/peritus/bumpversion) to manage the version numbering and with it, it is following the rules of *Semantic Version*. But a small clarification has been agreed between the developers.

* *MINOR* number is increased when a new functionality is included to the device and/or a new instrument has been included.
* *PATCH* number is increased for bugfixes of the devices and/or when new attributes are introduced to an existing instrument.

The detail here is that a new attribute to an existing instrument is not considered a new functionality, it is considered only a patch to the instrument.


## Quick deploy guide

It is assumed that one have a tango database where it is wanted to have a new Skippy device server. First is needed to have a python object representing the tango database:

```python
import PyTango
tangodb = PyTango.Database()
```

One can find an example in the *fakeInstrument* test, and here will be explained the main actions executed on the mentioned example:

```python
DevServer = 'Skippy'
DevInstance = 'FakeInstrument'
DevClass = 'Skippy'
DevName = 'fake/skyppy/instrument-01'

devInfo = PyTango.DbDevInfo()
devInfo.name = DevName
devInfo._class = DevClass
devInfo.server = DevServer+"/"+DevInstance
tangodb.add_device(devInfo)
```

The device server is created, but don't get confused: it is not running. Before that, one have to setup the device properties (the distributed system agent construction parameters). For the *fakeInstrument* the instrument is accessed using loopback network interface:

```python
propertyName = 'Instrument'
propertyValue = 'localhost'
property = PyTango.DbDatum(propertyName)
property.value_string.append(propertyValue)
tangodb.put_device_property(DevName, property)
```

At this point the device server is ready to be launched for the first time. One can use [Astor](http://www.esrf.eu/computing/cs/tango/tango_doc/tools_doc/astor_doc/index.html) or console launcher, but also from the same *python* console can be launched.

```python
from subprocess import Popen
Popen([DevServer, DevInstance, "-v4"])
```

But have on mind that existing the *python* console the device server will exit.
