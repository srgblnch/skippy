#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        agilentDSO.py
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
           'readCmd':lambda ch,num:":SELect:%s%d?"%(ch,num),
           'writeCmd':lambda ch,num:(lambda value:":SELect:%s%d %s"%(ch,num,value)),
           'channels':True,
         })

Attribute('Impedance',
          {'type':PyTango.CmdArgType.DevString,
           'dim':[0],
           'readCmd':lambda ch,num:":%s%d:TERmination"%(ch,num),
           'channels':True,
         })

Attribute('Amplitude',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim' :[0],
           'readCmd':lambda ch,num:":MEASUrement:IMMed:TYPe AMPlitude;"\
                                   ":MEASUrement:IMMed:SOURCE %s%d;"\
                                   ":MEASUrement:IMMed:VALue?"%(ch,num),
           'channels':True,
         })

# Attribute('Scale',
#           {'type':PyTango.CmdArgType.DevDouble,
#            'dim':[0],
#            'channels':True,
#          })

Attribute('Offset',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':lambda ch,num:":%s%d:OFFSet?"%(ch,num),
           'writeCmd':lambda ch,num:(lambda value:":%s%d:OFFSet %s"%(ch,num,value)),
           'channels':True,
         })

Attribute('CurrentSampleRate',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':":HORizontal:MAIn:SAMPLERate?",
         })

Attribute('ScaleH',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':":HORizontal:SCAle?",
           'writeCmd':lambda value:":HORizontal:SCAle %s"%(str(value)),
         })

# Attribute('OffsetH',
#          {'type':PyTango.CmdArgType.DevDouble,
#           'dim':[0],
#         })

