"""
Train realistic LSTM sentiment model with GloVe embeddings
"""

import tensorflow as tf
import pandas as pd
import numpy as np
import re
import pickle
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Conv1D, Bidirectional, LSTM, Dense, Input, Dropout, SpatialDropout1D, Embedding
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from tensorflow.keras.optimizers import Adam
from tqdm import tqdm

# Download NLTK data
nltk.download('stopwords', quiet=True)

print("=" * 80)
print("REALISTIC CRYPTOCURRENCY SENTIMENT ANALYSIS MODEL")
print("=" * 80)
print(f"TensorFlow Version: {tf.__version__}\n")

# Load dataset
print("Loading dataset...")
df = pd.read_csv('crypto_sentiment_dataset.csv')
print(f"✓ Loaded {len(df)} articles")
print(f"  Positive: {len(df[df['sentiment'] == 'Positive'])}")
print(f"  Negative: {len(df[df['sentiment'] == 'Negative'])}")

# Preprocessing
stop_words = stopwords.words('english')

def preprocess(text):
    """Clean and preprocess text"""
    text = re.sub(r'@\S+|https?:\S+|http?:\S|[^A-Za-z0-9 ]+', ' ', str(text).lower()).strip()
    tokens = [token for token in text.split() if token not in stop_words]
    return " ".join(tokens)

print("\nPreprocessing text...")
df['text'] = df['text'].apply(preprocess)
df['text_length'] = df['text'].apply(lambda x: len(x.split()))
print(f"✓ Preprocessing complete")
print(f"  Average text length: {df['text_length'].mean():.1f} words")

# Train-Test Split
TRAIN_SIZE = 0.8
MAX_SEQUENCE_LENGTH = 30
EMBEDDING_DIM = 300

print(f"\nSplitting data ({TRAIN_SIZE*100:.0f}% train, {(1-TRAIN_SIZE)*100:.0f}% test)...")
train_data, test_data = train_test_split(df, test_size=1-TRAIN_SIZE, random_state=42, stratify=df['sentiment'])
print(f"✓ Train: {len(train_data)}, Test: {len(test_data)}")

# Tokenization
print("\nTokenizing text...")
tokenizer = Tokenizer()
tokenizer.fit_on_texts(train_data.text)

vocab_size = len(tokenizer.word_index) + 1
print(f"✓ Vocabulary Size: {vocab_size}")

x_train = pad_sequences(tokenizer.texts_to_sequences(train_data.text), maxlen=MAX_SEQUENCE_LENGTH)
x_test = pad_sequences(tokenizer.texts_to_sequences(test_data.text), maxlen=MAX_SEQUENCE_LENGTH)

# Encode labels
encoder = LabelEncoder()
encoder.fit(train_data.sentiment.to_list())

y_train = encoder.transform(train_data.sentiment.to_list()).reshape(-1, 1)
y_test = encoder.transform(test_data.sentiment.to_list()).reshape(-1, 1)

print(f"✓ x_train: {x_train.shape}, y_train: {y_train.shape}")

# Load GloVe embeddings
print("\n" + "=" * 80)
print("Loading GloVe embeddings...")
print("=" * 80)

GLOVE_PATH = 'glove.6B.300d.txt'
embeddings_index = {}

with open(GLOVE_PATH, 'r', encoding='utf-8') as f:
    for line in tqdm(f, desc='Loading GloVe', total=400000):
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs

print(f"✓ Loaded {len(embeddings_index):,} word vectors")

# Create embedding matrix
print("\nCreating embedding matrix...")
embedding_matrix = np.zeros((vocab_size, EMBEDDING_DIM))
words_found = 0

for word, i in tokenizer.word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector
        words_found += 1

print(f"✓ Embedding matrix created: {embedding_matrix.shape}")
print(f"  Words found in GloVe: {words_found}/{vocab_size-1} ({words_found/(vocab_size-1)*100:.1f}%)")

# Build Model
print("\n" + "=" * 80)
print("Building model...")
print("=" * 80)

LR = 1e-3
BATCH_SIZE = 16  # Smaller batch size for small dataset
EPOCHS = 15

sequence_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
embedding_layer = Embedding(vocab_size, 
                            EMBEDDING_DIM, 
                            weights=[embedding_matrix],
                            trainable=False)(sequence_input)  # Freeze embeddings
x = SpatialDropout1D(0.2)(embedding_layer)
x = Conv1D(64, 5, activation='relu')(x)
x = Bidirectional(LSTM(64, dropout=0.2, recurrent_dropout=0.2))(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(512, activation='relu')(x)
outputs = Dense(1, activation='sigmoid')(x)

model = tf.keras.Model(sequence_input, outputs)
model.compile(optimizer=Adam(learning_rate=LR), loss='binary_crossentropy', metrics=['accuracy'])

print("\nModel Architecture:")
model.summary()

# Callbacks
reduce_lr = ReduceLROnPlateau(factor=0.1, min_lr=0.00001, monitor='val_loss', verbose=1, patience=3)
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1)

# Train Model
print("\n" + "=" * 80)
print("Training model...")
print("=" * 80)

history = model.fit(
    x_train, y_train, 
    batch_size=BATCH_SIZE, 
    epochs=EPOCHS,
    validation_data=(x_test, y_test), 
    callbacks=[reduce_lr, early_stop],
    verbose=1
)

print("\n✓ Training complete!")

# Evaluate
print("\n" + "=" * 80)
print("Evaluating model...")
print("=" * 80)

scores = model.predict(x_test, verbose=0)
y_pred = (scores > 0.5).astype(int)

def decode_sentiment(score):
    return "Positive" if score > 0.5 else "Negative"

y_pred_labels = [decode_sentiment(score[0]) for score in scores]

print("\nClassification Report:")
print(classification_report(test_data.sentiment.to_list(), y_pred_labels, 
                          target_names=['Negative', 'Positive'], digits=4))

accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

# Save Model
print("\n" + "=" * 80)
print("Saving model...")
print("=" * 80)

model.save('crypto_sentiment_model.keras')
print("✓ Model saved to 'crypto_sentiment_model.keras'")

with open('tokenizer.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)
print("✓ Tokenizer saved to 'tokenizer.pkl'")

# Save training history
with open('training_history.pkl', 'wb') as f:
    pickle.dump(history.history, f)
print("✓ Training history saved to 'training_history.pkl'")

print("\n" + "=" * 80)
print("✓ MODEL TRAINING COMPLETE")
print("=" * 80)
print(f"\nFinal Metrics:")
print(f"  Test Accuracy: {accuracy:.4f}")
print(f"  Training Epochs: {len(history.history['loss'])}")
print(f"  Final Training Loss: {history.history['loss'][-1]:.4f}")
print(f"  Final Validation Loss: {history.history['val_loss'][-1]:.4f}")
print("=" * 80 + "\n")
