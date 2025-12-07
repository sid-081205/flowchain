"""
Download and prepare GloVe embeddings for sentiment analysis
"""

import os
import requests
import zipfile
import numpy as np
from tqdm import tqdm

def download_glove(output_dir='.'):
    """Download GloVe 6B embeddings from Stanford NLP"""
    
    url = "http://nlp.stanford.edu/data/glove.6B.zip"
    zip_path = os.path.join(output_dir, "glove.6B.zip")
    
    print("=" * 80)
    print("DOWNLOADING GLOVE EMBEDDINGS")
    print("=" * 80)
    print(f"\nSource: {url}")
    print(f"Destination: {zip_path}")
    print("\nThis may take several minutes (~822MB download)...\n")
    
    # Check if already downloaded
    if os.path.exists(zip_path):
        print(f"✓ {zip_path} already exists. Skipping download.")
    else:
        # Download with progress bar
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading') as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        print(f"\n✓ Download complete: {zip_path}")
    
    return zip_path

def extract_glove(zip_path, output_dir='.'):
    """Extract GloVe embeddings"""
    
    print("\n" + "=" * 80)
    print("EXTRACTING GLOVE EMBEDDINGS")
    print("=" * 80)
    
    # Check if already extracted
    glove_300d = os.path.join(output_dir, "glove.6B.300d.txt")
    if os.path.exists(glove_300d):
        print(f"\n✓ {glove_300d} already exists. Skipping extraction.")
        return glove_300d
    
    print(f"\nExtracting {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all files
        zip_ref.extractall(output_dir)
    
    print(f"✓ Extraction complete")
    print(f"\nExtracted files:")
    for file in ['glove.6B.50d.txt', 'glove.6B.100d.txt', 'glove.6B.200d.txt', 'glove.6B.300d.txt']:
        filepath = os.path.join(output_dir, file)
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  - {file} ({size_mb:.1f} MB)")
    
    return glove_300d

def load_glove_embeddings(glove_path):
    """Load GloVe embeddings into memory"""
    
    print("\n" + "=" * 80)
    print("LOADING GLOVE EMBEDDINGS")
    print("=" * 80)
    print(f"\nLoading from: {glove_path}")
    print("This may take a minute...\n")
    
    embeddings_index = {}
    
    with open(glove_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc='Loading embeddings', unit=' words'):
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
    
    print(f"\n✓ Loaded {len(embeddings_index):,} word vectors")
    print(f"  Embedding dimension: {len(next(iter(embeddings_index.values())))}")
    
    return embeddings_index

def test_embeddings(embeddings_index):
    """Test embeddings with sample words"""
    
    print("\n" + "=" * 80)
    print("TESTING EMBEDDINGS")
    print("=" * 80)
    
    test_words = ['bitcoin', 'cryptocurrency', 'bullish', 'bearish', 'crash', 'surge']
    
    print("\nSample word vectors:")
    for word in test_words:
        if word in embeddings_index:
            vector = embeddings_index[word]
            print(f"  ✓ '{word}': {vector[:5]}... (dim={len(vector)})")
        else:
            print(f"  ✗ '{word}': Not found in GloVe vocabulary")
    
    # Calculate similarity example
    if 'bullish' in embeddings_index and 'bearish' in embeddings_index:
        vec1 = embeddings_index['bullish']
        vec2 = embeddings_index['bearish']
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        print(f"\nCosine similarity between 'bullish' and 'bearish': {similarity:.4f}")

def main():
    """Main execution function"""
    
    output_dir = '.'
    
    # Download GloVe
    zip_path = download_glove(output_dir)
    
    # Extract GloVe
    glove_300d_path = extract_glove(zip_path, output_dir)
    
    # Load and test embeddings
    embeddings_index = load_glove_embeddings(glove_300d_path)
    test_embeddings(embeddings_index)
    
    print("\n" + "=" * 80)
    print("✓ GLOVE EMBEDDINGS READY")
    print("=" * 80)
    print(f"\nPath: {glove_300d_path}")
    print(f"Vocabulary size: {len(embeddings_index):,} words")
    print(f"Embedding dimension: 300")
    print("\nYou can now use these embeddings in your model training.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
