import pandas as pd
import re
import tarfile
import os



def get_data(base_path = './data/parlamint_at_extracted/ParlaMint-AT.txt'):
    """
    Function to retrieve data from a source.
    This is a placeholder function and should be implemented with actual data retrieval logic.
    """
    print(f"Retrieving data from ParlaMint-AT...")
    with tarfile.open('./data/ParlaMint-AT.tgz', 'r:gz') as tar:
        tar.extractall('./data/parlamint_at_extracted')
    for root, dirs, files in os.walk('./data/parlamint_at_extracted'):
        for file in files:
            print(os.path.join(root, file))

    def clean_text(text):
        return re.sub(r'\[\[.*?\]\]', '', text).strip()

    def process_text_and_meta(txt_path, meta_path):
        # read text file as a dict with ID as key and text as value
        speech_df = pd.read_csv(txt_path, sep='\t', header=None, names=['ID', 'text'], encoding='utf-8')
        meta_df = pd.read_csv(meta_path, sep='\t', encoding='utf-8', index_col=False)
        combined_df = pd.merge(speech_df, meta_df, on='ID', how='left')
        combined_df['text'] = combined_df['text'].apply(clean_text)
        return combined_df

    def load_parlamint_corpus(base_dir):
        all_records = []

        for root, _, files in os.walk(base_dir):
            txt_files = [f for f in files if f.endswith('.txt') and not f.startswith('00README')]

            # Process only .txt files that are inside directories (ParlaMint-AT_xxxxx)
            for txt_file in txt_files:
                if '-meta-en.tsv' in txt_file:
                    continue  # Skip metadata files that might have .txt in folder names

                txt_path = os.path.join(root, txt_file)

                # Try to extract session identifier: remove extensions and extra path
                base_id = os.path.splitext(txt_file)[0].replace('.txt', '')
                base_id_parts = base_id.split('/')
                if len(base_id_parts) > 1:
                    base_id = base_id_parts[-1]

                # Look for corresponding metadata file in same dir
                meta_filename = f"{base_id}-meta-en.tsv"
                meta_path = os.path.join(root, meta_filename)

                if os.path.exists(meta_path):
                    try:
                        merged_df = process_text_and_meta(txt_path, meta_path)
                        all_records.append(merged_df)
                        print(f"Processed: {txt_file}")
                    except Exception as e:
                        print(f"Failed to process {txt_file}: {e}")
                else:
                    print(f"Skipped {txt_file}: No matching metadata found ({meta_filename})")

        if not all_records:
            raise ValueError("No valid files processed. Check structure and naming.")

        return pd.concat(all_records, ignore_index=True)
    return load_parlamint_corpus(base_path)
