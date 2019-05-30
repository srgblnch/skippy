>>> from skippylib import Skippy
>>> skippyObj = Skippy(name='scodilt0401', port=5025, nChannels=4)
>>> skippyObj.idn
'KEYSIGHT TECHNOLOGIES,DSOS204A,MY58150181,06.30.00701'
>>> stateCh1 = skippyObj.attributes['StateCh1']
>>> print("{!r}".format(StateCh1))
StateCh1 (SkippyReadWriteAttribute):
    rvalue: True
    wvalue: None
    timestamp: 1559207397.3
    quality: ATTR_VALID
    type: DevBoolean
    dim: 0
    readCmd: ':CHAN1:DISPlay?'
    readFormula: None
    writeCmd: ':%s%d:DISPlay %s'
>>> stateCh1.isRampeable()
False
