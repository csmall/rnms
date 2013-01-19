# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
import mock
from nose.tools import eq_, raises, assert_true, assert_false

from rnms import model
from rnms.tests.models import ModelTest

test_attribute_type = mock.MagicMock(spec=model.AttributeType)
test_attribute_type.rra_cf = mock.Mock(return_value='AVERAGE')

test_attribute = mock.MagicMock(spec=model.Attribute)
test_attribute.attribute_type = test_attribute_type

test_def = model.GraphTypeDef(None, 'input', None)

test_vdef = model.GraphTypeVname()
test_vdef.def_type = 1
test_vdef.name = 'vinput'

test_cdef = model.GraphTypeVname()
test_cdef.def_type = 0
test_cdef.name = 'cinput'

test_epoch = 55689300.0
test_epoch_str = str(test_epoch)
test_color = 'aa00ff'

class TestGraphTypeVname(ModelTest):
    """ Unit test case for the ``GraphTypeVname`` model. """
    klass = model.GraphTypeVname

    def test_def_type_name(self):
        """ Valid def_types return correct names """
        for id,name in ((0, 'CDEF'), (1, 'VDEF')):
            self.obj.def_type = id
            eq_(self.obj.def_type_name, name)

    @raises(model.GraphTypeError)
    def test_def_type_low(self):
        """ def_type -1 raises a GraphTypeError """
        self.obj.def_type = -1
        dummy = self.obj.def_type_name
    
    @raises(model.GraphTypeError)
    def test_def_type_hight(self):
        """ def_type 2 raises a GraphTypeError """
        self.obj.def_type = 2
        dummy = self.obj.def_type_name

    def test_cdef_format(self):
        """ CDEF produces correct output """
        self.obj.set_cdef('vinput','bytes,8,*')
        eq_(self.obj.format(test_attribute), 'CDEF:vinput=bytes,8,*')

    def test_vdef_format(self):
        """ VDEF produces correct output """
        self.obj.set_vdef('vinput','bytes,8,*')
        eq_(self.obj.format(test_attribute), 'VDEF:vinput=bytes,8,*')

class TestGraphLine(ModelTest):
    """Unit test case for the ``GraphTypeLine`` model."""
    klass = model.GraphTypeLine

    def test_print_output(self):
        """ PRINT object returns expected output """
        self.obj.set_print(test_vdef, 'Value: %8.2lf')
        eq_(self.obj.format(test_attribute), 'PRINT:vinput:Value\: %8.2lf')

    @raises(model.GraphTypeLineError)
    def test_print_bad_cdef(self):
        """ PRINT object raises error using CDEF """
        self.obj.set_print(test_cdef, 'Value: %8.2lf')
        #eq_(self.obj.format(test_attribute), 'PRINT:vinput:Value\: %8.2lf')

    def test_gprint_output(self):
        """ GPRINT object returns expected output """
        self.obj.set_gprint(test_vdef, 'Value: %8.2lf')
        eq_(self.obj.format(test_attribute), 'GPRINT:vinput:Value\: %8.2lf')

    @raises(model.GraphTypeLineError)
    def test_gprint_bad_cdef(self):
        """ GPRINT object raises error using CDEF """
        self.obj.set_gprint(test_cdef, 'Value: %8.2lf')
    
    def test_comment_output(self):
        """ COMMENT object returns expected output """
        self.obj.set_comment('This is a comment: hello')
        eq_(self.obj.format(test_attribute), r'COMMENT:This is a comment\: hello')
 
    def test_vrule_value(self):
        """ VRULE using value returns expected output """
        self.obj.set_vrule(None, test_epoch, test_color, 'A: legend')
        eq_(self.obj.format(test_attribute), 'VRULE:{}#{}:A\\: legend'.format(test_epoch, test_color))

    @raises(model.GraphTypeLineError)
    def test_vrule_badepoch(self):
        """ VRULE raises exception on bad time epoch """
        self.obj.set_vrule(None, 'yesterday', test_color, 'A: legend')

    @raises(model.GraphTypeLineError)
    def test_vrule_badcolor(self):
        """ VRULE raises exception on bad color """
        self.obj.set_vrule(None, test_epoch, 'hello', 'A: legend')

    def test_vrule_vdef(self):
        """ VRULE using VDEF returns expected output """
        self.obj.set_vrule(test_vdef, None, test_color, 'A: legend')
        eq_(self.obj.format(test_attribute), 'VRULE:vinput#{}:A\\: legend'.format(test_color))
    
    @raises(model.GraphTypeLineError)
    def test_vrule_cdef(self):
        """ VRULE using CDEF raises exception """
        self.obj.set_vrule(test_cdef, None, test_color, 'A: legend')
    
    @raises(model.GraphTypeLineError)
    def test_vrule_def(self):
        """ VRULE using CDEF raises exception """
        self.obj.set_vrule(test_cdef, None, test_color, 'A: legend')
    
    @raises(model.GraphTypeLineError)
    def test_vrule_vdef_value(self):
        """ VRULE using VDEF and value raises exception """
        self.obj.set_vrule(test_vdef, test_epoch, test_color, 'A: legend')
    
    ##### HRULE
    def test_hrule_ok(self):
        """ HRULE provides expected output """
        self.obj.set_hrule('42.0', test_color, 'A: legend')
        eq_(self.obj.format(test_attribute), 'HRULE:42.0#{}:A\\: legend'.format(test_color))

    @raises(model.GraphTypeLineError)
    def test_hrule_bad_color(self):
        """ HRULE with bad color raises exception """
        self.obj.set_hrule(123, 'yellow', 'A: legend')
    
    # Lines
    def test_line_def(self):
        """ LINE with DEF produces output """
        self.obj.set_line(test_def, test_color, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'LINE2:input#{}:A\\: legend'.format(test_color))
    
    def test_line_cdef(self):
        """ LINE with CDEF produces output """
        self.obj.set_line(test_cdef, test_color, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'LINE2:cinput#{}:A\\: legend'.format(test_color))

    def test_line_vdef(self):
        """ LINE with VDEF produces output """
        self.obj.set_line(test_vdef, test_color, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'LINE2:vinput#{}:A\\: legend'.format(test_color))
    
    def test_line_width(self):
        """ LINE with DEF and width produces output """
        self.obj.set_line(test_def, test_color, width=3.5, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'LINE3.5:input#{}:A\\: legend'.format(test_color))
    def test_line_nolegend(self):
        """ LINE with DEF and no legend produces correct output """
        self.obj.set_line(test_def, test_color)
        eq_(self.obj.format(test_attribute), 'LINE2:input#{}'.format(test_color))
    
    def test_line_nocolor(self):
        """ LINE with DEF and no color produces correct output """
        self.obj.set_line(test_def)
        eq_(self.obj.format(test_attribute), 'LINE2:input')
    
    def test_line_legend_stack(self):
        """ LINE with DEF and legend and stack produces correct output """
        self.obj.set_line(test_def, test_color, legend='A: legend', stack=True)
        eq_(self.obj.format(test_attribute), 'LINE2:input#{}:A\\: legend:STACK'.format(test_color))
    
    def test_line_stack(self):
        """ LINE with DEF and stack produces correct output """
        self.obj.set_line(test_def, test_color, stack=True)
        eq_(self.obj.format(test_attribute), 'LINE2:input#{}::STACK'.format(test_color))
    
    @raises(model.GraphTypeLineError)
    def test_line_nocolor_legend(self):
        """ LINE with DEF and no color with legend raises error """
        self.obj.set_line(test_def, legend='A: legend')

    @raises(model.GraphTypeLineError)
    def test_line_bad_color(self):
        """ LINE with bad color raises exception """
        self.obj.set_line(test_def, 'yellow')

    @raises(model.GraphTypeLineError)
    def test_line_bad_width(self):
        """ LINE with bad width raises exception """
        self.obj.set_line(test_def, width='wide')

    ### AREA
    def test_area_def(self):
        """ AREA with DEF produces output """
        self.obj.set_area(test_def, test_color, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'AREA:input#{}:A\\: legend'.format(test_color))
    
    def test_area_cdef(self):
        """ AREA with CDEF produces output """
        self.obj.set_area(test_cdef, test_color, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'AREA:cinput#{}:A\\: legend'.format(test_color))

    def test_area_vdef(self):
        """ AREA with VDEF produces output """
        self.obj.set_area(test_vdef, test_color, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'AREA:vinput#{}:A\\: legend'.format(test_color))
    
    def test_area_nolegend(self):
        """ AREA with DEF and no legend produces correct output """
        self.obj.set_area(test_def, test_color)
        eq_(self.obj.format(test_attribute), 'AREA:input#{}'.format(test_color))
    
    def test_area_nocolor(self):
        """ AREA with DEF and no color produces correct output """
        self.obj.set_area(test_def)
        eq_(self.obj.format(test_attribute), 'AREA:input')
    
    def test_area_legend_stack(self):
        """ AREA with DEF and legend and stack produces correct output """
        self.obj.set_area(test_def, test_color, legend='A: legend', stack=True)
        eq_(self.obj.format(test_attribute), 'AREA:input#{}:A\\: legend:STACK'.format(test_color))
    
    def test_area_stack(self):
        """ AREA with DEF and stack produces correct output """
        self.obj.set_area(test_def, test_color, stack=True)
        eq_(self.obj.format(test_attribute), 'AREA:input#{}::STACK'.format(test_color))
    
    @raises(model.GraphTypeLineError)
    def test_area_nocolor_legend(self):
        """ AREA with DEF and no color with legend raises error """
        self.obj.set_area(test_def, legend='A: legend')

    @raises(model.GraphTypeLineError)
    def test_area_bad_color(self):
        """ AREA with bad color raises exception """
        self.obj.set_area(test_def, 'yellow')

    # TICK
    def test_tick_def(self):
        """ TICK with DEF produces output """
        self.obj.set_tick(test_def, test_color)
        eq_(self.obj.format(test_attribute), 'TICK:input#{}'.format(test_color))
    
    def test_tick_vdef(self):
        """ TICK with VDEF produces output """
        self.obj.set_tick(test_vdef, test_color)
        eq_(self.obj.format(test_attribute), 'TICK:vinput#{}'.format(test_color))

    def test_tick_cdef(self):
        """ TICK with CDEF produces output """
        self.obj.set_tick(test_cdef, test_color)
        eq_(self.obj.format(test_attribute), 'TICK:cinput#{}'.format(test_color))

    def test_tick_alpha(self):
        """ TICK with DEF and color with alpha produces output """
        self.obj.set_tick(test_def, '00ffaaf0')
        eq_(self.obj.format(test_attribute), 'TICK:input#00ffaaf0')
    
    def test_tick_legend(self):
        """ TICK with legend and fraction produces output """
        self.obj.set_tick(test_def, test_color, fraction=0.2, legend='A: legend')
        eq_(self.obj.format(test_attribute), 'TICK:input#{}:0.2:A\\: legend'.format(test_color))
    
    @raises(model.GraphTypeLineError)
    def test_tick_bad_color(self):
        """ TICK with bad color raises exception """
        self.obj.set_tick(test_def, 'yellow')
    
    @raises(model.GraphTypeLineError)
    def test_tick_bad_alpha(self):
        """ TICK with bad color raises exception """
        self.obj.set_tick(test_def, '00ffaa5')
    
    @raises(model.GraphTypeLineError)
    def test_tick_bad_fraction(self):
        """ TICK with bad fraction raises exception """
        self.obj.set_tick(test_def, test_color, fraction='half')
    
    @raises(model.GraphTypeLineError)
    def test_tick_big_fraction(self):
        """ TICK with fraction over 100 raises exception """
        self.obj.set_tick(test_def, test_color, fraction='100.1')
    
    @raises(model.GraphTypeLineError)
    def test_tick_legend_no_fraction(self):
        """ TICK with no fraction but with legend raises exception """
        self.obj.set_tick(test_def, test_color, legend='A: legend')
