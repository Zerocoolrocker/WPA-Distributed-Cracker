import os, ctypes


def get_ram():
    def windowsRam():
        """Uses Windows API to check RAM in this OS"""
        kernel32 = ctypes.windll.kernel32
        c_ulong = ctypes.c_ulong
        class MEMORYSTATUS(ctypes.Structure):
            _fields_ = [
                ("dwLength", c_ulong),
                ("dwMemoryLoad", c_ulong),
                ("dwTotalPhys", c_ulong),
                ("dwAvailPhys", c_ulong),
                ("dwTotalPageFile", c_ulong),
                ("dwAvailPageFile", c_ulong),
                ("dwTotalVirtual", c_ulong),
                ("dwAvailVirtual", c_ulong)
            ]
        memoryStatus = MEMORYSTATUS()
        memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUS)
        kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))

        return int(memoryStatus.dwTotalPhys/1024**2)

    def linuxRam():
        """Returns the RAM of a linux system"""
        totalMemory = os.popen("free -m").readlines()[1].split()[1]
        return int(totalMemory)

    if os.name == "posix":
        return linuxRam()
    elif os.name == "nt":
        return windowsRam()