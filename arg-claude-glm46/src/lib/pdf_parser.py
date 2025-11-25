"""PDF parsing functionality using PyMuPDF."""

import fitz  # PyMuPDF
from typing import List, Dict


def parse_pdf_to_markdown(file_path: str) -> str:
    """
    Parse a PDF file and extract content in markdown format.

    Args:
        file_path (str): Path to the PDF file

    Returns:
        str: Extracted content in markdown format

    Raises:
        FileNotFoundError: If the PDF file is not found
        Exception: If there's an error parsing the PDF
    """
    try:
        # Open the PDF file
        doc = fitz.open(file_path)

        # Extract text from all pages
        text_content = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_content.append(f"## Page {page_num + 1}\n\n{text}")

        doc.close()

        # Join all pages with double newlines
        return "\n\n".join(text_content)

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error parsing PDF file: {str(e)}")


def extract_images_from_pdf(file_path: str) -> List[Dict]:
    """
    Extract images from a PDF file.

    Args:
        file_path (str): Path to the PDF file

    Returns:
        List[Dict]: List of extracted images with metadata

    Raises:
        FileNotFoundError: If the PDF file is not found
        Exception: If there's an error extracting images
    """
    try:
        doc = fitz.open(file_path)
        images = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                images.append({
                    "page": page_num + 1,
                    "index": img_index,
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "extension": base_image["ext"],
                    "data": image_bytes
                })

        doc.close()
        return images

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error extracting images from PDF: {str(e)}")