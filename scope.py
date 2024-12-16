import time
import pyvisa

class Oscilloscope:
    def __new__(cls, visa_resource_string):
        rm = pyvisa.ResourceManager()
        scope = rm.open_resource(visa_resource_string)
        idn = scope.query("*IDN?").strip().split(",")
        manufacturer = idn[0].strip().upper()
        if manufacturer == "TEKTRONIX":
            instance = super().__new__(TektronixOscilloscope)
        elif manufacturer == "ROHDE&SCHWARZ":
            instance = super().__new__(RohdeSchwarzOscilloscope)
        elif manufacturer == "KEYSIGHT TECHNOLOGIES":
            instance = super().__new__(KeysightOscilloscope)
        else:
            raise ValueError(f"Unsupported oscilloscope manufacturer: {manufacturer}")
        
        instance.scope = scope  # Store the scope instance
        instance.idn = idn  # Store the IDN for later use
        instance.manufacturer = manufacturer
        return instance

    def __init__(self, visa_resource_string):
        pass

    def set_labels(self, label1, label2, label3, label4):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def take_screenshot(self, filename):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def close(self):
        """Close the connection to the oscilloscope."""
        self.scope.close()

class TektronixOscilloscope(Oscilloscope):
    def set_labels(self, label1, label2, label3, label4):
        self.scope.write(f":CHAN1:LABEL \"{label1}\"")
        self.scope.write(f":CHAN2:LABEL \"{label2}\"")
        self.scope.write(f":CHAN3:LABEL \"{label3}\"")
        self.scope.write(f":CHAN4:LABEL \"{label4}\"")

    def take_screenshot(self, file_path):
        self.scope.write("HARDCOPY:FORMat PNG")
        self.scope.write("HARDCOPY:LAYout LAN")
        self.scope.write("HARDCOPY:PORT ETHERNET")
        self.scope.write("HARDCOPY Start")

        time.sleep(2)  # Wait for the hardcopy to complete
        
        byte_data = self.scope.read_raw()  # Read the screenshot data
        with open(file_path, 'wb') as f:
            f.write(byte_data)

class KeysightOscilloscope(Oscilloscope):
    def set_labels(self, label1, label2, label3, label4):
        self.scope.write(f":CHAN1:LABEL \"{label1}\"")
        self.scope.write(f":CHAN2:LABEL \"{label2}\"")
        self.scope.write(f":CHAN3:LABEL \"{label3}\"")
        self.scope.write(f":CHAN4:LABEL \"{label4}\"")

    def take_screenshot(self, file_path):
        self.scope.write(":DISPlay:DATA? BMP, SCReen")
        byte_data = self.scope.read_raw()  # Read the screenshot data
        with open(file_path, 'wb') as f:
            f.write(byte_data)

class RohdeSchwarzOscilloscope(Oscilloscope):
    def set_labels(self, label1, label2, label3, label4):
        if self.idn[1].strip() == "MXO54":
            self.scope.write(f"DISP:SIGN:LAB C1, \"{label1}\"")
            self.scope.write(f"DISP:SIGN:LAB C2, \"{label2}\"")
            self.scope.write(f"DISP:SIGN:LAB C3, \"{label3}\"")
            self.scope.write(f"DISP:SIGN:LAB C4, \"{label4}\"")
        else:
            self._set_label_for_rohde_schwarz(label1, label2, label3, label4)

    def _set_label_for_rohde_schwarz(self, label1, label2, label3, label4):
        self._set_single_label(label1, 'C1W1', 20)
        self._set_single_label(label2, 'C2W1', 40)
        self._set_single_label(label3, 'C3W1', 60)
        self._set_single_label(label4, 'C4W1', 80)

    def _set_single_label(self, label, channel, offset):
        if label:
            self.scope.write(f"DISP:SIGN:LAB:TEXT? 'Label1', {channel}")
            if self.scope.read_stb() == 4:  # There was an error
                self.scope.write(f"DISP:SIGN:LAB:ADD 'Label1', {channel}, '{label}', REL, 10, {offset}")
            else:  # No error
                self.scope.write(f"DISP:SIGN:LAB:TEXT 'Label1', {channel}, '{label}'")
        else:
            self.scope.write(f"DISP:SIGN:LAB:REM 'Label1', {channel}")

    def take_screenshot(self, file_path):
        self.scope.write("SYST:DISP:UPD ON")
        self.scope.write("STOP")
        self.scope.write("HCOP:DEST 'MMEM'")
        self.scope.write("HCOP:DEV:LANG PNG")
        
        if self.idn[1].strip() == "MXO54":
            self.scope.write(f"MMEM:NAME '/home/storage/userData/screenshots/Dev_Screenshot.png'")
        else:
            self.scope.write(f"MMEM:NAME 'c:/temp/Dev_Screenshot.png'")
        
        self.scope.write("HCOP:DEV:INV OFF")
        self.scope.write("HCOP:WBKG OFF")
        self.scope.write("HCOP:IMM")

        time.sleep(2)  # Wait for the hardcopy to complete

        if self.idn[1].strip() == "MXO54":
            data = self.scope.query_binary_values(f"MMEM:DATA? '/home/storage/userData/screenshots/Dev_Screenshot.png'", datatype='B', header_fmt='ieee', container=bytes)
        else:
            data = self.scope.query_binary_values(f"MMEM:DATA? 'c:/temp/Dev_Screenshot.png'", datatype='B', header_fmt='ieee', container=bytes)
        
        with open(file_path, 'wb') as file:
            file.write(data)

        self.scope.write("SYST:DISP:UPD OFF")