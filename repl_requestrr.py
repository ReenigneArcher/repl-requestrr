import os
import re
import requests
import subprocess
import zipfile
import py7zr
import time

#local imports
import keep_alive

requestrr_path = os.path.join(os.getcwd(), 'requestrr')
temp_path = os.path.join(os.getcwd(), 'temp/requestrr')
requestrr_platform = 'requestrr-linux-x64'

def make_dir(directory):
    try:
        os.makedirs(directory, mode=511, exist_ok=True)
        print(f'Successfully created directory: {directory}')
    except FileExistsError:
        pass
    except:
        print(f'Failed to create directory {directory}')


def download_file(url, save_dir):
    print(f"Download started for {url}")
    try:
        response = requests.get(url, stream=True)
    except requests.RequestException as e:
        print(f"Download error: {e}")
        return False

    make_dir(save_dir)

    save_path = os.path.join(save_dir, url.rsplit('/')[-1])

    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    print(f"Download finished for {url}")

    return save_path


def extract_archive(archive_file, destination_folder):
    extension = archive_file.rsplit('.', 1)[-1].lower()

    if extension == 'zip':
        with zipfile.ZipFile(archive_file, 'r') as archive:
            root_folder = archive.namelist()[0]
            archive.extractall(path=destination_folder)
    elif extension == '7z':
        with py7zr.SevenZipFile(archive_file, 'r') as archive:
            root_folder = archive.getnames()[0]
            methods = archive.archiveinfo().method_names

            if 'bcj2' not in methods.lower():  # methods is a string... will actually have BCJ2*
                archive.extractall(path=destination_folder)

            else:
                return False

    os.remove(archive_file)  # delete the archive file

    try:
        return root_folder
    except NameError:
        if os.path.isdir(destination_folder):
            return destination_folder
        else:
            return False


def get_latest_release():
    """return the latest version from github"""
    url = 'https://api.github.com/repos/darkalfx/requestrr/releases'

    try:
        response = requests.get(url)
    except requests.RequestException as e:
        print(f"Requests error: {e}")
        return False

    releases = response.json()

    for release in releases:
        if not release['prerelease'] and not release['draft']:
            latest = release['name']
            print(f"Latest Requestrr version: {latest}")

            for asset in release['assets']:
                if asset['name'] == f'{requestrr_platform}.zip':
                    download_url = asset['browser_download_url']

            try:
                download_url
                break
            except NameError:
                pass

    try:
        download_url
    except NameError:
        return False

    downloaded_file = download_file(url=download_url, save_dir=temp_path)
    extract_archive(archive_file=downloaded_file, destination_folder=requestrr_path)


def main():
    make_dir(requestrr_path)
    make_dir(temp_path)

    get_latest_release()

    # set permissions on file
    binary_path = os.path.join(requestrr_path, requestrr_platform, 'Requestrr.WebApi')
    st_mode = 33261
    os.chmod(binary_path, st_mode)  # https://www.tutorialspoint.com/python/os_chmod.htm

    #run requestrr
    print(binary_path)

    if os.path.isfile(binary_path):
        print('binary is true')

    binary_dir = os.path.dirname(os.path.realpath(binary_path))
    print(binary_dir)

    proc = subprocess.Popen([binary_path], cwd=binary_dir)
    proc.communicate()

    #delay 60 seconds
    #time.sleep(60)

    #keep the server alive
    #keep_alive.keep_alive()


if __name__ == '__main__':
    main()
