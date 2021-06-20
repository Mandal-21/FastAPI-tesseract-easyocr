from fastapi import FastAPI, File, UploadFile
import shutil
import os
import PIL
from PIL import Image
import pytesseract
from pytesseract import Output
import easyocr
import cv2

# pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'

app = FastAPI()

# New folder to save ocr images
if os.path.isdir("saved_images"):
    pass
else:
    os.mkdir("saved_images")


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    if os.path.isdir("image"):
        pass
    else:
        os.mkdir("image")
    filename = f"image/{file.filename}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # output from tesseract and easyocr
    op_tesseract = pytesseract.image_to_string(filename)
    op_easyocr = easyocr.Reader(["en"]).readtext(filename, paragraph=True)

    # Getting bounding boxes from easyocr
    cord_ocr = op_easyocr[-1][0]
    x_min, y_min = [min(idx) for idx in zip(*cord_ocr)]  # min cord
    x_max, y_max = [max(idx) for idx in zip(*cord_ocr)]  # max cord

    img_ocr = cv2.imread(filename)
    cv2.rectangle(img_ocr, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2) # get the bounding box on image
    cv2.imwrite("saved_images/easyocr.png", img_ocr) # save the image

    # Getting bounding boxes from tesseract
    img_tesseract = cv2.imread(filename)  # read image
    d = pytesseract.image_to_data(Image.open(filename), output_type=Output.DICT) # dict-form boundary
    n_boxes = len(d['level']) # find the text box

    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], 
                        d['width'][i], d['height'][i])
        cv2.rectangle(img_tesseract, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite('saved_images/tesseract.png', img_tesseract)

    return {
        "Tesseract": op_tesseract,
        "EasyOcr": op_easyocr[-1][-1]
    }