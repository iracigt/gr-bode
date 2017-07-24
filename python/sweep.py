#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from PyQt4 import Qt, QtCore, QtGui
from gnuradio.qtgui import Range

import logging
import threading

# https://gist.github.com/cypreess/5481681
class PeriodicThread(object):
    """
    Python periodic Thread using Timer with instant cancellation
    """

    def __init__(self, callback=None, period=1, name=None, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.period = period
        self.stop = False
        self.current_timer = None
        self.schedule_lock = threading.Lock()

    def start(self):
        """
        Mimics Thread standard start method
        """
        self.schedule_timer()

    def run(self):
        """
        By default run callback. Override it if you want to use inheritance
        """
        if self.callback is not None:
            self.callback(*self.args, **self.kwargs)

    def _run(self):
        """
        Run desired callback and then reschedule Timer (if thread is not stopped)
        """
        try:
            self.run()
        except Exception, e:
            print e
        finally:
            with self.schedule_lock:
                if not self.stop:
                    self.schedule_timer()

    def schedule_timer(self):
        """
        Schedules next Timer run
        """
        self.current_timer = threading.Timer(self.period, self._run)
        if self.name:
            self.current_timer.name = self.name
        self.current_timer.start()

    def cancel(self):
        """
        Mimics Timer standard cancel method
        """
        with self.schedule_lock:
            self.stop = True
            if self.current_timer is not None:
                self.current_timer.cancel()

    def join(self):
        """
        Mimics Thread standard join method
        """
        self.current_timer.join()




class SweepWidget(QtGui.QWidget):
    def __init__(self, ranges, slot, label, deltaT, rangeType=float):
        """ Creates the QT Sweep widget """
        QtGui.QWidget.__init__(self)

        self.range = ranges
        self.deltaT = deltaT

        # rangeType tells the block how to return the value as a standard
        self.rangeType = rangeType

        # Top-block function to call when any value changes
        # Some widgets call this directly when their value changes.
        # Others have intermediate functions to map the value into the right range.
        self.notifyChanged = slot

        layout = Qt.QHBoxLayout()
        label = Qt.QLabel(label)
        layout.addWidget(label)

        self.d_widget = self.Slider(self, self.range, self.notifyChanged, self.deltaT, rangeType)

        layout.addWidget(self.d_widget)
        self.setLayout(layout)

    class Slider(QtGui.QSlider):
        """ Creates the range using a slider """
        def __init__(self, parent, ranges, slot, deltaT, rangeType=float):
            QtGui.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)

            self.rangeType = rangeType

            # Setup the slider
            #self.setFocusPolicy(QtCore.Qt.NoFocus)
            self.setRange(0, ranges.nsteps - 1)
            self.setTickPosition(2)
            self.setSingleStep(1)
            self.range = ranges

            self.deltaT = deltaT

            # Round the initial value to the closest tick
            temp = int(round(ranges.demap_range(ranges.default), 0))
            self.setValue(temp)

            if ranges.nsteps > ranges.min_length:
                interval = int(ranges.nsteps/ranges.min_length)
                self.setTickInterval(interval)
                self.setPageStep(interval)
            else:
                self.setTickInterval(1)
                self.setPageStep(1)

            # Setup the handler function
            self.valueChanged.connect(self.changed)
            self.notifyChanged = slot

            # Setup the Timer

            def inc(sweep):
                new = sweep.value() + 1
                if (new <= sweep.maximum()):
                    sweep.setValue(new)
                    # QtGui.QSlider.repaint(sweep)
                else:
                    sweep.thread.cancel()

            self.thread = PeriodicThread(inc, self.deltaT, "Sweep", self)
            self.thread.start()


        def changed(self, value):
            """ Handle the valueChanged signal and map the value into the correct range """
            val = self.range.map_range(value)
            self.notifyChanged(self.rangeType(val))

        def mousePressEvent(self, event):
            # if((event.button() == QtCore.Qt.LeftButton)):
            #     new = self.minimum() + ((self.maximum()-self.minimum()) * event.x()) / self.width()
            #     self.setValue(new)
            #     event.accept()
            # # Use repaint rather than calling the super mousePressEvent.
            # # Calling super causes issue where slider jumps to wrong value.
            # QtGui.QSlider.repaint(self)
            pass

        def mouseMoveEvent(self, event):
            # new = self.minimum() + ((self.maximum()-self.minimum()) * event.x()) / self.width()
            # self.setValue(new)
            # event.accept()
            # QtGui.QSlider.repaint(self)
            pass
