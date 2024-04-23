import barcode
from barcode import Code128
from barcode.writer import ImageWriter

def generate_barcode(barcode_number, filename):
    # Generate the barcode object
    code128 = barcode.get('code128', barcode_number, writer=ImageWriter())
    # Save the barcode image
    code128.save(filename)

# List of barcode numbers
barcode_numbers = [
"2344"
]

for i , barcode_number in enumerate(barcode_numbers, start=4):
    filename = f"barcode_{i}.png"
    generate_barcode(barcode_number, filename)
    print(f"Barcode image generated for {barcode_number}. Saved as {filename}")
