import win32gui
import win32process
import psutil


def list_windows():
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                except:
                    proc_name = "Unknown"

                print(f"{proc_name:<30} [ hwnd: {hwnd:<10}, pid: {pid:<10}],  title: {title}")
                windows.append((hwnd, title, proc_name))

    windows = []
    win32gui.EnumWindows(enum_callback, windows)

if __name__ == "__main__":
    list_windows()