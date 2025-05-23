import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Convert a book file (EPUB, FB2, PDF) to an MP3 audiobook.")
    
    parser.add_argument("input_file", 
                        help="Path to the input book file (e.g., EPUB, FB2, PDF).")
    
    parser.add_argument("--output_file", 
                        help="Optional: Desired name for the output MP3 file. "
                             "If not provided, it defaults to the input file name with an .mp3 extension.")
    
    parser.add_argument("--lang", 
                        default='en', 
                        help="Optional: Language for the text-to-speech conversion (e.g., 'en', 'es'). Defaults to 'en'.")
    
    args = parser.parse_args()
    
    # Determine default output file name if not provided
    output_file = args.output_file
    if not output_file:
        base, ext = os.path.splitext(args.input_file)
        output_file = base + ".mp3"
        
    print(f"Input file: {args.input_file}")
    print(f"Output file: {output_file}") # Print the processed output_file name
    print(f"Language: {args.lang}")

    # Placeholder for future logic
    # print("\nFurther processing would happen here...")

if __name__ == '__main__':
    main()
