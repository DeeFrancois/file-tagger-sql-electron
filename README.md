# File Tagger - Powered by SQL and Electron JS

A program built for organizing a folder of art references by specified descriptive tags.

![demo](https://github.com/DeeFrancois/FileTagger_ElectronVersion/blob/main/DocumentationImages/demo.png)

The interface allows you to easily add, remove, and sort by tags. It also allows specifying the source of the file. The information is stored in a database but can also be written into the metadata of the files as well* 

<sup>*Metadata manipulation currently only works for videos</sup>

## Motivation
One of my hobbies is digital painting so I needed a way to organize my reference photos. I was disapointed with the windows tagging system so I figured I'd just make my own. 

## Usage

![demo](https://github.com/DeeFrancois/FileTagger_ElectronVersion/blob/main/DocumentationImages/demo.gif)

## External Dependencies:
- Electron https://www.electronjs.org/docs/latest/tutorial/installation
- ffmpeg + ffprobe https://ffmpeg.org/download.html


## Main Python Dependencies:
- Python-Eel 
- Pillow
- SQLite3
- multiprocessing
- ...and some others that may or may not have required installation with pip, can't remember

requirements.txt file included so you use the following command to install them all:

    pip3 install -r requirements.txt

## How it works
- User Interface
    - The Python backend uses [Python-Eel](https://github.com/python-eel/Eel) to communicate with the Javascript frontend (Electron framework)
- SQL: 
    - The database schema is an implementation of the [Toxi Solution](http://howto.philippkeller.com/2005/04/24/Tags-Database-schemas/) which uses 3 tables to facilitate a many-to-many system. One table for Images, another for Tags, and then a third for Image-Tag relationships. "Adding tags to videos" really means creating a new entry in the IMAGE-TO-TAG table. This allows more comprehensive querying (like finding all images with x tag), and enables the ability to store more information about both Images and Tags (e.x Image source, tag priority)
- Metadata manipulation
    - The program uses the ffmpeg and ffprobe libraries to manipulate the metadata. Writing to the file is optional as it requires replacing the file with a new copy which may overwrite other potentially important metadata like dates.

## Current Issues
Not sure if I can deploy this as an exe at the moment and honestly, I don't really plan to try at the moment.

Licensed under the [MIT License](LICENSE).
