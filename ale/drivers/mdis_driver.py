from glob import glob
import os

import pvl
import spiceypy as spice
import numpy as np

from ale import config
from ale.drivers.base import Framer, TransverseDistortion, Spice, PDS3, Isis3

class MdisSpice(Spice, Framer, TransverseDistortion):
    id_lookup = {
        'MDIS-WAC': 'MSGR_MDIS_WAC',
        'MDIS-NAC':'MSGR_MDIS_NAC',
        'MERCURY DUAL IMAGING SYSTEM NARROW ANGLE CAMERA':'MSGR_MDIS_NAC',
        'MERCURY DUAL IMAGING SYSTEM WIDE ANGLE CAMERA':'MSGR_MDIS_WAC'
    }

    @property
    def metakernel(self):
        metakernel_dir = config.mdis
        mks = sorted(glob(os.path.join(metakernel_dir,'*.tm')))
        if not hasattr(self, '_metakernel'):
            for mk in mks:
                if str(self.start_time.year) in os.path.basename(mk):
                    self._metakernel = mk
        return self._metakernel

    @property
    def focal_length(self):
        """
        """
        coeffs = spice.gdpool('INS{}_FL_TEMP_COEFFS '.format(self.fikid), 0, 5)

        # reverse coeffs, mdis coeffs are listed a_0, a_1, a_2 ... a_n where
        # numpy wants them a_n, a_n-1, a_n-2 ... a_0
        f_t = np.poly1d(coeffs[::-1])

        # eval at the focal_plane_tempature
        return f_t(self.focal_plane_tempature)

    @property
    def focal_epsilon(self):
        return float(spice.gdpool('INS{}_FL_UNCERTAINTY'.format(self.ikid), 0, 1)[0])

    @property
    def starting_detector_sample(self):
        return int(spice.gdpool('INS{}_FPUBIN_START_SAMPLE'.format(self.ikid), 0, 1)[0])

    @property
    def starting_detector_line(self):
        return int(spice.gdpool('INS{}_FPUBIN_START_LINE'.format(self.ikid), 0, 1)[0])


class MdisPDS3Driver(PDS3, MdisSpice):
    @property
    def instrument_id(self):
        return self.id_lookup[self._label['INSTRUMENT_ID']]

    @property
    def focal_plane_tempature(self):
        return self._label['FOCAL_PLANE_TEMPERATURE'].value


class MdisIsis3Driver(Isis3, MdisSpice):
    @property
    def metakernel(self):
        metakernel_dir = config.mdis
        mks = sorted(glob(os.path.join(metakernel_dir,'*.tm')))
        if not hasattr(self, '_metakernel'):
            for mk in mks:
                if str(self.start_time.year) in os.path.basename(mk):
                    self._metakernel = mk
        return self._metakernel

    @property
    def instrument_id(self):
        return self.id_lookup[self._label['IsisCube']['Instrument']['InstrumentId']]

    @property
    def focal_plane_tempature(self):
        return self._label['IsisCube']['Instrument']['FocalPlaneTemperature'].value
