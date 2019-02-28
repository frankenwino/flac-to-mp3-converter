# sudo apt install sox libsox-fmt-all ffmpeg
# https://github.com/Puckid/albumSplitter/blob/master/albumSplitter.py
# https://github.com/jiaaro/pydub/blob/master/API.markdown

"""
TODO: For some reason, the year is not added to the mp3 version of the song.
"""


from deflacue import deflacue as cue
from pydub import AudioSegment as aud
from pprint import pprint
import os
import sys

def cue_flac_mp3(cue_file, flac_file, cover=None):
    metadata = cue.CueParser(cue_file, encoding="utf-8").get_data_tracks()
    flac_file_object = aud.from_file(flac_file, format="flac")

    for song in metadata:
        album = song["ALBUM"]
        year = song["DATE"]
        genre = song["GENRE"]
        artist = song["PERFORMER"]
        title = song["TITLE"].replace("/", "-")
        track = song["TRACK_NUM"]
        start_time = song["POS_START_SAMPLES"] // (44100 / 1000.)
        try:
            end_time = song["POS_END_SAMPLES"] // (44100 / 1000.)
        except TypeError:
            end_time = None

        # pprint({'artist': artist, 'album_artist': artist, 'year': year, 'album': album, 'track': track, 'title': title, 'genre': genre})

        tmp = flac_file_object[start_time:end_time]

        output_dir = os.path.join(mp3_folder, artist, "{} - {}".format(year, album))
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)


        mp3_file_path = os.path.join(output_dir, "{} {}.mp3".format(track, title))

        if cover is None:
            print("Creating {}".format(mp3_file_path))
            tmp.export(
                mp3_file_path,
                format="mp3",
                bitrate="320k",
                tags={'artist': artist, 'album_artist': artist, 'year': year, 'album': album, 'track': track, 'title': title, 'genre': genre}

            )
        else:
            print("Creating with cover {}".format(mp3_file_path))
            tmp.export(
                mp3_file_path,
                format="mp3",
                bitrate="320k",
                tags={'artist': artist, 'album_artist': artist, 'year': year, 'album': album, 'track': track, 'title': title, 'genre': genre},
                cover=cover

            )

home_folder =  os.environ['HOME']
convert_folder = os.path.join(home_folder, "Documents", 'ConvertMusic')
flac_folder = os.path.join(convert_folder, 'flac')
mp3_folder = os.path.join(convert_folder, 'mp3')


if __name__ == "__main__":
    pass
    # cue_file = "/home/andy/Documents/ConvertMusic/split_flac (copy)/Sodom/1987 - Persecution Mania [1993, Teichiku Rec., TECX-20527, Japan]/Sodom - Persecution Mania (TECX-20527).cue"
    # flac_file = "/home/andy/Documents/ConvertMusic/split_flac (copy)/Sodom/1987 - Persecution Mania [1993, Teichiku Rec., TECX-20527, Japan]/Sodom - Persecution Mania (TECX-20527).flac"
    # cover = "/home/andy/Documents/ConvertMusic/split_flac (copy)/Sodom/1987 - Persecution Mania [1993, Teichiku Rec., TECX-20527, Japan]/Front.jpg"
    cue_flac_mp3(cue_file, flac_file, cover)
