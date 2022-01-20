import dataclasses
import colour
import logging
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Patch:
    _name: str
    _spectral_distribution: list
    _xyz: list = dataclasses.field(default_factory=list)
    _rgb: list = dataclasses.field(default_factory=list)

    #=================================#
    # Set / Get
    #=================================#
    def name(self):
        return self._name

    # xyz
    def set_xyz(self, xyz):
        self._xyz = xyz

    def xyz(self):
        return self._xyz

    # rgb
    def set_rgb(self, rgb):
        self._rgb = rgb

    def rgb(self):
        return self._rgb

    def srgb(self):
        return colour.XYZ_to_sRGB(self.xyz())

    def xyY(self):
        return colour.XYZ_to_xyY(self.xyz())
    #=================================#
    # Method
    #=================================#
    def calc_xyz(self, cmfs, min_sd, max_sd, steps):
        result = colour.sd_to_XYZ(
            self._spectral_distribution,
            cmfs,
            method='Integration',
            shape=colour.SpectralShape(min_sd, max_sd, steps)
        )

        return result/100.0

    def render(self, cmfs, illuminant, shape):
        result = colour.sd_to_XYZ(
            self._spectral_distribution,
            cmfs,
            illuminant,
            shape=colour.SpectralShape(shape[0], shape[1], shape[2])
        )

        return result/100.0

@dataclasses.dataclass
class Checker:
    _name: str = dataclasses.field(init=False)
    _patches: dict = dataclasses.field(init=False)
    _cmfs: list = None
    _illuminant: list = None
    _illuminant_name: str = None

    def __init__(self, name, sds):
        logger.info('Init Chekcer data')
        logger.info(f'name = {name}')

        self._patches = {}

        self.set_name(name)
        self.set_sds(sds)

    #=================================#
    # Set / Get
    #=================================#
    def get(self):
        #  reference = colour.CCS_COLOURCHECKERS['ColorChecker24 - After November 2014']

        name = self.full_name()
        il_name = self.illuminant_name()
        patches = self.xyY()

        # il = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer'][il_name]           
        il = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65']           

        result = colour.characterisation.ColourChecker(
            name,
            patches,
            il
        )

        return result

    # Name
    def set_name(self, name):
        self._name = name

    def name(self):
        return self._name

    def full_name(self):
        name = self.name()
        ilm_name = self.illuminant_name()

        result = f'ColorChecker24 - {name}({ilm_name})'
        return result

    # Pathces
    def set_sds(self, sds):
        for name in sds:
            logger.info(name)
            sd = sds.get(name)
            patch = Patch(name, sd)

            self.set_patch(name, patch)

    # patch
    def set_patch(self, name, path):
        self._patches[name] = path

    # cmf
    def set_cmfs(self, cmfs):
        self._cmfs = cmfs

    def cmfs(self):
        return self._cmfs

    # illuminant
    def set_illuminant(self, ilm):
        self._illuminant = ilm

    def illuminant(self):
        return self._illuminant
    
    # illuminant_name
    def set_illuminant_name(self, name):
        self._illuminant_name = name

    def illuminant_name(self):
        return self._illuminant_name

    # xyz
    def xyz(self):
        result = { name: self._patches[name].xyz() for name in self._patches }
        return result

    def rgb(self):
        result = { name: np.array(self._patches[name].rgb()) for name in self._patches }
        return result

    def srgb(self):
        result = { name: np.array(self._patches[name].srgb()) for name in self._patches }
        return result

    def xyY(self):
        result = { name: np.array(self._patches[name].xyY()) for name in self._patches }
        return result

    #=================================#
    # Methods
    #=================================#
    def update_xyz(self, min_sd, max_sd, steps):
        cmfs = self.cmfs()

        for name in self._patches:
            patch = self._patches.get(name)

            xyz = patch.calc_xyz(
                cmfs, min_sd, max_sd, steps)

            patch.set_xyz(xyz)

    def render(self, shape):
        cmfs = self.cmfs()
        ilm = self.illuminant()

        for name in self._patches:
            patch = self._patches.get(name)

            xyz = patch.render( cmfs, ilm , shape)

            patch.set_xyz(xyz)

    def convert(self, name):
        m = colour.RGB_COLOURSPACES[name].matrix_XYZ_to_RGB

        for name in self._patches:
            patch = self._patches.get(name)

            xyz = patch.xyz()

            rgb = m@xyz
            patch.set_rgb(rgb)

    def show(self):
        pprint(self._patches)

class TyColorChecker_v1:
    script_updated = 'JAN 20 2021'
    script_version = 'v1.0.0'
    script_name = 'TyColorChecker'
    script_coding = 'Tatsuya YAMAGISHI'
    script_tool_version = 'Python 3.7.9'
    script_created = 'JAN 20 2021'

    #=================================#
    # Init
    #=================================#
    def __init__(self, logger):
        self.init_logger()

        logger.info('Init')

        self._checker = None
        self._shape = None

    def init_logger(self):
        logger.propagate = False

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter(
            '[%(levelname)s][%(asctime)s][%(name)s][%(filename)s][%(funcName)s:%(lineno)s] %(message)s')
        )
        logger.addHandler(stream_handler)
        
        return logger

    #=================================#
    # Set / Get
    #=================================#
    def set(self, name):
        logger.info(f'Checker = {name}')
        if not name in self.chekcer_names():
            logger.warning(f'"{name}" is not found.')
        else:
            logger.info('> Set Checker data.')
            sds = colour.characterisation.SDS_COLOURCHECKERS.get(name)

            checker = Checker(name, sds)
            self.set_checker(checker)

    def get(self):
        return self._checker

    def set_checker(self, checker):
        self._checker = checker

    def checker(self):
        return self._checker.get()

    # cmf
    def set_cmf(self, name):
        logger.info('> Set CMF')
        logger.info(f'{name}')

        if not name in self.cmf_names():
            logger.warning(f'"{name}" is not found.')
        else:
            logger.info('> Set CMF data.')
            cmfs = colour.MSDS_CMFS.get(name)
            self._checker.set_cmfs(cmfs)
            self._checker.update_xyz(
                self._shape[0],
                self._shape[1],
                self._shape[2],
            )
    
    def cmf(self):
        return self._checker.cmf()

    # illuminant
    def set_illuminant(self, name):
        logger.info('> Set Illuminant')
        logger.info(f'{name}')

        if not name in self.illuminant_names():
            logger.warning(f'"{name}" is not found.')
        else:
            illuminant = colour.SDS_ILLUMINANTS.get(name)
            self._checker.set_illuminant(illuminant)
            self._checker.set_illuminant_name(name)

    def illuminant(self):
        return self._checker.illuminant()

    def xyz(self):
        return self._checker.xyz()

    def rgb(self):
        return self._checker.rgb()

    def set_shape(self, shape):
        self._shape = shape

    def shape(self):
        return self._shape

    # スペクトルデータを持つチェッカー名リスト取得
    def chekcer_names(self):
        return sorted(colour.characterisation.SDS_COLOURCHECKERS.keys())
    
    def cmf_names(self):
        return sorted(colour.MSDS_CMFS.keys())

    def illuminant_names(self):
        return sorted(colour.SDS_ILLUMINANTS.keys())

    def colorspace_names(self):
        return sorted(colour.RGB_COLOURSPACES.keys())

    #=================================#
    # Methods
    #=================================#
    def render(self):
        shape = self.shape()
        self._checker.render(shape)

    def convert(self, name):
        self._checker.convert(name)
    #=================================#
    # Show
    #=================================#
    def show_checkers(self):
        logger.info('> Show Checkers')
        result = self.chekcer_names()
        pprint(result)

    def show_cmfs(self):
        logger.info('> Show CMFS')
        result = self.cmf_names()
        pprint(result)

    def show_illuminants(self):
        logger.info('> Show Illuminants')
        result = self.illuminant_names()
        print(result)

    def show_colorspaces(self):
        logger.info('> Show colorspaces')
        result = self.colorspace_names()
        print(result)

    def show_xyz(self):
        logger.info('> Show XYZ')
        result = self.xyz()
        pprint(result)

    def show_rgb(self):
        logger.info('> Show RGB')
        result = self.rgb()
        pprint(result)
    #=================================#
    # Plot
    #=================================#
    def plot_cmf(self):
        logger.info('> Plot CMF')
        cmf = self.cmf()

        colour.plotting.colour_style()
        colour.plotting.plot_single_cmfs(
            cmf,
            bounding_box=(380, 780, 0.0, 2.0));

    def plot_illuminant(self):
        logger.info('> Plot Illuminant')

        ilm = self.illuminant()
        colour.plotting.colour_style()
        colour.plotting.plot_single_sd(ilm);

    def plot_checker(self, checker):
        logger.info('> Plot Checker')

        colour.plotting.colour_style()
        colour.plotting.plot_single_colour_checker(
            checker, text_parameters={'visible': False});

    def plot_mult_checker(self, cc1, cc2):
        logger.info('> Plot Mult Checker')

        colour.plotting.colour_style()
        colour.plotting.plot_multi_colour_checkers(
            [cc1.checker(), cc2.checker()]);

def main():
    logging.basicConfig(level = logging.INFO)

    cc = TyColorChecker_v1(logger)
    cc.set_shape((380, 780, 5))
    
    cc.show_checkers()
    cc.set('ISO 17321-1')
    # cc.show()

    cc.show_cmfs()
    cc.set_cmf('cie_2_1931')
    # cc.plot_cmf()
    cc.show_xyz()

    cc.show_illuminants()
    cc.set_illuminant('D65')
    # cc.set_illuminant('FL7')
    # cc.plot_illuminant()

    cc.render()

    # cc.show_colorspaces()
    cc.convert('sRGB')

    cc.show_rgb()
    
    # ref = colour.CCS_COLOURCHECKERS['ColorChecker24 - After November 2014']
    # pprint(ref)
    # cc.plot_checker(checker)

    cc2 = TyColorChecker_v1(logger)
    cc2.set_shape((380, 780, 5))
    cc2.set('ISO 17321-1')
    cc2.set_cmf('cie_2_1931')
    cc2.set_illuminant('FL7')
    cc2.render()

    cc.plot_mult_checker(cc, cc2)

if __name__ == '__main__':
    main()