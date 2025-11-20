import platform
import os

def get_usb_or_downloads_path():
    system = platform.system().lower()
    # Android detection (Kivy's buildozer sets ANDROID_ARGUMENT)
    if 'ANDROID_ARGUMENT' in os.environ or 'android' in system:
        # Try to find USB mount (common paths)
        usb_paths = ['/storage/usb', '/storage/udisk', '/mnt/media_rw', '/mnt/usb', '/storage/UsbDriveA', '/storage/UsbDriveB']
        for path in usb_paths:
            if os.path.isdir(path):
                # Return first found USB path
                return path
        # Default to Downloads
        downloads = os.path.join(os.path.expanduser('~'), 'Download')
        if os.path.isdir(downloads):
            return downloads
        # Fallback to home
        return os.path.expanduser('~')
    elif 'windows' in system:
        # Try to find USB drive (removable drives)
        import string
        import ctypes
        drives = [f'{d}:\\' for d in string.ascii_uppercase]
        for drive in drives:
            if os.path.exists(drive):
                try:
                    drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                    # DRIVE_REMOVABLE == 2
                    if drive_type == 2:
                        return drive
                except Exception:
                    continue
        # Default to Downloads
        downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
        if os.path.isdir(downloads):
            return downloads
        return os.path.expanduser('~')
    else:
        # Linux/Mac: just use Downloads
        downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
        if os.path.isdir(downloads):
            return downloads
        return os.path.expanduser('~')
