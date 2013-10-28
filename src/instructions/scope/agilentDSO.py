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

####
# Example of attribute:
#
#   Attribute('name' -> name of the attribute
#             {'type' -> check the PyTango.CmdArgType
#              'dim'  -> can be: 0
#                               [1,X]
#                               [2,X,Y]
#              'channels' -> boolean to build attrs with a 'ch' suffix
#              'funtions' -> boolean to build attrs with a 'fn' suffix
#              'unit'     -> the unit of the tango attribute
#              'min','max'-> in writable attributes configure limits
#              'format'   -> in floats and integers the representation
#              'label'    -> attribute property
#              'description' -> attribute property
#              'memorized' -> attribute property
#             }
#            )
#

Attribute('Amplitude',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim' :0,
           'readCmd':lambda ch,num:":MEASure:VAMPlitude? %s%d"%(ch,num),
           'channels':True,
           'functions':True,
         })

Attribute('OffsetH',
         {'type':PyTango.CmdArgType.DevDouble,
          'dim':0,
          'readCmd':":TIMebase:POS?",
          'writeCmd':lambda value:":TIMebase:POS %s"%(str(value)),
         })
        