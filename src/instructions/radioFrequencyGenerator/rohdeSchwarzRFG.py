#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        rohdeSchwarzRFG.py
## 
## Project :     SCPI
##
## $Author :      sblanch$
##
## $Revision :    $
##
## $Date :        $
##
## $HeadUrl :     $
##============================================================================
##        (c) - Controls Software Section - ALBA/CELLS
##############################################################################

import PyTango

Attribute('Frequency',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':":FREQ?",
           'writeCmd':lambda value:":FREQ %s"%(str(value)),
           'rampeable':True,
         })

Attribute('PowerLevel',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':":POW?",
           'writeCmd':lambda value:":POW %s"%(str(value)),
         })

Attribute('RfState',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":OUTP:STAT?",
           'writeCmd':lambda value:":OUTP:STAT %s"%(value),
         })

Attribute('FrequencyRangeLow',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':":FREQ:PHAS:CONT:LOW?",
           'writeCmd':lambda value:":FREQ:PHAS:CONT:LOW %s"%(str(value)),
         })

Attribute('FrequencyRangeHigh',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':":FREQ:PHAS:CONT:HIGH?",
           'writeCmd':lambda value:":FREQ:PHAS:CONT:HIGH %s"%(str(value)),
         })

Attribute('PowerRangeLow',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"::OUTP:AFIX:RANG:LOW?",
           'writeCmd':lambda value:":OUTP:AFIX:RANG:LOW %s"%(str(value)),
         })

Attribute('PowerRangeHigh',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':":OUTP:AFIX:RANG:UPP?",
           'writeCmd':lambda value:":OUTP:AFIX:RANG:UPP %s"%(str(value)),
         })

Attribute('Impedancy',
          {'type':PyTango.CmdArgType.DevShort,
           'dim':[1,100],
           'readCmd':":OUTP:IMP?",
         })

Attribute('PhaseContinuousFrequencyActive',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":FREQ:PHAS:CONT:STAT?",
         })

Attribute('PhaseContinuousFrequencyNarrow',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':":FREQ:PHAS:CONT:MODE?",
         })

Attribute('ExtOscSrc',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":ROSCillator:SOURce?",
           'writeCmd':lambda value:":ROSCillator:SOURce %s"%(str(value)),
         })

Attribute('Errors',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[1,100],
           'readCmd':":SYST:SERROR?",
         })
