import os
from final_pdf_processor import process_pdf

def main():
    input_dir = "input_pdfs"
    output_dir = "output_jsons"

    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.replace(".pdf", ".json"))
            try:
                process_pdf(input_path, output_path)
            except Exception as e:
                print(f"❌ Failed to process {file}: {e}")

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # For Windows support when frozen into .exe
    main()
