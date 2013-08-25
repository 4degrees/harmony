# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from .standard import Standard


class Simple(Standard):
    '''Simple widget that wraps a single control.'''

    def _construct(self):
        '''Construct widget.'''
        super(Simple, self)._construct()
        self._control = self._constructControl()
        self._headerLayout.insertWidget(1, self._control, stretch=1)

    def _constructControl(self):
        '''Return the control widget.

        Subclasses should override this to return an appropriate control
        widget.

        '''
        raise NotImplementedError()
