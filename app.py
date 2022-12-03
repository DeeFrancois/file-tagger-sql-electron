from asyncio.windows_events import NULL
from email.mime import base
from fileinput import filename
from genericpath import isdir, isfile
from glob import glob
from logging import root
from operator import itemgetter
import sqlite3
import os
import random
import eel
import eel.browsers
import time
import sys
from numpy import size, true_divide
import webview
import threading
from PIL import Image, ImageOps
from multiprocessing import Pool
import subprocess
import tkinter as tk
from tkinter import filedialog
from PIL.ExifTags import TAGS

#Split sidebar with two buttons at top (or tabs?); All tags, Current vid metadata
#http://howto.philippkeller.com/2005/04/24/Tags-Database-schemas/ Toxi solution
#https://stackoverflow.com/questions/20856/recommended-sql-database-design-for-tags-or-tagging

#TODO: Finish folder change feature, figure out how to deal with folder modification
    # maybe compare db filenames to folder filenames on each run and then prompt user to update (delete/add) database on each change (or "Apply to All" ofc)
#  feature to pin window on top? will have to figure out electron specific stuff (main.js), specifically how to change window property from (opened.js to main.js communication)

class my_database:
    def __init__(self,current_db) -> None:
        self.tag_list = []
        self.current_db = current_db
        self.loaded_database=current_db+'.db'
        # self.folder=r'C:\Users\damet\Desktop\New folder\Programming\Github_Projects\Personal_WIP_Directory\_pythonsql-ELECTRON\testdatabase'
        self.populated=0

        if not isfile(self.loaded_database):
            print(self.loaded_database)
            self.fresh_database_creation()
        else:
            self.conn = sqlite3.connect(self.loaded_database)
            self.conn.execute('PRAGMA foreign_keys=ON')
            self.c = self.conn.cursor()
            
            self.populated=1
            # self.write_metadata_to_db(self.folder)
            self.get_tag_list()

    def fresh_database_creation(self):
        self.conn = sqlite3.connect(self.loaded_database)
        self.conn.execute('PRAGMA foreign_keys=ON')
        self.c = self.conn.cursor()

        # self.c.execute("DROP TABLE IF EXISTS IMAGES")
        # self.c.execute("DROP TABLE IF EXISTS TAGS")
        # self.c.execute("DROP TABLE IF EXISTS IMAGE_TAG")

        # Creating table
        img_table = """ CREATE TABLE IMAGES (
                    image_id integer,
                    filename varchar NOT NULL default '',
                    source varchar default '',
                    PRIMARY KEY (image_id),
                ); """

        tag_table = """ CREATE TABLE TAGS (
                    tag_id integer,
                    description varchar NOT NULL default '',
                    PRIMARY KEY (tag_id)
                ); """

        img_tag_map = """ CREATE TABLE IMAGE_TAG (
                    image_id integer NOT NULL default '0',
                    tag_id integer NOT NULL default '0',
                    PRIMARY KEY (image_id,tag_id),
                    CONSTRAINT image_fk FOREIGN KEY (image_id) REFERENCES IMAGES (image_id) ON DELETE CASCADE,
                    CONSTRAINT tag_fk FOREIGN KEY (tag_id) REFERENCES TAGS (tag_id) ON DELETE CASCADE
                ); """
        
        self.c.execute(img_table)
        self.c.execute(tag_table)
        self.c.execute(img_tag_map)

        self.conn.commit()

        self.add_folder_to_db()
        self.add_tag_list_to_db(self.tag_list)
        # self.exec_taging()

    def add_folder_to_db(self):
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory()

        glob_pattern = os.path.join(folder, '*')
        the_list = sorted(glob(glob_pattern), key=os.path.getctime)
        the_list = [x for x in the_list if x.split('.')[-1] in ['webm','png','mp4','jpg','jpeg'] ]

        file_count = len(the_list)
        count = 0
        for item in the_list:
            count+=1
            print(count/file_count*100,'%')
            self.c.execute("INSERT INTO IMAGES(filename) VALUES (?)",(item,))
            self.conn.commit()
            source = self.get_metadata(item)
            # print("Adding: ",item, "with Source: ",source," to database")
            self.add_source(item,source)

        self.populated=1

    def get_folder_from_db(self):
        print("Retrieving files only from the Database")
        self.c.execute("SELECT filename FROM IMAGES")
        file_list=self.c.fetchall()
        file_list=[x[0] for x in file_list]
        # self.get_root_folder_from_db()
        print(file_list)
        return file_list

    def get_folder_from_folder(self):
        print("Retrieving all files in Folder")
        folder = self.get_root_folder_from_db()

        glob_pattern = os.path.join(folder, '*.*')
        file_list = sorted(glob(glob_pattern), key=os.path.getctime)
        file_list = [x for x in file_list]
        if (len(file_list)>0):
            print("EMPTY")

        # file_list = [x for x in file_list if x.split('.')[-1] in ['webm','png','mp4','jpg'] ]
        return file_list
    
    def get_root_folder_from_db(self):
        self.c.execute("SELECT filename FROM IMAGES")
        file_list=self.c.fetchone()
        root_folder = file_list[0].split('/')[-1].split('\\')[0]
        root_filepath = file_list[0].split(root_folder)[0]+root_folder+'/'
        return root_filepath

    def clear_null_images(self):
        self.c.execute("DELETE FROM IMAGES WHERE filename='none'")
        self.conn.commit()
    
    def clear_null_tags(self):
        self.c.execute("SELECT description FROM TAGS")
        tag_list = [x[0] for x in self.c.fetchall()]
        for tag in tag_list:
            self.c.execute('SELECT * FROM IMAGE_TAG JOIN TAGS ON IMAGE_TAG.tag_id = TAGS.tag_id WHERE TAGS.description="{}"'.format(tag))
            if self.c.fetchone() is None:
                print("No images with tag: ",tag, " remain")
                self.delete_tag(tag)


    def the_transfer(self):
       
        print("STARTING TRANSFER")
        other_conn = sqlite3.connect('old_references.db')
        other_conn.execute('PRAGMA foreign_keys=ON')
        other_c = other_conn.cursor()
        self.c.execute("SELECT filename FROM IMAGES") #CURRENT
        new_filenames = [x[0] for x in self.c.fetchall()]

        for new_filepath in new_filenames: #FOR EVERY CURRENT FILEPATH
            if new_filepath == 'none':
                continue
            old_filename = new_filepath.split('\\')[-1]
            print(old_filename)
            other_c.execute('UPDATE IMAGES SET filename="{}" WHERE filename LIKE "%{}%"'.format(new_filepath,old_filename)) #REPLACE OLD FILEPATH WITH CURRENT FILEPATH IF IT CONTAINS CURRENT FILENAME
        other_conn.commit()

    def adjust_old_filenames(self):
        print("Starting adjustment")
        other_conn = sqlite3.connect('temp_db.db')
        other_conn.execute('PRAGMA foreign_keys=ON')
        other_c = other_conn.cursor()
        other_c.execute("SELECT filename FROM IMAGES")
        curr_filepaths = [x[0] for x in other_c.fetchall()]
        new_path=input("Enter new path (example: D:/db_folder\\)")

        for old_filepath in curr_filepaths:
            print("OLD FILEPATH: ",old_filepath)
            curr_filename = old_filepath.split('\\')[-1]
            new_filepath= new_path + curr_filename
            print("New: ",new_filepath)
            other_c.execute('UPDATE IMAGES SET filename="{}" WHERE filename="{}"'.format(new_filepath,old_filepath))
        other_conn.commit()
    
    def add_image_to_db(self,filename):
        print("Adding Image to database: ",filename)
        self.c.execute("INSERT INTO IMAGES(filename) VALUES(?)",(filename,)) 
        self.conn.commit()
        source = self.get_metadata(filename)
        print("Adding: ",filename, "with Source: ",source," to database")
        self.add_source(filename,source)

    def delete_image_from_db(self,filename):
        tags = self.check_tags(filename)
        print("Removing file from database: ",filename)
        self.c.execute("DELETE FROM IMAGES WHERE filename='{}'".format(filename))
        self.conn.commit()

        for tag in tags:
            self.c.execute('SELECT * FROM IMAGE_TAG JOIN TAGS ON IMAGE_TAG.tag_id = TAGS.tag_id WHERE TAGS.description="{}"'.format(tag[0]))
            if self.c.fetchone() is None:
                print("NOPE")
                self.delete_tag(tag[0])
        
        

    
    def write_metadata_to_db(self,folder):
        the_list=os.listdir(folder)
        the_list= [x for x in the_list if os.path.isfile(folder+'/'+x) ]
        for item in the_list:
            source = self.get_metadata(item)
            print("Adding: ",item, "with Source: ",source," to database")
            self.add_source(item,source)
    
    def get_metadata(self,filename):
        curr = filename
        exts = filename.split('.')[-1]
        output=''
        if (exts == 'jpg' or exts == 'png' or exts == 'jpeg' or exts =='jfif'): #Unfinished, dont have a way to efficiently read/edit title property
            return
        else:
            output = subprocess.check_output(
                'ffprobe "{}" -show_entries format_tags=title -of compact=p=0:nk=1 -v 0'.format(curr)
            )
        output = output.strip().decode('UTF-8')
        return output

    def add_tag_list_to_db(self,tags):
        for item in tags:
            self.c.execute("INSERT INTO TAGS(description) VALUES (?)",(item,))
        self.conn.commit()
    
    def get_tag_list(self):
        self.c.execute('SELECT description FROM TAGS')
        tag_list=self.c.fetchall()
        self.tag_list=[x[0] for x in tag_list]
        return self.tag_list
        #print(self.tag_list)
    
    def if_tag_exists(self,tag):
        # SELECT * FROM TAGS JOIN IMAGE_TAG ON TAGS.tag_id = IMAGE_TAG.tag_id WHERE TAGS.description='dog'
        self.c.execute('SELECT description FROM TAGS')
        tag_list=self.c.fetchall()
        self.tag_list=[x[0] for x in tag_list]
        return tag in self.tag_list
    
    def create_tag(self,tag):
        self.c.execute("INSERT INTO TAGS(description) VALUES (?)",(tag,))
        self.conn.commit()
        py_populate_tags()

    def delete_tag(self,tag):
        print("Deleting tag: ",tag)
        self.c.execute("SELECT tag_id FROM TAGS WHERE description='{}'".format(tag))
        tag_id = self.c.fetchone()
        tag_id = tag_id[0]
        self.c.execute("DELETE FROM TAGS WHERE tag_id='{}'".format(tag_id))
        self.conn.commit()
        eel.js_clear_taglist()
        py_populate_tags()
    
    def delete_tag_from_video(self,tag,filename): #work on efficiency later
        print("Deleting tag: ",tag, " from video: ",filename)

        self.c.execute("SELECT tag_id FROM TAGS WHERE description='{}'".format(tag))
        tag_id = self.c.fetchone()
        tag_id = tag_id[0]
        self.c.execute("SELECT image_id FROM IMAGES WHERE filename='{}'".format(filename))
        image_id = self.c.fetchone()
        image_id = image_id[0]
        
        self.c.execute('DELETE FROM IMAGE_TAG WHERE tag_id={} AND image_id={}'.format(tag_id,image_id))
        self.conn.commit()
        self.c.execute('SELECT * FROM IMAGE_TAG WHERE tag_id={}'.format(tag_id))
        if self.c.fetchone() == None:
            self.c.execute('DELETE FROM TAGS WHERE tag_id={}'.format(tag_id))
            self.conn.commit()
        else:
            print(self.c.fetchone())
        eel.js_clear_taglist()
        py_populate_tags()
    
    def tag_video(self,filename,tags):
        self.c.execute("SELECT image_id FROM IMAGES WHERE filename='{}'".format(filename))
        curr_image_id = self.c.fetchone()
        curr_image_id = curr_image_id[0]
        # print("Image: ",filename," corresponds to ID:",curr_image_id)
        tags=tags.split(' ')
        print("Applying tags: ",tags, "to image: ",filename)
        for tag in tags:
            if tag == '':
                pass
            if not self.if_tag_exists(tag):
                print("Creating new tag: ",tag)
                self.create_tag(tag)
            self.c.execute("SELECT tag_id FROM TAGS WHERE description='{}'".format(tag))
            curr_tag_id = self.c.fetchone()
            curr_tag_id = curr_tag_id[0]
            
            # print("Curr_tag_id: ", curr_tag_id)
            # print("Applying individual tag: ",tag)
            try:
                self.c.execute("INSERT INTO IMAGE_TAG(image_id,tag_id) VALUES(?,?)",(curr_image_id,curr_tag_id))
            except:
                print("Constraint")

            self.conn.commit()
    
    def add_source(self,filename,source):
        self.c.execute('UPDATE IMAGES SET source="{}" WHERE filename="{}"'.format(source,filename))
        self.conn.commit()
            

    def exec_taging(self):
        list_of_files = (os.listdir(self.folder))
        random.shuffle(list_of_files)
        
        for item in list_of_files:
            # print(os.getcwd()+'\\'+self.folder+'\\'+item)
            os.startfile(os.getcwd()+'\\'+self.folder+'\\'+item)
            self.c.execute("SELECT image_id FROM IMAGES WHERE filename='{}'".format(item))
            curr_image_id = self.c.fetchone()
            curr_image_id = curr_image_id[0]
            # print("Image: ",item," corresponds to ID:",curr_image_id)
            user_input = input("Enter Tags for current Video:")
            if user_input == 'q':
                return
            user_input = user_input.split(' ')

            for tag in user_input:
                if not self.if_tag_exists(tag):
                    self.create_tag(tag)

                self.c.execute("SELECT tag_id FROM TAGS WHERE description='{}'".format(tag))
                curr_tag_id = self.c.fetchone()
                curr_tag_id = curr_tag_id[0]
                
                # print("Curr_tag_id: ", curr_tag_id)
                # print("Applying individual tag: ",tag)
                
                self.c.execute("INSERT INTO IMAGE_TAG(image_id,tag_id) VALUES(?,?)",(curr_image_id,curr_tag_id))
                self.conn.commit()

            # print("Finished Applying: ",user_input)
            self.c.execute("SELECT TAGS.description FROM TAGS JOIN IMAGE_TAG ON TAGS.tag_id = IMAGE_TAG.tag_id WHERE IMAGE_TAG.image_id={}".format(curr_image_id))
            # print(self.c.fetchall())
    
    def check_tags(self,filename):
        # print("Check tags")
        if self.populated==0:
            print("NOT POPULARED")
            return
        self.c.execute("SELECT image_id FROM IMAGES WHERE filename='{}'".format(filename))
        curr_image_id=self.c.fetchone()
        # print(curr_image_id)
        if curr_image_id == None:
            the_db.add_image_to_db(filename)
            return ''
        curr_image_id=curr_image_id[0]
        self.c.execute("SELECT TAGS.description FROM TAGS JOIN IMAGE_TAG ON TAGS.tag_id = IMAGE_TAG.tag_id WHERE IMAGE_TAG.image_id={}".format(curr_image_id))
        return (self.c.fetchall())
    
    def check_source(self,filename):
        self.c.execute("SELECT source FROM IMAGES WHERE filename='{}'".format(filename))
        curr_source=self.c.fetchone()[0]
        # print(curr_source)
        return curr_source

    def check_tags_loop(self):
        list_of_files = os.listdir(self.folder)
        # print(len(list_of_files))
        for item in list_of_files:
            self.c.execute("SELECT image_id FROM IMAGES WHERE filename='{}'".format(item))
            curr_image_id=self.c.fetchone()
            curr_image_id=curr_image_id[0]
            self.c.execute("SELECT TAGS.description FROM TAGS JOIN IMAGE_TAG ON TAGS.tag_id = IMAGE_TAG.tag_id WHERE IMAGE_TAG.image_id={}".format(curr_image_id))
            # print("FILENAME: ", item, " TAGS: ", self.c.fetchall())
    def get_batch_based_on_tag(self,tag):
        print(tag)
        if self.if_tag_exists(tag):
            self.c.execute("SELECT tag_id FROM TAGS WHERE TAGS.description='{}'".format(tag))
            curr_image_id=self.c.fetchone()
            curr_image_id=curr_image_id[0]
            # SELECT tag_id FROM TAGS WHERE TAGS.description = 'dog';
            self.c.execute("SELECT filename FROM IMAGES JOIN IMAGE_TAG ON IMAGES.image_id=IMAGE_TAG.image_id WHERE IMAGE_TAG.tag_id={}".format(curr_image_id))
            filenames = self.c.fetchall()
            file_list=[x[0] for x in filenames]
            return file_list
        


        




print("Here")

#Using Electron


eel.init('web')
# eel.start('main.html',mode='chrome',block=False,size=(909,690))
# eel.browsers.set_path('electron', 'node_modules/electron/dist/electron')
# options = {
# 	'mode': 'custom',
# 	'args': ['node_modules/electron/dist/electron.exe', '.']
# }
# eel.start('web/main.html',mode='electron',size=(909,690))
def resource_path(rel_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

eel.browsers.set_path('electron',resource_path('node_modules/electron/dist/electron.exe'))
# eel.start('index.html',mode='electron')

# webview.create_window('title','http://localhost/web/main.html:8000')
# webview.start()
# 
# global current_folder
# global current_index
# global current_drawer_index
# global folder_size
# global current_db
# global the_db
# global last_tag_batch
# global base_list
# last_tag_batch = ''
# current_index = -1
# current_drawer_index=0


# lock =0
# # current_db=input('Specify database folder')
# current_db='crashlogs2'



# current_folder=os.listdir('web/files/'+current_db+'/')
# current_folder= [x for x in current_folder if os.path.isfile('web/files/'+current_db+'/'+x) ]
# random.shuffle(current_folder)
# base_list = current_folder
# the_db = my_database(current_db)
# folder_size = len(current_folder)

@eel.expose
def close():
    sys.exit(0)

@eel.expose
def hide_based_on_tags(): #This filter works for first display (so to hide stuff for demos, but will need to move filter functions to the actual the_db class for it to work within real usage)
    filter_list = ['poster','test','nude']
    current_list = current_folder
    for ind,item in enumerate(current_list):
        filter_flag = False
        tags = the_db.check_tags(item)
        # print(tags)
        for current_tag in tags:
            if current_tag[0] in filter_list:
                print("FILTERING OUT: ")
                print(current_folder[ind])
                current_folder[ind] = 'none'
                break
    print("After filtering, size of folder: ",len(current_folder))
    
        

@eel.expose
def py_left_control():
    global current_index
    if current_index-1 > -1:
        current_index-=1
    else:
        current_index=folder_size-1

    if current_folder[current_index]=='none':
        print("Hidden post")
        print(current_index)
        py_left_control()
        return
    eel.js_display_file(current_folder[current_index],current_db,current_index)
    eel.js_trigger_hover()
    py_get_tags()
    
@eel.expose
def py_right_control():
    print("RIGHT CONTROL")
    global current_index
    if current_index+1 <= folder_size-1:
        current_index=current_index+1
    else:
        current_index=0
    
    if current_folder[current_index]=='none':
        print("Hidden post")
        py_right_control()
        return
    eel.js_display_file(current_folder[current_index],current_db,current_index)
    eel.js_trigger_hover()
    py_get_tags()

@eel.expose
def py_get_tags():
    # print("Get tags")
    filename = current_folder[current_index]
    tags=the_db.check_tags(filename)
    if len(tags)==0:
        tags = 'No tags available'
    # print("Filename: ",filename," Tags: ",tags)
    # print("Displaying")
    eel.js_display_tags(tags)
    source = the_db.check_source(filename)
    # print(len(source))
    filename=filename.split('\\')[-1]
    if len(filename) > 20:
        filename = filename[0:25]+'...'
        
    if len(source) > 20:
        source=source[0:20]+'...'
    
    # get_more_details(current_folder[current_index])
    eel.js_display_source(filename,source)
     #unfinished

def get_more_details(filename):
    image = Image.open(filename)
    exifdata=image.getexif()
    print(str(exifdata))
    # print(exif)
    eel.js_more_details(str(exifdata))


@eel.expose
def py_set_tags(tags):
    # print("TAGS RECIEVED: ",tags)
    filename = current_folder[current_index]
    the_db.tag_video(filename,tags)
    py_get_tags()
    py_right_control()

@eel.expose 
def py_set_source(source,write_to_file): 
    # print("Setting video source")
    print(source)
    filepath = current_folder[current_index]
    the_db.add_source(filepath,source)
    if (write_to_file):
        write_source_to_file(filepath,source)
    py_right_control()



@eel.expose
def py_delete_tags_from_video(tags):
    filename=current_folder[current_index]
    taglist = tags.split(' ')
    for item in taglist:
        the_db.delete_tag_from_video(item,filename)
    py_get_tags()

@eel.expose
def py_delete_tags(tags):
    taglist = tags.split(' ')
    for item in taglist:
        the_db.delete_tag(item)
    py_get_tags()





@eel.expose
def py_update_index(filename):
    print("UPDATE INDEX")
    print(repr(filename))
    global current_index
    # print(current_folder)
    # print(filename)
    current_index=current_folder.index(filename)-1
    
    py_right_control()
    # py_get_tags()


@eel.expose
def py_populate_drawer():
    global current_drawer_index
    # print("Called to populate")
    eel.js_clear_drawer()
    eel.js_change_database_label(current_db+'.db')
    current_drawer_index=0
    for item in current_folder[current_drawer_index:3000]:
        if (item is 'none'):
            continue
        # print(item)
        filename=item.split('\\')[-1]
        thumb_path='files/thumbs/'+current_db+'/'+filename.replace('.webm','.jpg').replace('.mp4','.jpg')
        eel.js_add_to_drawer(item,current_db,thumb_path)
        current_drawer_index+=1
    py_initial_routine()
    py_populate_tags()
    py_right_control()
    eel.js_refresh_thumb_size()

@eel.expose
def py_open_file(relpath):
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, 'web/'+relpath)
    os.startfile(relpath)
    # curr=os.getcwd()
    # print(curr)
    # print(os.path.join(curr,'\web',filename))
    # os.startfile(path)
    

@eel.expose
def py_retrieve_batch_with_tag(tag):
    
    global last_tag_batch
    global current_drawer_index
    global current_folder
    global folder_size
    if tag == last_tag_batch:
        last_tag_batch = ''
        print("Sorting by: ",tag)

        eel.js_clear_drawer()
        current_drawer_index=0
        current_folder=base_list
        folder_size = len(current_folder)
        for item in current_folder[current_drawer_index:150]:
            # print(item)
            filename=item.split('\\')[-1]
            thumb_path='files/thumbs/'+current_db+'/'+filename.replace('.webm','.jpg').replace('.mp4','.jpg')
            eel.js_add_to_drawer(item,current_db,thumb_path)
            current_drawer_index+=1
    else:
        last_tag_batch = tag
        print("Clearing sort")

        eel.js_clear_drawer()
        current_drawer_index=0
        current_folder=the_db.get_batch_based_on_tag(tag)
        
        folder_size = len(current_folder)

        for item in current_folder:
            # print(item)
            filename=item.split('\\')[-1]
            thumb_path='files/thumbs/'+current_db+'/'+filename.replace('.webm','.jpg').replace('.mp4','.jpg')
            eel.js_add_to_drawer(item,current_db,thumb_path)
            current_drawer_index+=1


@eel.expose
def py_populate_tags():
    eel.js_clear_taglist()
    tags = the_db.get_tag_list()
    for item in tags:
        eel.js_add_to_tagfield(item)

@eel.expose
def py_hide_image(filepath):
    # print("HIDING POST")
    current_folder[current_folder.index(filepath)]='none'

@eel.expose
def py_delete_image(input_filepath,delete_locally):
    global current_index
    global folder_size

    current_folder.pop(current_folder.index(input_filepath))
    folder_size-=1
    the_db.delete_image_from_db(input_filepath)
    filename=input_filepath.split('\\')[-1]
    thumbnail = 'files/thumbs/'+current_db+'/'+filename.replace(filename.split('.')[-1],'jpg')

    dirname = os.path.dirname(__file__)

    thumbnail = os.path.join(dirname, 'web/'+thumbnail)
    if delete_locally:
        print("Deleting local files as well")
        os.remove(input_filepath)
        os.remove(thumbnail)
    if current_index-1 > -1:
        current_index-=1
    else:
        current_index=folder_size-1
    py_right_control()

    
def write_source_to_file(filepath,source): #TODO: Make this optional, then find a way to edit a video file without changing the creation date  
    curr = filepath
    filename=filepath.split('\\')[-1]
    print("Writing source to file")
    subprocess.call(
        # ffmpeg -i default.mp4 -metadata title="my title" -codec copy output.mp4 && mv output.mp4 default.mp4
        'ffmpeg -i "{}" -metadata title="{}" -codec copy "out-{}"'.format(curr,source,filename))
    os.replace('out-{}'.format(filename),curr)
    print("DONE")

def get_metadata():
    for filepath in current_folder:
        curr = filepath
        output = subprocess.check_output(
            'ffprobe "{}" -show_entries format_tags=title -of compact=p=0:nk=1 -v 0'.format(curr) 
        )
        output = output.strip().decode('UTF-8')
        if output != '':
            print("FILE: ",filepath, "METADATA: ",output)

def generate_thumbnail():
    print("Generating Thumbnails")
    count = 0
    file_count = len(current_folder)

    try:
        os.mkdir('web/files/thumbs/'+current_db)
    except:
        pass
    for filepath in current_folder:
        count+=1
        filename=filepath.split('\\')[-1]
        # print(filename)
        curr = filepath
        # print(curr)

        output='web/files/thumbs/'+current_db+'/'+filename.replace('.webm','.jpg').replace('.mp4','.jpg')
        if os.path.exists(output):
            continue
        print(count/file_count*100,'%')
        
        # ffmpeg.input(curr).output(output).run()
        # print('Input: ',curr, " OUTPUT: ",output)
        exts = filename.split('.')[-1]
        # print(exts)
        size=(236,326)
        if exts == 'ini':
            continue
        if not(exts == 'jpg' or exts == 'png' or exts == 'jpeg' or exts =='jfif'):
            
            subprocess.call(
            'ffmpeg -hide_banner -loglevel error -y -i "{}" -q:v 1 -vframes 1 "{}"'.format(curr, output))
            
            try:
                # Load just once, then successively scale down
                im=Image.open(output)
                # im.thumbnail(size,Image.ANTIALIAS)
                im2 = ImageOps.fit(im,size,method=Image.LANCZOS,centering=(0.5,0.5))
                im2.save(output)

            except Exception as e: 
                return e 

        else: #image
            try:
                # Load just once, then successively scale down
                im=Image.open(curr)
                # im.thumbnail(size,Image.ANTIALIAS)
                im2 = ImageOps.fit(im,size,method=Image.LANCZOS,centering=(0.5,0.5))
                im2.save(output)

            except Exception as e:
                im=Image.open(curr)
                rgb_im = im.convert('RGB')
                # im.thumbnail(size,Image.ANTIALIAS)
                im2 = ImageOps.fit(rgb_im,size,method=Image.LANCZOS,centering=(0.5,0.5))
                im2.save(output)
                # pass

@eel.expose
def py_check_if_exists(db_name,gen_thumbs,shuffle):
    if os.path.isfile(db_name+'.db'):
        py_open_new_db(db_name,gen_thumbs,shuffle)
    else:
        print(db_name)
        eel.js_confirmation(db_name)
        
@eel.expose
def py_open_new_db(new_folder,gen_thumbs,shuffle):
    
    global the_db
    global current_index
    global current_drawer_index
    global current_folder
    global folder_size
    global lock
    global current_db
    global base_list
    global last_tag_batch
    try:
        del the_db
    except:
        pass
    
    eel.js_clear_taglist()
    current_index = -1
    current_drawer_index=0
    current_db = new_folder
    lock =0
    last_tag_batch=''

    the_db = my_database(current_db)
    # current_folder=the_db.get_folder_from_db()
    # print(the_db.get_folder_from_db())
    # the_db.adjust_old_filenames()
    current_folder=the_db.get_folder_from_folder()
    base_list=current_folder
    # if len(base_list) == 0:
    #     print("EMPTY")
    #     the_db.adjust_old_filenames()
    #     return
    the_db.get_tag_list()
    folder_size = len(current_folder)
    print(folder_size, " images in folder")
    # generate_thumbnail()
    if gen_thumbs:
        generate_thumbnail()
    if shuffle:
        random.shuffle(current_folder)
    # hide_based_on_tags()
    py_populate_drawer()
    # the_db.the_transfer()
    # the_db.adjust_old_filenames()
    # print(the_db.get_root_folder_from_db())
    # the_db.get_root_folder_from_db()
    the_db.clear_null_images()
    the_db.clear_null_tags()
    # get_metadata()

# generate_thumbnail()
# x = threading.Thread(target=generate_thumbnail)
# x.start()
@eel.expose
def py_initial_routine():
    #check for existing folders
    folders=os.listdir()
    # print(folders)
    existing_databases = []
    
    for item in folders:
        # if item.split('.')[-1] == 'db' and item.split('.')[0]!='crashlogs' and item.split('.')[0]!='test_crashlogs':
        if item.split('.')[-1] == 'db':
            existing_databases.append(item)
    eel.js_update_autocomplete(existing_databases)


eel.start('main.html',mode='electron')
# py_initial_routine()
# py_initial_routine()
# while True:
#     eel.sleep(1)