from fbs_runtime.application_context.PyQt5 import ApplicationContext
from BanglaVoiceCalculator import *
from base import *
import sys

if __name__ == '__main__':
    window = MainWindow()
    window.show()
    exit_code = appContext.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)