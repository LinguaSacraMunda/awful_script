import os
import eyed3
import mutagen
import codecs

#download path
PATH = 'D:/YT/Download/'
#destination path
PDST = 'D:/YT/Converted/'
#temporary location of downloaded files
TEMP = 'D:/YT/Download/temp/'

#find the folder where the files are to be moved to after tagging
#folder is named in form of: {artist_name} - {album_name}
def defineAlbumPath():
    DIRS = [n for n in os.listdir(PATH)]
    for n in DIRS:
        if n != 'temp':
            albm = n
            albm_dir = PATH + n
            return [albm, albm_dir]

#make a list of *.mp3 files in the PATH/temp/ (folder used for storing downloaded files)
def getFilesInTemp():
    file_names = [n for n in os.listdir(TEMP) if os.path.isfile(os.path.join(TEMP, n)) and n[(len(n) - 3)::] == 'mp3']
    return(file_names)

def looseFileMove(albm_dir, album):
    file_names = [n for n in os.listdir(albm_dir) if os.path(os.path.join(albm_dir, n))]
    for file in file_names:
        src = albm_dir + file
        dst = PDST + album + '/' + file
        os.rename(src, dst)

def getGenInfo(albm):
    gen_data = ['artist_name', 'album_title', 'year']
    #'-' changed to ' - ' to cover cases of hyphen in artist name
    gen_data[0] = albm[:(albm.index(' - '))]
    #3 is used to remove ' - ' starting at the first blank space
    gen_data[1] = albm[(albm.index(' - ') + 3):]
    #TODO query the web to find album release date?
    gen_data[2] = str(input("Release year: "))
    return(gen_data)

def clearName(file_name):
    #remove the numbering in front of the name and rename the file
    main_name = file_name[(file_name.index('-') + 1):]
    os.rename(TEMP + file_name, TEMP + main_name)
    #remove the .mp3 extension from the name string
    name = main_name[:-4]
    return name

def getNameAndIndex(file_name):
    #downloaded file names formed as XXXXX-{song_name}
    index = int(file_name[:(file_name.index('-'))])
    name = clearName(file_name)
    return [name, index]

def moveFile(file_name, album):
    scr = TEMP + file_name + '.mp3'
    dst = PDST + album + '/' + file_name + '.mp3'
    os.rename(scr, dst)

def getRuntime(file):
    audio = mutagen.File(file)
    return(audio.info.length)
 
def m3u8Editor(m3u8File, playlist):
    line = f"#EXTINF:{playlist[2]}, {playlist[0]} - {playlist[1]}\n{playlist[1]}.mp3\n"
    m3u8File.writelines(line)

def main():
    albm_info = defineAlbumPath()
    down_list = getFilesInTemp()
    #general metadata the is used immutably for every file
    gen_data = getGenInfo(albm_info[0])
    #make a new directory to hold tagged files
    fpath = PDST + albm_info[0]
    if albm_info[0] not in os.listdir(PDST): 
        os.mkdir(fpath)

    m3u8Path = os.path.join(fpath, "{}.m3u8".format(
        os.path.basename(fpath)
    ))

    with codecs.open(m3u8Path, "w", "utf-8") as m3u8File:
        m3u8File.writelines("#EXTM3U\n")

        playlist = []

        for file_name in down_list:
            #get file name and index for every separate file
            index_data = getNameAndIndex(file_name)
            audfile = eyed3.load(TEMP + index_data[0] + '.mp3')
            print('Editing metadata of '+ index_data[0] + '...')
            #edit the following metadata tags
            audfile.tag.artist = gen_data[0]
            audfile.tag.album_artist = gen_data[0]
            audfile.tag.album = gen_data[1]
            audfile.tag.title = index_data[0]
            audfile.tag.track_num = index_data[1]
            audfile.tag.recording_date = gen_data[2]
            #save changed tags
            audfile.tag.save()

            #get info for m3u8 file
            playlist.append(gen_data[0])
            playlist.append(index_data[0])
            playlist.append(getRuntime(TEMP + index_data[0] + '.mp3'))

            print(f'Editing "{gen_data[0]} - {gen_data[1]}.m3u8"')
            m3u8Editor(m3u8File, playlist)

            playlist = []

            print('Moving ' + index_data[0] + '...')
            moveFile(index_data[0], albm_info[0])

        m3u8File.close()

    #check to see if any loose files(i.e. album cover) are still in the original album directory and move them
    looseFileMove(albm_info[1], albm_info[0])
    
    print('Done')

    #delete the now empty dir in PATH
    os.rmdir(albm_info[1])

    



if __name__ == '__main__':
    main()
else:
    print('File to be run as __main__')
