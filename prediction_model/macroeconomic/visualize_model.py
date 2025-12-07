"""
Visualize the efficacy of the realistic sentiment neural network model
"""

import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, precision_recall_curve
import itertools

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

print("=" * 80)
print("CREATING VISUALIZATIONS FOR SENTIMENT MODEL EFFICACY")
print("=" * 80)

# Load model and data
print("\nLoading model and data...")
model = tf.keras.models.load_model('crypto_sentiment_model.keras')

with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

with open('training_history.pkl', 'rb') as f:
    history = pickle.load(f)

df = pd.read_csv('crypto_sentiment_dataset.csv')

print("✓ Model and data loaded")

# Prepare test data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords', quiet=True)
stop_words = stopwords.words('english')

def preprocess(text):
    text = re.sub(r'@\S+|https?:\S+|http?:\S|[^A-Za-z0-9 ]+', ' ', str(text).lower()).strip()
    tokens = [token for token in text.split() if token not in stop_words]
    return " ".join(tokens)

df['text'] = df['text'].apply(preprocess)

train_data, test_data = train_test_split(df, test_size=0.2, random_state=42, stratify=df['sentiment'])

MAX_SEQUENCE_LENGTH = 30
x_test = pad_sequences(tokenizer.texts_to_sequences(test_data.text), maxlen=MAX_SEQUENCE_LENGTH)

encoder = LabelEncoder()
encoder.fit(train_data.sentiment.to_list())
y_test = encoder.transform(test_data.sentiment.to_list()).reshape(-1, 1)

# Get predictions
print("\nGenerating predictions...")
y_pred_proba = model.predict(x_test, verbose=0)
y_pred = (y_pred_proba > 0.5).astype(int)

print("✓ Predictions generated")

# Create main visualization
print("\nCreating visualizations...")
fig = plt.figure(figsize=(20, 12))

# 1. Training & Validation Loss
ax1 = plt.subplot(2, 3, 1)
plt.plot(history['loss'], label='Training Loss', linewidth=2, color='#2E86AB', marker='o', markersize=6)
plt.plot(history['val_loss'], label='Validation Loss', linewidth=2, color='#A23B72', marker='s', markersize=6)
plt.title('Model Loss Over Epochs', fontsize=14, fontweight='bold')
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Loss', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# 2. Training & Validation Accuracy
ax2 = plt.subplot(2, 3, 2)
plt.plot(history['accuracy'], label='Training Accuracy', linewidth=2, color='#2E86AB', marker='o', markersize=6)
plt.plot(history['val_accuracy'], label='Validation Accuracy', linewidth=2, color='#A23B72', marker='s', markersize=6)
plt.title('Model Accuracy Over Epochs', fontsize=14, fontweight='bold')
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Accuracy', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# 3. Confusion Matrix
ax3 = plt.subplot(2, 3, 3)
cm = confusion_matrix(y_test, y_pred)
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True, 
            xticklabels=['Negative', 'Positive'], 
            yticklabels=['Negative', 'Positive'],
            annot_kws={'size': 14, 'weight': 'bold'})
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.ylabel('True Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)

# Add percentage annotations
for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    plt.text(j + 0.5, i + 0.7, f'({cm_normalized[i, j]:.1%})',
             ha='center', va='center', fontsize=10, color='gray')

# 4. ROC Curve
ax4 = plt.subplot(2, 3, 4)
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)
plt.plot(fpr, tpr, color='#2E86AB', linewidth=2, label=f'ROC Curve (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--', linewidth=2, label='Random Classifier')
plt.fill_between(fpr, tpr, alpha=0.2, color='#2E86AB')
plt.title('ROC Curve', fontsize=14, fontweight='bold')
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# 5. Precision-Recall Curve
ax5 = plt.subplot(2, 3, 5)
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
avg_precision = np.mean(precision)
plt.plot(recall, precision, color='#A23B72', linewidth=2, label=f'PR Curve (Avg Precision = {avg_precision:.4f})')
plt.fill_between(recall, precision, alpha=0.2, color='#A23B72')
plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
plt.xlabel('Recall', fontsize=12)
plt.ylabel('Precision', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# 6. Prediction Distribution
ax6 = plt.subplot(2, 3, 6)
plt.hist(y_pred_proba[y_test.flatten() == 0], bins=20, alpha=0.6, label='Negative Class', color='#E63946', edgecolor='black')
plt.hist(y_pred_proba[y_test.flatten() == 1], bins=20, alpha=0.6, label='Positive Class', color='#06D6A0', edgecolor='black')
plt.axvline(x=0.5, color='black', linestyle='--', linewidth=2, label='Decision Boundary')
plt.title('Prediction Score Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Predicted Probability', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('model_efficacy_visualization.png', dpi=300, bbox_inches='tight')
print("✓ Main visualization saved as 'model_efficacy_visualization.png'")

# Print detailed metrics
print("\n" + "=" * 80)
print("MODEL PERFORMANCE METRICS")
print("=" * 80)

y_pred_labels = ['Positive' if score > 0.5 else 'Negative' for score in y_pred_proba]
print("\nClassification Report:")
print(classification_report(test_data.sentiment.to_list(), y_pred_labels, 
                          target_names=['Negative', 'Positive'], digits=4))

# Calculate additional metrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\nDetailed Metrics:")
print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"Recall:    {recall:.4f} ({recall*100:.2f}%)")
print(f"F1-Score:  {f1:.4f}")
print(f"ROC AUC:   {roc_auc:.4f}")

print("\nConfusion Matrix Breakdown:")
tn, fp, fn, tp = cm.ravel()
print(f"True Negatives:  {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Positives:  {tp}")

# Create additional metrics visualization
fig2 = plt.figure(figsize=(16, 6))

# 7. Learning Rate Schedule (if available)
ax7 = plt.subplot(1, 3, 1)
if 'lr' in history:
    plt.plot(history['lr'], linewidth=2, color='#F77F00', marker='o')
    plt.title('Learning Rate Schedule', fontsize=14, fontweight='bold')
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Learning Rate', fontsize=12)
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
else:
    # Show training progress instead
    epochs = range(1, len(history['loss']) + 1)
    plt.plot(epochs, history['loss'], 'o-', label='Training', color='#2E86AB', linewidth=2)
    plt.plot(epochs, history['val_loss'], 's-', label='Validation', color='#A23B72', linewidth=2)
    plt.title('Training Progress', fontsize=14, fontweight='bold')
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)

# 8. Model Confidence Distribution
ax8 = plt.subplot(1, 3, 2)
confidence = np.maximum(y_pred_proba, 1 - y_pred_proba)
plt.hist(confidence, bins=20, color='#06D6A0', edgecolor='black', alpha=0.7)
plt.title('Model Confidence Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Confidence Score', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.grid(True, alpha=0.3)

# 9. Performance Metrics Bar Chart
ax9 = plt.subplot(1, 3, 3)
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC AUC']
values = [accuracy, precision, recall, f1, roc_auc]
colors = ['#2E86AB', '#A23B72', '#F77F00', '#06D6A0', '#E63946']
bars = plt.bar(metrics, values, color=colors, edgecolor='black', linewidth=1.5)
plt.title('Model Performance Metrics', fontsize=14, fontweight='bold')
plt.ylabel('Score', fontsize=12)
plt.ylim(0, 1.1)
plt.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'{value:.4f}',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('model_additional_metrics.png', dpi=300, bbox_inches='tight')
print("✓ Additional metrics visualization saved as 'model_additional_metrics.png'")

print("\n" + "=" * 80)
print("✓ ALL VISUALIZATIONS COMPLETE")
print("=" * 80)
print(f"\nModel Summary:")
print(f"  Dataset: {len(df)} articles (80/20 train/test split)")
print(f"  Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  ROC AUC: {roc_auc:.4f}")
print(f"  Training Epochs: {len(history['loss'])}")
print(f"  GloVe Embeddings: 300d (frozen)")
print("=" * 80 + "\n")
