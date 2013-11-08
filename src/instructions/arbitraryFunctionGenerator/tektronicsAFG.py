#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        tektronicsAFG.py
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

Attribute('State',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":OUTPut%d:STATE?",
           'writeCmd':lambda num:(lambda value:":OUTPut%d:STATE %s"%(num,value)),
           'channels':True
         })

Attribute('ModulationAM',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":source%d:am:state?",
           'writeCmd':lambda num:(lambda value:":source%d:am:state %s"%(num,value)),
           'channels':True
         })

Attribute('ModulationFM',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":source%d:fm:state?",
           'writeCmd':lambda num:(lambda value:":source%d:fm:state %s"%(num,value)),
           'channels':True
         })

Attribute('ModulationFSK',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":source%d:fsk:state?",
           'writeCmd':lambda num:(lambda value:":source%d:fsk:state %s"%(num,value)),
           'channels':True
         })

Attribute('ModulationPM',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":source%d:pm:state?",
           'writeCmd':lambda num:(lambda value:":source%d:pm:state %s"%(num,value)),
           'channels':True
         })

Attribute('Function',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":SOURce%d:FUNCtion:SHAPe?",
           'writeCmd':lambda num:(lambda value:":SOURce%d:FUNCtion:SHAPe %s"%(num,value)),
           'channels':True
         })

Attribute('lock',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":SYSTem:KLOCk:STATe?",
           'writeCmd':lambda value:":SYSTem:KLOCk:STATe %s"%(value)
         })

Attribute('click',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":SYSTem:KCLick:STATe?",
           'writeCmd':lambda value:":SYSTem:KCLick:STATe %s"%(value)
         })

Attribute('beep',
          {'type':PyTango.CmdArgType.DevBoolean,
           'dim':[0],
           'readCmd':":SYSTem:BEEPer:STATe?",
           'writeCmd':lambda value:":SYSTem:BEEPer:STATe %s"%(value)
         })