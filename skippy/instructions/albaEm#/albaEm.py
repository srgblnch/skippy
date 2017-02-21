#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        AlbaEm#.py
## 
## Project :     SCPI
##
## $Author :      mbroseta$
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

Attribute('Mac',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"*MAC?",
           #'writeCmd':lambda num:(lambda value:":OUTPut%d:STATE %s"%(num,value)),
         })

# IO Port functions
Attribute('IO01_CONFIG',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO01:CONFI?",
           'writeCmd':lambda value:"IOPO01:CONFI %s"%value,
         })

Attribute('IO01',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO01:VALU?",
           'writeCmd':lambda value:"IOPO01:VALU %s"%value,
         })
Attribute('IO02_CONFIG',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO02:CONFI?",
           'writeCmd':lambda value:"IOPO02:CONFI %s"%value,
         })

Attribute('IO02',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO02:VALU?",
           'writeCmd':lambda value:"IOPO02:VALU %s"%value,
         })
Attribute('IO03_CONFIG',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO03:CONFI?",
           'writeCmd':lambda value:"IOPO03:CONFI %s"%value,
         })

Attribute('IO03',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO03:VALU?",
           'writeCmd':lambda value:"IOPO03:VALU %s"%value,
         })
Attribute('IO04_CONFIG',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO04:CONFI?",
           'writeCmd':lambda value:"IOPO04:CONFI %s"%value,
         })

Attribute('IO04',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"IOPO04:VALU?",
           'writeCmd':lambda value:"IOPO04:VALU %s"%value,
         })


# Trigger Commands
Attribute('TriggerDelay',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"TRIG:DELA?",
           'writeCmd':lambda value:"TRIG:DELA %s"%value,           
         })
Attribute('TriggerInput',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"TRIG:INPU?",
           'writeCmd':lambda value:"TRIG:INPU %s"%value,           
         })
Attribute('TriggerMode',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"TRIG:MODE?",
           'writeCmd':lambda value:"TRIG:MODE %s"%value,           
         })
Attribute('TriggerPolarity',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"TRIG:POLA?",
           'writeCmd':lambda value:"TRIG:POLA %s"%value,           
         })
Attribute('SWTrigger',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"TRIG:SWSET?",
           'writeCmd':lambda value:"TRIG:SWSET %s"%value,           
         })

# Acquisition Commands
Attribute('AcqFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:FILTER?",
           'writeCmd':lambda value:"ACQU:FILTER %s"%value,           
         })
Attribute('Meas',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:MEAS?",
           #'writeCmd':lambda value:"ACQU:FILTER %s"%value,           
         })
Attribute('NData',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:NData?",
           #'writeCmd':lambda value:"ACQU:FILTER %s"%value,           
         })
Attribute('AcqRange',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:RANGE?",
           'writeCmd':lambda value:"ACQU:RANGE %s"%value,           
         })
Attribute('AcqStart',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:START?",
           'writeCmd':lambda value:"ACQU:START %s"%value,           
         })
Attribute('AcqState',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:STATE?",
           #'writeCmd':lambda value:"ACQU:FILTER %s"%value,           
         })
Attribute('AcqStop',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:STOP?",
           'writeCmd':lambda value:"ACQU:STOP %s"%value,           
         })
Attribute('AcqTime',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"ACQU:TIME?",
           'writeCmd':lambda value:"ACQU:TIME %s"%value,           
         })


# Channel 01
Attribute('CHAN01_InstantCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN01:INSCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN01_Current',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN01:CURRent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN01_AverageCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN01:AVGCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN01_CARange',
          {'type':PyTango.CmdArgType.DevLong,
           'dim':[0],
           'readCmd':"CHAN01:CABO:RANGE?",
           'writeCmd':lambda value:"CHAN01:CABO:RANGE %s"%value,           
         })
Attribute('CHAN01_CAFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN01:CABO:FILT?",
           'writeCmd':lambda value:"CHAN01:CABO:FILT %s"%value,
         })
Attribute('CHAN01_CAPostFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN01:CABO:POST?",
           'writeCmd':lambda value:"CHAN01:CABO:POST %s"%value,
         })
Attribute('CHAN01_CAPreFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN01:CABO:PREF?",
           'writeCmd':lambda value:"CHAN01:CABO:PREF %s"%value,
         })
Attribute('CHAN01_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN01:CABO:INVE?",
           'writeCmd':lambda value:"CHAN01:CABO:INVE %s"%value,
         })
Attribute('CHAN01_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN01:CABO:TIGA?",
           'writeCmd':lambda value:"CHAN01:CABO:TIGA %s"%value,
         })
Attribute('CHAN01_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN01:CABO:VGAI?",
           'writeCmd':lambda value:"CHAN01:CABO:VGAI %s"%value,
         })

# Channel 02
Attribute('CHAN02_InstantCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN02:INSCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN02_Current',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN02:CURRent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN02_AverageCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN02:AVGCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN02_CARange',
          {'type':PyTango.CmdArgType.DevLong,
           'dim':[0],
           'readCmd':"CHAN02:CABO:RANGE?",
           'writeCmd':lambda value:"CHAN02:CABO:RANGE %s"%value,           
         })
Attribute('CHAN02_CAFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN02:CABO:FILT?",
           'writeCmd':lambda value:"CHAN02:CABO:FILT %s"%value,
         })
Attribute('CHAN02_CAPostFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN02:CABO:POST?",
           'writeCmd':lambda value:"CHAN02:CABO:POST %s"%value,
         })
Attribute('CHAN02_CAPreFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN02:CABO:PREF?",
           'writeCmd':lambda value:"CHAN02:CABO:PREF %s"%value,
         })
Attribute('CHAN02_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN02:CABO:INVE?",
           'writeCmd':lambda value:"CHAN02:CABO:INVE %s"%value,
         })
Attribute('CHAN02_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN02:CABO:TIGA?",
           'writeCmd':lambda value:"CHAN02:CABO:TIGA %s"%value,
         })
Attribute('CHAN02_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN02:CABO:VGAI?",
           'writeCmd':lambda value:"CHAN02:CABO:VGAI %s"%value,
         })

# Channel 03
Attribute('CHAN03_InstantCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN03:INSCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN03_Current',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN03:CURRent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN03_AverageCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN03:AVGCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN03_CARange',
          {'type':PyTango.CmdArgType.DevLong,
           'dim':[0],
           'readCmd':"CHAN03:CABO:RANGE?",
           'writeCmd':lambda value:"CHAN03:CABO:RANGE %s"%value,           
         })
Attribute('CHAN03_CAFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN03:CABO:FILT?",
           'writeCmd':lambda value:"CHAN03:CABO:FILT %s"%value,
         })
Attribute('CHAN03_CAPostFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN03:CABO:POST?",
           'writeCmd':lambda value:"CHAN03:CABO:POST %s"%value,
         })
Attribute('CHAN03_CAPreFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN03:CABO:PREF?",
           'writeCmd':lambda value:"CHAN03:CABO:PREF %s"%value,
         })
Attribute('CHAN03_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN03:CABO:INVE?",
           'writeCmd':lambda value:"CHAN03:CABO:INVE %s"%value,
         })
Attribute('CHAN03_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN03:CABO:TIGA?",
           'writeCmd':lambda value:"CHAN03:CABO:TIGA %s"%value,
         })
Attribute('CHAN03_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN03:CABO:VGAI?",
           'writeCmd':lambda value:"CHAN03:CABO:VGAI %s"%value,
         })

# Channel 04
Attribute('CHAN04_InstantCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN04:INSCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN04_Current',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN04:CURRent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN04_AverageCurrent',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"CHAN04:AVGCurrent?",
           #'writeCmd':lambda num:(lambda value:"DEBUg:ENABle %s"%value),
         })
Attribute('CHAN04_CARange',
          {'type':PyTango.CmdArgType.DevLong,
           'dim':[0],
           'readCmd':"CHAN04:CABO:RANGE?",
           'writeCmd':lambda value:"CHAN04:CABO:RANGE %s"%value,           
         })
Attribute('CHAN04_CAFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN04:CABO:FILT?",
           'writeCmd':lambda value:"CHAN04:CABO:FILT %s"%value,
         })
Attribute('CHAN04_CAPostFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN04:CABO:POST?",
           'writeCmd':lambda value:"CHAN04:CABO:POST %s"%value,
         })
Attribute('CHAN04_CAPreFilter',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN04:CABO:PREF?",
           'writeCmd':lambda value:"CHAN04:CABO:PREF %s"%value,
         })
Attribute('CHAN04_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN04:CABO:INVE?",
           'writeCmd':lambda value:"CHAN04:CABO:INVE %s"%value,
         })
Attribute('CHAN04_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN04:CABO:TIGA?",
           'writeCmd':lambda value:"CHAN04:CABO:TIGA %s"%value,
         })
Attribute('CHAN04_CAInversion',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':"CHAN04:CABO:VGAI?",
           'writeCmd':lambda value:"CHAN04:CABO:VGAI %s"%value,
         })

