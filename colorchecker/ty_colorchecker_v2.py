import colour
import dataclasses
import logging
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
import sys

from PySide2 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Material:
    _name: str
    _spectral_distribution: list
    _xyz: list = dataclasses.field(default_factory=list)
    _dif: list = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Checker:
    _name: str = dataclasses.field(init=False)
    _patches: dict = dataclasses.field(init=False)

    def __init__(self, name, sds):
        logger.info('> Init Chekcer data')
        logger.info(f'name = {name}')

        self._patches = {}

        self.set_name(name)
        self.set_patches(sds)

    #=================================#
    # Set / Get
    #=================================#
    # Name
    def set_name(self, name):
        self._name = name

    def name(self):
        return self._name

    def set_patches(self, sds):
        for name in sds:
            logger.info(name)
            sd = sds.get(name)
            patch = Material(name, sd)

            self.set_patch(name, patch)

    # patch
    def set_patch(self, name, path):
        self._patches[name] = path

@dataclasses.dataclass
class Scene:
    _cmfs: list = None
    _colorspace: str = None
    _chekcer: Checker = None
    _light: Material = None
    _width: int = 480
    _height: int = 320
    _default_color = QtGui.QColor('Blue')

    #=================================#
    # Set / Get
    #=================================#
    def set_colorspace(self, colorspace):
        self._colorspace = colorspace
    
    def colorspace(self):
        return self._colorspace

    def set_light(self, name, ilm):
        light = Material(name, ilm)
        self._light = light

    def set_cmfs(self, cmfs):
        self._cmfs = cmfs

    def set_checker(self, checker):
        self._checker = checker

    def width(self):
        return self._width

    def height(self):
        return self._height

    def size(self):
        return [self.width(), self.height()]

    def default_color(self):
        return self._default_color

class TyColorChecker_v2:
    script_updated = 'JAN 20 2021'
    script_version = 'v2.0.0'
    script_name = 'TyColorChecker'
    script_coding = 'Tatsuya YAMAGISHI'
    script_tool_version = 'Python 3.7.9'
    script_created = 'JAN 20 2021'

    #=================================#
    # Init
    #=================================#
    def __init__(self):
        self.init_logger()
        logger.info('> Init ColorChecker')

        self._scene = Scene()

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
    def size(self):
        return self._scene.size()

    def default_color(self):
        return self._scene.default_color()

    def set_colorspace(self, name):
        logger.info(f'> Set Colorspace = {name}')
        self._scene.set_colorspace(name)

    def set_illuminant(self, name):
        logger.info(f'> Set Light = {name}')
        ilm = colour.SDS_ILLUMINANTS.get(name)
        self._scene.set_light(name, ilm)

    def set_cmfs(self, name):
        logger.info(f'> Set CMFs = {name}')
        cmfs = colour.MSDS_CMFS.get(name)
        self._scene.set_cmfs(cmfs)

    def set_checker(self, name):
        logger.info(f'> Set Checker = {name}')
        sds = colour.characterisation.SDS_COLOURCHECKERS.get(name)
        checker = Checker(name, sds)
        self._scene.set_checker(checker)

    #=================================#
    # Name List
    #=================================#
    def colorspaces(self):
        return sorted(colour.RGB_COLOURSPACES.keys())
    
    def illuminants(self):
        return sorted(colour.SDS_ILLUMINANTS.keys())

    def cmfs(self):
        return sorted(colour.MSDS_CMFS.keys())

    def checkers(self):
        return sorted(colour.characterisation.SDS_COLOURCHECKERS.keys())
    
    #=================================#
    # Methods
    #=================================#
    def render(self):
        logger.info(f'> Rendering')
        # self._scene.render()

    #=================================#
    # Show
    #=================================#
    def show_colorspace(self, name):
        style = {
        # Figure Size Settings
        'figure.figsize': (8.0, 7.0)
        }

        if name == 'Spectrum':
            name = ''
    
        colour.plotting.colour_style()
        plt.style.use(style)
        colour.plotting.plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931(name);
######################################################
# View
######################################################
class ComboBoxWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)

        self.label = QtWidgets.QLabel('Label')
        self.label.setMinimumWidth(80)
        layout.addWidget(self.label)

        self.combobox = QtWidgets.QComboBox()
        self.combobox.setMinimumWidth(260)
        layout.addWidget(self.combobox)

        self.button = QtWidgets.QPushButton('Show')
        self.button.setFixedWidth(50)
        layout.addWidget(self.button)

    #=================================#
    # Set / Get
    #=================================#
    def set(self, name):
        num = self.combobox.findText(name)
        if num:
            self.combobox.setCurrentIndex(num)

    def get(self):
        return self.combobox.currentText()

    def set_label(self, text):
        self.label.setText(text)

    #=================================#
    # Methods
    #=================================#
    def clear(self):
        self.combobox.clear()

    def addItems(self, items):
        self.combobox.addItems(items)

class MenuWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        h = 50

        self.colorspace = ComboBoxWidget()
        self.colorspace.set_label('Colorspace:')
        self.colorspace.setMaximumHeight(h)
        layout.addWidget(self.colorspace)

        self.ilm = ComboBoxWidget()
        self.ilm.set_label('Illuminat:')
        self.ilm.setMaximumHeight(h)
        layout.addWidget(self.ilm)

        self.cmfs = ComboBoxWidget()
        self.cmfs.set_label('CMFs:')
        self.cmfs.setMaximumHeight(h)
        layout.addWidget(self.cmfs)

        self.checker = ComboBoxWidget()
        self.checker.set_label('ColorChecker:')
        self.checker.setMaximumHeight(h)
        layout.addWidget(self.checker)

        self.render_button = QtWidgets.QPushButton('Render')
        self.render_button.setMinimumHeight(50)
        font = QtGui.QFont()
        font.setFamily('Arial Black')
        font.setPointSize(11)
        self.render_button.setFont(font)

        layout.addWidget(self.render_button)

class RenderView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._image = None
        self._pixmap = None

        layout = QtWidgets.QVBoxLayout(self)

        self.view = QtWidgets.QLabel()
        layout.addWidget(self.view)

    #=================================#
    # Set / Get
    #=================================#
    def set_image(self, image):
        self._image = image
        self.set_pixmap(self._image)

    def set_pixmap(self, image):
        pixmap = QtGui.QPixmap(image)
        self.view.setPixmap(pixmap)

class View(QtWidgets.QMainWindow):
    def __init__(self, Core, parent=None):
        super().__init__(parent)

        self.core = Core

        self.init()
        self.setup()

        self.resize(960, 480)

    #=================================#
    # init
    #=================================#
    def init(self):
        self.init_menubar()
        self.init_central_widget()
        self.init_statusbar()
        self.init_signals()
        
        self.update_title()

    def init_menubar(self):
        logger.info('> Gui: init_menubar')

        self.menu_bar = self.menuBar()
        
        # File
        self.menu_file = QtWidgets.QMenu('File', self)
        self.menu_bar.addAction(self.menu_file.menuAction())

        action = QtWidgets.QAction('Exit', self)
        action.setShortcut(QtGui.QKeySequence('Ctrl+Q'))
        action.triggered.connect(lambda: self.close())
        self.menu_file.addAction(action)

    def init_central_widget(self):
        logger.info('> Gui: init_central_widget')

        layout = QtWidgets.QHBoxLayout()
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.menu_widget = MenuWidget()
        layout.addWidget(self.menu_widget)

        self.render_widget = RenderView()
        layout.addWidget(self.render_widget)

        image = self.new_image()
        self.render_widget.set_image(image)

    def init_statusbar(self):
        logger.info('> Gui: init_statusbar')

        self.statusbar = self.statusBar()

    #=================================#
    # init signals
    #=================================#
    def init_signals(self):
        logger.info('> Init Signals')
        self.menu_widget.colorspace.button.clicked.connect(self.show_colorspace)

    #=================================#
    # Setup
    #=================================#
    def setup(self):
        # Colorspaces
        logger.info('> Setup Colorspace')
        ui = self.menu_widget.colorspace
        ui.clear()
        items = ['Spectrum']
        items.extend(self.core.colorspaces())
        ui.addItems(items)
        pprint(items)
        self.set_colorspace('Spectrum')

        # Illuminants
        logger.info('> Setup Illuminant')
        ui = self.menu_widget.ilm
        ui.clear()
        items = self.core.illuminants()
        ui.addItems(items)
        pprint(items)
        ui.set('D65')

        # CMFs
        logger.info('> Setup CMFs')
        ui = self.menu_widget.cmfs
        ui.clear()
        items = self.core.cmfs()
        ui.addItems(items)
        pprint(items)
        ui.set('CIE 1931 2 Degree Standard Observer')

        # Checker
        logger.info('> Checkers')
        ui = self.menu_widget.checker
        ui.clear()
        items = self.core.checkers()
        ui.addItems(items)
        pprint(items)
        ui.set('ISO 17321-1')

    #=================================#
    # Set / Get
    #=================================#
    def new_image(self):
        w, h = self.core.size()
        result = QtGui.QImage(w, h , QtGui.QImage.Format_RGB888)
        result.fill(self.core.default_color())
        return result

    def set_colorspace(self, name):
        self.menu_widget.colorspace.set(name)

    def colorspace(self):
        return self.menu_widget.colorspace.get()

    #=================================#
    # update
    #=================================#
    def update_title(self):
        result = f'{self.core.script_name} {self.core.script_version}'
        self.setWindowTitle(result)

    #=================================#
    # show
    #=================================#
    def show_colorspace(self):
        logger.info('> Show Colorspace')

        name = self.colorspace()
        logger.info(name)
        self.core.show_colorspace(name)
    

def debug():
    cc = TyColorChecker_v2()

    # ColorSpace
    colorspaces = cc.colorspaces()
    pprint(colorspaces)
    
    # Illuminant
    ilms = cc.illuminants()
    pprint(ilms)

    # CMFs
    cmfs = cc.cmfs()
    pprint(cmfs)

    # checker
    checkers = cc.checkers()
    pprint(checkers)

    cc.set_colorspace('sRGB')
    cc.set_illuminant('D65')
    cc.set_cmfs('cie_2_1931')
    cc.set_checker('ISO 17321-1')

    cc.render()

def main():
    app = QtWidgets.QApplication(sys.argv)
    core = TyColorChecker_v2()
    view = View(core)
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    
    # debug()
    main()