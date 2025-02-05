import unittest
from tests.libreVNA import libreVNA as libreVNA
import tests.definitions as defs
import subprocess
import time
import select
from signal import SIGINT

class TestBase(unittest.TestCase):
    def setUp(self):
        self.gui = subprocess.Popen([defs.GUI_PATH, '-p', '19544'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # wait for the SCPI server to become available
        timeout = time.time() + 3;
        poll_obj = select.poll()
        poll_obj.register(self.gui.stdout, select.POLLIN)
        while time.time() < timeout:
            poll_result = poll_obj.poll(0)
            if poll_result:
                line = self.gui.stdout.readline().decode().strip()
                if "Listening on port 19544" in line:
                    break
       
        time.sleep(0.2)
        
        self.vna = libreVNA('localhost', 19544)
        try:
            self.vna.cmd(":DEV:CONN")
        except Exception as e:
            self.tearDown()
            raise e
        if self.vna.query(":DEV:CONN?") == "Not connected":
            self.tearDown()
            raise AssertionError("Not connected")
               
    def tearDown(self):
        self.gui.send_signal(SIGINT)
        try:
            self.gui.wait(timeout = 0.1)
        except subprocess.TimeoutExpired:
            self.gui.kill()
            
        