import xra

import time
from storage3.utils import StorageException
from supabase import create_client, Client
import os
from dotenv import load_dotenv

from com import communication
import OCR

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

oldname = None
oldname_ocr = None
skip = True
skip_ocr = True

if __name__ == "__main__":
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    model = xra.Xra()
    model.init()

    oldname2 = ""
    skip = 0

    while True:
        response = supabase.table("storage") \
            .select("*") \
            .eq("type", "rmn") \
            .order("created_at", desc=True) \
            .execute()
        name = f"{response.data[0]['file_name']}"

        if name != oldname2 and skip:
            try:
                with open(f"{name}.png", "wb+") as f:
                    response = supabase.storage.from_("xra").download(
                        name
                    )
                    f.write(response)
            except StorageException:
                print("The file doesn't exist!")
            rez = model.evaluate(f"{name}.png")

            _, uid = f"{name}.png".split('&', 1)
            uid, _ = uid.split('.', 1)
            did, _ = f"{name}.png".split('_', 1)
            print(uid, did)
            response = (
                supabase.table("xray-rez")
                .insert({"rez": rez, "file_name": f"{name}.png", "uid": f"{name}.png", "did": did})
                .execute()
            )

            os.remove(f"{name}.png")

            oldname2 = name
        skip = 1


        print("TIME STARTED!")
        word_name = communication(bucket_name="medical_reports").download()
        print(word_name)

        if word_name != oldname_ocr and skip_ocr:
            ocr = OCR.OCR_class(word_name)
            OCR.create_directory()
            ocr.convert_from_docx_to_photo()
            ocr.optical_character_recog()
            ocr.collect_data("patient_table")

            oldname_ocr = word_name

        time.sleep(2)

