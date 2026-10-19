from pdf2docx import Converter
import os
import io
import logging
from contextlib import redirect_stdout, redirect_stderr

logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("pdf2docx").setLevel(logging.ERROR)


def convert_pdf_to_word(participant_name):

    pdf_file = f"output/{participant_name}_360°_Feedback Report.pdf"

    word_file = f"output/{participant_name}_360°_Feedback Report.docx"

    if not os.path.exists(pdf_file):
        print(f"PDF not found: {pdf_file}")
        return

    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        cv = Converter(pdf_file)
        cv.convert(word_file)
        cv.close()

    print(f"✅ Word created: {word_file}")