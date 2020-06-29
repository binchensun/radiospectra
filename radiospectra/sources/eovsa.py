# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from astropy.io import fits
from astropy.time import Time
import os
import datetime

import numpy as np

from radiospectra.spectrogram import REFERENCE, LinearTimeSpectrogram
from radiospectra.util import get_day, ConditionalDispatch

__all__ = ['EOVSASpectrogram']


class EOVSASpectrogram(LinearTimeSpectrogram):
    _create = ConditionalDispatch.from_existing(LinearTimeSpectrogram._create)
    create = classmethod(_create.wrapper())
    COPY_PROPERTIES = LinearTimeSpectrogram.COPY_PROPERTIES + [
        ('bg', REFERENCE)
    ]

    @staticmethod
    def swavesfile_to_date(filename):
        _, name = os.path.split(filename)
        date = name.split('_')[2]
        return datetime.datetime(
            int(date[0:4]), int(date[4:6]), int(date[6:])
        )

    @classmethod
    def read(cls, filename, **kwargs):
        """
        Read in FITS file and return a new SWavesSpectrogram.
        """
        fl = fits.open(filename, **kwargs)
        data = fl[0].data
        freq_axis = fl[1].data.sfreq
        tdata = fl[2].data
        mjd = tdata.mjd
        sec = tdata.time / 1000.
        start = Time(mjd[0] + sec[0] / 86400., format='mjd').datetime
        end = Time(mjd[-1] + sec[-1] / 86400., format='mjd').datetime
        time_axis = sec - sec[0]
        header = fl[0].header
        t_delt = 1.0
        t_init = (start - get_day(start)).seconds
        #content = 'EOVSA Total Power Spectrogram'
        t_label = 'Time [UT]'
        f_label = 'Frequency [GHz]'
        #reverse the frequency axis
        freq_axis = freq_axis[::-1]
        data = data[::-1, :]

        return cls(data, time_axis, freq_axis, start, end, t_init, t_delt,
                   t_label, f_label, content)

    def __init__(self, data, time_axis, freq_axis, start, end,
                 t_init, t_delt, t_label, f_label, content):
        # Because of how object creation works, there is no avoiding
        # unused arguments in this case.
        # pylint: disable=W0613

        super(EOVSASpectrogram, self).__init__(
            data, time_axis, freq_axis, start, end,
            t_init, t_delt, t_label, f_label,
            content, set(["EOVSA"])
        )
        #self.bg = bg


try:
    EOVSASpectrogram.create.im_func.__doc__ = (
        """ Create EOVSASpectrogram from given input dispatching to the
        appropriate from_* function.

    Possible signatures:

    """ + EOVSASpectrogram._create.generate_docs())
except AttributeError:
    EOVSASpectrogram.create.__func__.__doc__ = (
        """ Create EOVSASpectrogram from given input dispatching to the
        appropriate from_* function.

    Possible signatures:

    """ + EOVSASpectrogram._create.generate_docs())

if __name__ == "__main__":
    opn = EOVSASpectrogram.read("/Users/binchen/Dropbox/EOVSA/spectrasoftware/EOVSA_TPall_20200626.fts")
    opn.plot(min_=0, linear=False).show()
    print("Press return to exit")
