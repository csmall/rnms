# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>
#
""" Parsing functions for Rosenberg  NMS"""
from pyparsing import (Literal,CaselessLiteral,Word,Combine,Group,Optional,
        ZeroOrMore,Forward,nums,alphas,oneOf)
import math
import operator
from string import Template
import re

__field_re = re.compile(r'\${?([a-z0-9_-]+)',re.I)

def fill_fields(string, host=None, attribute=None, event=None):
    """
    Parse the raw string and fill any fields with values obtained from the
    given objects. Fields can be defined as $key or ${key} and use the
    standard string.Template parsing to do its job.
    Fields that are replaced are
      attribute         attribute.display_name
      attribute_id      attribute.id
      index             attribute.index
      description       attribute.description()
      speed_units       attribute field speed converted to SI units (64k)
      host              host.display_name or attribute.host.display_name

      state             event.alarm_state.display_name

      plus any fields from the event or attribute in that order
    """
    field_keys = __field_re.findall(string)
    if field_keys == []:
        return string
    field_values = {}
    # Event fields are firat as they may be overwritten
    if event is not None:
        field_values.update(dict([ef.tag,ef.data] for ef in event.fields))
    if host is not None:
        field_values['host'] = host.display_name
    if attribute is not None:
        field_values['attribute'] = attribute.display_name
        field_values['attribute_id'] = str(attribute.id)
        field_values['index'] = str(attribute.index)

    for field_key in field_keys:
        if field_key in field_values:
            continue
        if event is not None:
            if field_key == 'state':
                field_values[field_key] = event.alarm_state.display_name
        if attribute is not None:
            # expensive ones go here
            if field_key == 'description':
                field_values[field_key] = attribute.description()
                continue
            if  field_key == 'host':
                field_values['host'] = attribute.host.display_name
                continue
            # Special case, speed defaults to 10000000 (100 Mbps) if 0
            if field_key == 'speed':
                att_field = attribute.get_field('speed')
                if att_field is None or att_field == 0:
                    att_field = 100000000
                field_values['speed'] = att_field
                continue

            # Special case, speed_units convers 8000 -> '8.00 k'
            if field_key == 'speed_units':
                att_field = attribute.get_field('speed')
                if att_field is not None:
                    speed = float(att_field)
                    for div,sym in ((1000000.0,'M'), (1000.0,'k')):
                        if speed > div:
                            field_values['speed_units'] = str(speed/div)+' '+sym
                            break
                    else:
                        field_values['speed_units'] = att_field
                continue
            # Last thing to check, maybe attribute field?
            att_field = attribute.get_field(field_key)
            if att_field is not None:
                field_values[field_key] = att_field
    
    text_template = Template(string)
    return text_template.safe_substitute(field_values)





class RnmsTextTemplate(Template):
    """ Sub-class of Template to parse the event type strings """
#    pattern = r"""
#     <(?P.*)>  # Replace anything between <>
#     (?P)(?P)(?P)"""
    delimiter = '<'
    pattern = r'''
     <(?:
     (?P<escaped><)|
     (?P<named>[a-z][a-z0-9_-]*)>|
     {(?P<braced>[a-z][a-z0-9_-]*)}|
     (?P<invalid>)
     )
     '''

class NumericStringParser(object):
    '''
    Most of this code comes from the fourFn.py pyparsing example

    '''
    def pushFirst(self, strg, loc, toks ):
        self.exprStack.append( toks[0] )
    def pushUMinus(self, strg, loc, toks ):
        if toks and toks[0]=='-': 
            self.exprStack.append( 'unary -' )
    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal( "." )
        e     = CaselessLiteral( "E" )
        fnumber = Combine( Word( "+-"+nums, nums ) + 
                           Optional( point + Optional( Word( nums ) ) ) +
                           Optional( e + Word( "+-"+nums, nums ) ) )
        ident = Word(alphas, alphas+nums+"_$")       
        plus  = Literal( "+" )
        minus = Literal( "-" )
        mult  = Literal( "*" )
        div   = Literal( "/" )
        lpar  = Literal( "(" ).suppress()
        rpar  = Literal( ")" ).suppress()
        addop  = plus | minus
        multop = mult | div
        expop = Literal( "^" )
        pi    = CaselessLiteral( "PI" )
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (pi|e|fnumber|ident+lpar+expr+rpar).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar+expr+rpar)
                ).setParseAction(self.pushUMinus)       
        # by defining exponentiation as "atom [ ^ factor ]..." instead of 
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore( ( expop + factor ).setParseAction( self.pushFirst ) )
        term = factor + ZeroOrMore( ( multop + factor ).setParseAction( self.pushFirst ) )
        expr << term + ZeroOrMore( ( addop + term ).setParseAction( self.pushFirst ) )
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term       
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = { "+" : operator.add,
                "-" : operator.sub,
                "*" : operator.mul,
                "/" : operator.truediv,
                "^" : operator.pow }
        self.fn  = { "sin" : math.sin,
                "cos" : math.cos,
                "tan" : math.tan,
                "abs" : abs,
                "trunc" : lambda a: int(a),
                "round" : round,
                "sgn" : lambda a: abs(a)>epsilon and cmp(a,0) or 0}
    def evaluateStack(self, s ):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack( s )
        if op in "+-*/^":
            op2 = self.evaluateStack( s )
            op1 = self.evaluateStack( s )
            return self.opn[op]( op1, op2 )
        elif op == "PI":
            return math.pi # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op]( self.evaluateStack( s ) )
        elif op[0].isalpha():
            return 0
        else:
            return float( op )
    def eval(self,num_string,parseAll=True):
        self.exprStack=[]
        results=self.bnf.parseString(num_string,parseAll)
        val=self.evaluateStack( self.exprStack[:] )
        return val
