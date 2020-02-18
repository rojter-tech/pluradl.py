import os
import os.path
import ssl
import stat
import subprocess
import sys
import platform

STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )

def install_cert():
    openssl_dir, openssl_cafile = os.path.split(
        ssl.get_default_verify_paths().openssl_cafile)

    print("Cerificate were not installed.")
    print("Detected operating system:", platform.system())
    print("Installing certificate ...")
    if platform.system() == 'Linux':
        subprocess.check_call([sys.executable,
            "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi", "--user"])
    elif platform.system() == 'Darwin':
        subprocess.check_call([sys.executable,
            "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])
    elif platform.system() == 'Windows':
        subprocess.check_call([sys.executable,
            "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi", "--user"])
    else:
        subprocess.check_call([sys.executable,
            "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi", "--user"])

    import certifi

    # change working directory to the default SSL directory
    if os.path.exists(openssl_dir):
        os.chdir(openssl_dir)
    
    abspath_to_certifi_cafile = os.path.abspath(certifi.where())
    print(" -- removing any existing file or link")
    try:
        os.remove(openssl_cafile)
    except FileNotFoundError:
        pass
    except PermissionError:
        print(openssl_cafile)
        pass
    print(" -- creating symlink to certifi certificate bundle")
    try:
        os.symlink(abspath_to_certifi_cafile, openssl_cafile)
    except FileExistsError:
        pass
    print(" -- setting permissions")
    try:
        os.chmod(openssl_cafile, STAT_0o775)
    except PermissionError:
        pass
    print(" -- update complete")

if __name__ == '__main__':
    install_cert()