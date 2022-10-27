# File Tagging with SQL

A file tagging program for organization that uses SQL to create and manage your own filesystem. 

The interface allows you to easily add/remove tags, and sort by them as well. This can also be used to manipulate "title" metadata so that you can embed the source of the image/video into the file itself.

![demo](https://github.com/DeeFrancois/FileTagger_ElectronVersion/blob/main/DocumentationImages/demo.png)


## Motivation
One of my hobbies is digital painting so I needed a way to organize my reference photos. I was disapointed with the windows tagging system so I figured I'd just make my own. 

## How to use

![demo](https://github.com/DeeFrancois/FileTagger_ElectronVersion/blob/main/DocumentationImages/demo.png)


## How it works
- SQL: 
    - This is an implementation of the [Toxi Solution] which uses 3 tables to facilitate a many-to-many system. One table for Images, another for Tags, and then a third for Image-Tag relationships. "Adding tags to videos" really means creating a new entry in the IMAGE-TO-TAG table. This allows more comprehensive querying (like finding all images with x tag), and enables the ability to store more information about both Images and Tags (e.x Image source, tag priority)
- Metadata manipulation
    - It uses ffmpeg and ffprobe to check for existing metadata, and write specified data to the file. Writing to the file is optional as it requires replacing the file with a new copy which may overwrite other potentially important metadata like dates.
- Interface
    - Javascript front end with python backend thanks to python-eel. 

## Current Issues
Not sure if I can deploy this as an exe at the moment and honestly, I don't really plan to try at the moment.

Licensed under the [MIT License](LICENSE).
