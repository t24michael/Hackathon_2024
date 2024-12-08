from pytesseract import pytesseract
from spire.doc import *
from spire.doc.common import *
from PIL import Image
import os
from com import communication



def create_directory():
    directory = "Output"

    try:
        os.mkdir(directory)
        print(f"Directory '{directory}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory}' already exists.")
    except PermissionError:
        print(f"Unable to create '{directory}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return directory

class OCR_class:
    def __init__(self, file: str):
        self.file = file
        self.new_folder = None
        self.file_name = None
        self.dictionary_of_abbreviations = {"Name":"name",
                                            "Birthdate":"birthdate",
                                            "Gender":"gender",
                                            "Address":"address",
                                            "Phone Number":"phone_number",
                                            "Email":"email",
                                            "Past Medical Condition":"pmc",
                                            "Surgeries and Procedures":"sap",
                                            "Allergies":"allergies",
                                            "Smoking Status":"ss",
                                            "Alcohol Consumption":"ac",
                                            "Physical Activity":"pa",
                                            "Vital Signs":"vs",
                                            "Body Mass":"bm",
                                            "Laboratory Test Results":"ltr"}
        self.uid = None
        self.did = None

    def convert_from_docx_to_photo(self):
        self.file_name = self.file[self.file.index("_")+1:self.file.index("&")]
        self.did = self.file_name
        self.uid = self.file[self.file.index("&")+1:self.file.index(".")]
        document = Document()

        document.LoadFromFile(self.file)
        parent_folder = "Output"
        self.new_folder = os.path.join(parent_folder, self.file[:self.file.index(".")])
        print(f"Actual folder path : {self.new_folder}")
        os.makedirs(self.new_folder, exist_ok=True)
        for i in range(document.GetPageCount()):
            image_stream = document.SaveImageToStreams(i, ImageType.Bitmap)

            with open(f"{self.new_folder}/{self.file_name}-{i}.png".format(i), "wb") as imageFile:
                imageFile.write(image_stream.ToArray())

        document.Close()


    def optical_character_recog(self):
        full_text = []
        path_to_tes = r"C:\Users\Michael\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        pytesseract.tesseract_cmd = path_to_tes
        # print("TEST")
        files = os.listdir(self.new_folder)
        png_count = [file for file in files if file.endswith(".png")]
        for i in range(len(png_count)):
            # print("TEST 2 OCR")
            # print(f"Iteratia :{i}")
            img = Image.open(f"{self.new_folder}/{self.file_name}-{i}.png".format(i))

            text = pytesseract.image_to_string(img)

            lines = text.split("\n")

            full_text.extend(lines)

            # print(f"text OCR: {full_text}")


        with open(f"{self.new_folder}/output.txt", "w") as file:
            for line in full_text:
                file.write(line + "\n")

    def collect_data(self, table_name):
        com = communication(table_name)
        with open(f"{self.new_folder}/output.txt", "r") as file:
            lines = file.readlines()
        # print(f"collect_data: {lines}")
        extracted_data = {}
        for line in lines:
            line = line.strip()
            for abbr, full_name in self.dictionary_of_abbreviations.items():
                pos = line.lower().find(abbr.lower())
                if pos != -1:
                    print(line[pos + len(abbr) + 1:])
                    data_value = line[pos + len(abbr) + 1:].strip()
                    extracted_data[full_name] = data_value
        com.insert(self.uid, self.did, **extracted_data)




# word_name = communication(bucket_name = "medical_reports").download()
# ocr = OCR_class(word_name)
# create_directory()
# ocr.convert_from_docx_to_photo()
# ocr.optical_character_recog()
# ocr.collect_data("patient_table")




