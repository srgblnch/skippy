#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        arroyo5300.py
## 
## Project :     SCPI
##
## $Author :      jmoldes$
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

Attribute('Temperature',
          {'type':PyTango.CmdArgType.DevDouble,
           'dim':[0],
           'readCmd':"TEC:T?",
         })
