from asyncio.windows_events import NULL
from email.mime import base
from fileinput import filename
from genericpath import isdir, isfile
from glob import glob
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

#
#TODO: DELETE IMAGES FROM DATABASE
#FIX "orphan"
#http://howto.philippkeller.com/2005/04/24/Tags-Database-schemas/ Toxi solution
#https://stackoverflow.com/questions/20856/recommended-sql-database-design-for-tags-or-tagging
class my_database:
    def __init__(self,current_db) -> None:
        self.tag_list = []
        #self.folder = 'web/files'
        # self.loaded_database = input('Enter database name: ')
        # self.folder = input('files or other')
        self.current_db = current_db
        self.loaded_database=current_db+'.db'
        self.folder=r'C:\Users\damet\Desktop\New folder\Programming\Github_Projects\Personal_WIP_Directory\_pythonsql-ELECTRON\testdatabase'
       
        
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
            # self.check_tags()

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
                    PRIMARY KEY (image_id)
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
        print("ADDING FOLDER")
        root = tk.Tk()
        root.withdraw()

        folder = filedialog.askdirectory()

        # the_list=os.listdir(folder)
        # the_list= [x for x in the_list if os.path.isfile(folder+'/'+x) ]
        glob_pattern = os.path.join(folder, '*')
        the_list = sorted(glob(glob_pattern), key=os.path.getctime)
        for item in the_list:
            self.c.execute("INSERT INTO IMAGES(filename) VALUES (?)",(item,))
            self.conn.commit()
            source = self.get_metadata(item)
            print("Adding: ",item, "with Source: ",source," to database")
            self.add_source(item,source)
        self.populated=1
    def get_folder_from_db(self):
        print("Retrieving files from database")
        self.c.execute("SELECT filename FROM IMAGES")
        file_list=self.c.fetchall()
        file_list=[x[0] for x in file_list]
        return file_list

    def add_image_to_db(self,filename):
        print("Adding Image to database: ",filename)
        self.c.execute("INSERT INTO IMAGES(filename) VALUES(?)",(filename,)) 
        self.conn.commit()
        source = self.get_metadata(filename)
        print("Adding: ",filename, "with Source: ",source," to database")
        self.add_source(filename,source)
        # print("ADDED")
    def delete_image_from_db(self,filename):
        print("Removing file from database: ",filename)
        self.c.execute("DELETE FROM IMAGES WHERE filename='{}'".format(filename))
        self.conn.commit()

    
    def write_metadata_to_db(self,folder):
        the_list=os.listdir(folder)
        the_list= [x for x in the_list if os.path.isfile(folder+'/'+x) ]
        for item in the_list:
            # self.c.execute("INSERT INTO IMAGES(filename) VALUES (?)",(item,))
            # self.conn.commit()
            source = self.get_metadata(item)
            print("Adding: ",item, "with Source: ",source," to database")
            self.add_source(item,source)
    
    def get_metadata(self,filename):
        curr = filename
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
        # # SELECT TAGS.description FROM TAGS JOIN IMAGE_TAG ON TAGS.tag_id = IMAGE_TAG.tag_id WHERE IMAGE_TAG.image_id={}
        # self.c.execute("SELECT tag_id FROM TAGS WHERE description='{}'".format(tag))
        # curr_tag_id=self.c.fetchone()
        # curr_tag_id=curr_tag_id[0]
        # self.c.execute("SELECT * FROM IMAGE_TAG WHERE tag_id='{}'".format(curr_tag_id))
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
        if self.c.fetchone() is None:
            # print("NO MORE")
            self.c.execute('DELETE FROM TAGS WHERE tag_id={}'.format(tag_id))
            self.conn.commit()
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
            if tag is '':
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
        # self.c.execute("SELECT image_id FROM IMAGES WHERE filename='{}'".format(filename))
        # curr_image_id = self.c.fetchone()[0]
        # print(curr_image_id)
        self.c.execute('UPDATE IMAGES SET source="{}" WHERE filename="{}"'.format(source,filename))
        self.conn.commit()
            

    def exec_taging(self):
        list_of_files = (os.listdir(self.folder))
        random.shuffle(list_of_files)
        # print(len(list_of_files))
        
        for item in list_of_files:
            # print(os.getcwd()+'\\'+self.folder+'\\'+item)
            os.startfile(os.getcwd()+'\\'+self.folder+'\\'+item)
            self.c.execute("SELECT image_id FROM IMAGES WHERE filename='{}'".format(item))
            curr_image_id = self.c.fetchone()
            curr_image_id = curr_image_id[0]
            # print("Image: ",item," corresponds to ID:",curr_image_id)
            user_input = input("Enter Tags for current Video:")
            if user_input is 'q':
                return
            user_input = user_input.split(' ')
            # print("Applying tags: ", user_input, " to image")

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
        if curr_image_id is None:
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

# Using webview
# def start_app():
#     eel_thread = threading.Thread(target=eel_start) # Eel app start.
#     eel_thread.setDaemon(True)
#     eel_thread.start() # Run eel in a seperate thread.

#     webview_start() # Start pywebview web browser.

# def eel_start():
#     # EEL app start.
#     eel.init('web')
#     eel.start("main.html", port=8000, mode=None, shutdown_delay=0.0)

# def webview_start():
#     # pywebview start.
#     webview.create_window("App Name", "http://localhost:8000/main.html", frameless=True)
#     webview.start()
# #
# start_app()

#Using Electron


eel.init('web')
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


def close(event):
    sys.exit(0)

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
    eel.js_display_file(current_folder[current_index],current_db)
    eel.js_trigger_hover()
    py_get_tags()
    
@eel.expose
def py_right_control():
    global current_index
    if current_index+1 <= folder_size-1:
        current_index=current_index+1
    else:
        current_index=0
    
    if current_folder[current_index]=='none':
        print("Hidden post")
        py_right_control()
        return
    eel.js_display_file(current_folder[current_index],current_db)
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
    if len(filename) > 20:
        filename = filename[0:25]+'...'
        
    if len(source) > 20:
        source=source[0:20]+'...'
        
    eel.js_display_source(filename,source)

@eel.expose
def py_set_tags(tags):
    # print("TAGS RECIEVED: ",tags)
    filename = current_folder[current_index]
    the_db.tag_video(filename,tags)
    py_get_tags()
    py_right_control()

@eel.expose 
def py_set_source(source): 
    # print("Setting video source")
    print(source)
    filepath = current_folder[current_index]
    the_db.add_source(filepath,source)
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
    for item in current_folder[current_drawer_index:150]:
        # print(item)
        filename=item.split('\\')[-1]
        thumb_path='files/thumbs/'+current_db+'/'+filename.replace('.webm','.jpg').replace('.mp4','.jpg')
        eel.js_add_to_drawer(item,current_db,thumb_path)
        current_drawer_index+=1
    py_initial_routine()
    py_populate_tags()
    py_right_control()

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

        for item in current_folder[current_drawer_index:150]:
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
    # print("Deleting: ",input_filepath)
    # 'data-img':`files/${folder_choice}/`+e,
    #files/thumbs/${folder_choice}/`+e.replace('.webm','.jpg').replace('.mp4','.jpg')
    current_folder[current_folder.index(input_filepath)]='none'
    the_db.delete_image_from_db(input_filepath)
    filename=input_filepath.split('\\')[-1]
    thumbnail = 'files/thumbs/'+current_db+'/'+filename.replace(filename.split('.')[-1],'jpg')

    dirname = os.path.dirname(__file__)

    # filepath = os.path.join(dirname, 'web/'+filepath)
    thumbnail = os.path.join(dirname, 'web/'+thumbnail)
    if delete_locally:
        print("Deleting local files as well")
        os.remove(input_filepath)
        os.remove(thumbnail)
    # os.startfile(filepath)
    # os.startfile(thumbnail)

    
def write_source_to_file(filepath,source):
    curr = filepath
    filename=filepath.split('\\')[-1]
    print(curr)
    print(filename)
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
        if output is not '':
            print("FILE: ",filepath, "METADATA: ",output)

def generate_thumbnail():
    print("Generating Thumbnails")

    for filepath in current_folder:
        filename=filepath.split('\\')[-1]
        curr = filepath
        # print(curr)

        output='web/files/thumbs/'+current_db+'/'+filename.replace('.webm','.jpg').replace('.mp4','.jpg')
        # ffmpeg.input(curr).output(output).run()
        try:
            os.mkdir('web/files/thumbs/'+current_db)
        except:
            pass
        print('Input: ',curr, " OUTPUT: ",output)
        exts = filename.split('.')[-1]
        print(exts)
        size=(236,326)

        if not(exts == 'jpg' or exts == 'png' or exts == 'jpeg' or exts =='jfif'):
            
            subprocess.call(
            'ffmpeg -y -i "{}" -q:v 1 -vframes 1 "{}"'.format(curr, output))
            
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
                return e 

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

    # glob_pattern = os.path.join(test_folderpath, '*')
    # current_folder = sorted(glob(glob_pattern), key=os.path.getctime)
    # random.shuffle(current_folder)
    the_db = my_database(current_db)
    current_folder=the_db.get_folder_from_db()
    base_list=current_folder
    the_db.get_tag_list()
    folder_size = len(current_folder)
    print(folder_size, " images in folder")
    # generate_thumbnail()
    if gen_thumbs:
        generate_thumbnail()
    if shuffle:
        random.shuffle(current_folder)
    py_populate_drawer()
    # get_metadata()
    # py_right_control()

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
        if item.split('.')[-1] == 'db' and item.split('.')[0]!='crashlogs':
            existing_databases.append(item)
    eel.js_update_autocomplete(existing_databases)


eel.start('main.html',mode='electron',size=(909,690))
# py_initial_routine()
# py_initial_routine()
# while True:
#     eel.sleep(1)