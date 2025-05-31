from PyQt5.QtCore import QObject, pyqtSignal

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(str, float)
    error = pyqtSignal(str)