import os
import configparser
import magic
from pprint import pprint
import subprocess
import shutil
import pathlib
import threading
import sys
import cue_parse
#https://unix.stackexchange.com/questions/10251/how-do-i-split-a-flac-with-a-cue
# sudo apt-get install cuetools shntool
# cuebreakpoints file.cue | shnsplit -o flac file.flac
# cuetag.sh file.cue "split-*".flac

"""
shnsplit -f file.cue -t %n-%t -o flac file.flac
cuetag file.cue "split-*".flac
"""

def mime_type(file_path):
    return magic.from_file(file_path, mime=True)

def replace_special_chars(file_name):
    new_file_name = os.path.basename(file_name.replace(" ", ""))
    new_name =  os.path.join(os.path.dirname(file_name), new_file_name)
    os.rename(file_name, new_name)

    return new_name

def cues_and_flacs():
    flac_cue_dict_list = []
    for root, dirs, files in os.walk(cue_file_root_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path):
                file_mime_type = mime_type(file_path)
                # print(file_mime_type.split("/"), file_name)

                if file_mime_type == "audio/x-flac":
                    flac_file_path = file_path
                    filename_stem = os.path.splitext(file_name)[0]
                    cue_file_path = os.path.join(root, "{}.cue".format(filename_stem))
                    log_file_path = os.path.join(root, "{}.log".format(filename_stem))


                    if os.path.isfile(cue_file_path):
                        flac_cue_dict = {
                            "flac": flac_file_path,
                            "cue": cue_file_path,
                            "log": log_file_path
                        }
                        for f_name in os.listdir(os.path.dirname(cue_file_path)):
                            f_path = os.path.join(os.path.dirname(cue_file_path), f_name)
                            if os.path.isfile(f_path):
                                file_mime_type = mime_type(f_path)
                                if file_mime_type.split("/")[0] == "image" and f_name.lower().startswith("front"):
                                    # print(f_path)
                                    flac_cue_dict["cover"] = f_path
                        flac_cue_dict_list.append(flac_cue_dict)

    return flac_cue_dict_list

# def split_flac(flac_cue_dict_list):
#     for flac_cue_dict in flac_cue_dict_list[0:1]:
#         flac_file = flac_cue_dict["flac"]
#         cue_file = flac_cue_dict["cue"]
#
#         working_dir = os.path.dirname(flac_file)
#         os.chdir(working_dir)
#
#         subprocess.check_output(["shnsplit", "-f", cue_file, "-t", "split-%n-%t", "-o", "flac", flac_file])
#         output = subprocess.check_output(["cuetag", cue_file, "split-*"])
#         print(output)
#
#         sys.exit(0)
#
#         working_dir_name = working_dir.split(os.sep)[-1]
#         split_flac_dir = os.path.join(flac_root_dir, working_dir_name)
#         if not os.path.isdir(split_flac_dir):
#             os.makedirs(split_flac_dir)
#
#         for i in os.listdir(working_dir):
#             if i.startswith("split"):
#                 print(os.path.abspath(i))
#                 shutil.move(os.path.abspath(i), os.path.join(split_flac_dir, i))




def worker(flac_song_path, mp3_song_path):
    flac_song = os.path.basename(flac_song_path)
    print("Processing:\t{}".format(flac_song))
    mp3_song_folder = os.path.dirname(mp3_song_path)
    if not os.path.isdir(mp3_song_folder):
        os.makedirs(mp3_song_folder)
    subprocess.check_output(["ffmpeg", "-y", "-i", flac_song_path, "-b:a", "320k", mp3_song_path])
    print("Complete:\t{}".format(flac_song))


def get_flag_song_list():
    flac_song_list = []
    for root, dirs, file_name in os.walk(flac_root_dir):
        for i in file_name:
            file_path = os.path.join(root, i)
            mime_type = magic.from_file(file_path, mime=True)
            print(file_name, mime_type, type(mime_type))
            if mime_type == 'audio/x-flac':
                flac_song_list.append(file_path)
    return flac_song_list


def get_mp3_song_path(flac_song_path):
    flac_song = os.path.basename(flac_song_path)
    flac_song_folder = os.path.dirname(flac_song_path)
    mp3_song_folder = mp3_folder.join(flac_song_folder.split(flac_root_dir))
    mp3_song = flac_song.replace(pathlib.Path(flac_song_path).suffix, '.mp3')
    mp3_song_path = os.path.join(mp3_song_folder, mp3_song)
    return mp3_song_path


def check_dependencies():
    dependency_list = ["flac", "lame", "ffmpeg"]
    dependencies_installed = True
    for dependency in dependency_list:
        not_installed_message = "{} not installed. sudo apt install {}".format(dependency, dependency)
        try:
            output = subprocess.check_output(["which", dependency]).strip()
            expected_output = "/usr/bin/{}".format(dependency).encode()
            if output == expected_output:
                print("{} installed: {}".format(dependency, str(output)))
            else:
                print(not_installed_message)
                dependencies_installed = False
        except subprocess.CalledProcessError as e:
            print(not_installed_message)
            dependencies_installed = False
    if dependencies_installed is False:
        sys.exit(0)


root_dir = "/home/andy/Documents/ConvertMusic"
cue_file_root_dir = os.path.join(root_dir, "cue_files")
flac_root_dir = os.path.join(root_dir, "flac")
mp3_folder = os.path.join(root_dir, 'mp3')

if __name__ == "__main__":
    # Locates unsplit flac files and their corresponding cue files, splits them & converts to mp3
    flac_cue_dict_list = cues_and_flacs()
    for flac_cue_dict in flac_cue_dict_list:

        cue = flac_cue_dict["cue"]
        flac = flac_cue_dict["flac"]
        try:
            cover = flac_cue_dict["cover"]
        except KeyError:
            cover = None
        cue_parse.cue_flac_mp3(cue_file=cue, flac_file=flac, cover=cover)

    # Locates individual song flac files and converts to mp3
    threads = []
    flac_song_list = get_flag_song_list()
    for flac_song_path in flac_song_list:
        mp3_song_path = get_mp3_song_path(flac_song_path)
        print(mp3_song_path)
        t = threading.Thread(target=worker, args=(flac_song_path, mp3_song_path))
        threads.append(t)
        t.start()
