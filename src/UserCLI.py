from FileData import *
import os

class UserCLI:
    def __init__ (self):
        self.fileData = FileData()

    def addFile (self):
        while True:
            fileName = input("Please enter file path ")
            fileName.replace('\\', '\\\\')
            if not os.path.exists(fileName):
                print("File {} does not exist. Try again".format(fileName))
                continue
            else:
                break
        self.fileData.location = fileName

    def selectFileExtension (self):
        while True:
            extension = input("Please enter your desired extension. You may choose between: mp4, avi, webm, wmv ")
            if extension not in ['mp4', 'avi', 'webm', 'wmv']:
                print("Extension is not valid. Try again")
                continue
            else:
                break
        self.fileData.fileExtension = extension

    def selectResolution (self):
        while True:
            try:
                width = int(input("Enter your desired width "))
            except ValueError:
                print("Width incorrect. Try again")
                continue
            else:
                break
        self.fileData.resolution.append(width)
        while True:
            try:
                height = int(input("Enter your desired height "))
            except ValueError:
                print("Height incorrect. Try again")
                continue
            else:
                break
        self.fileData.resolution.append(height)

    def setSaveLocation (self):
        while True:
            saveLocation = input("Enter location where your file will be saved after conversion ")
            if not os.path.isdir(saveLocation):
                print("Path incorrect. Try again")
                continue
            else:
                break
        self.fileData.saveLocation = saveLocation

    def setFileData (self):
        self.addFile()
        self.selectFileExtension()
        self.selectResolution()
        self.setSaveLocation()
