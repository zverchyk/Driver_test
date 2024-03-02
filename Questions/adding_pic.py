import fitz

pdf_file = "Questions\Alberta-Basic-Licence-Drivers-Assessment-6 (1).pdf"
pdf_document = fitz.open(pdf_file)

# Iterate through each page
for page_num in range(len(pdf_document)):
    page = pdf_document.load_page(page_num)
    images = page.get_images(full=True)

    # Extract each image on the page
    for img_index, img_info in enumerate(images):
        base_image = pdf_document.extract_image(img_info[0])
        image_bytes = base_image["image"]

        # Save the image
        with open(f"image_{page_num}_{img_index}.png", "wb") as img_file:
            img_file.write(image_bytes)

# Close the PDF
pdf_document.close()