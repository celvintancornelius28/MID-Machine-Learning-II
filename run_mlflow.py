import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import mlflow
import mlflow.sklearn

# ==========================================
# 1. PERSIAPAN DATASET
# ==========================================
print("Membaca dataset...")
# Ganti 'dataset.csv' dengan path atau nama file dataset IoT aslimu yang ada di folder VS Code
df = pd.read_csv('G:\ml\Preprocessed_Balanced_dataset (1).csv') 

# Asumsi fitur target berada di kolom paling akhir
target_col = df.columns[-1]
X = df.drop(columns=[target_col])
y = df[target_col]

# Membagi data (Stratified agar seimbang, pastikan random_state sama dengan di Kaggle)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ==========================================
# 2. KONFIGURASI MLFLOW TRACKING
# ==========================================
# Membuat atau mengatur experiment di MLflow
mlflow.set_experiment("IoT_Vulnerability_Detection")

print("Memulai sesi MLflow Tracking...")
# Memulai run MLflow
with mlflow.start_run(run_name="Best_Embedded_Pipeline"):
    
    # ==========================================
    # 3. DEFINISI PARAMETER TERBAIK (STATIS)
    # ==========================================
    # ⚠️ PENTING: Ganti angka-angka di bawah ini sesuai dengan output Tahap 7 di Kaggle!
    best_params = {
        'max_features': None,    # Ganti dengan nilai feature_selection__max_features
        'n_estimators': 200,   # Ganti dengan nilai model__n_estimators
        'max_depth': None,       # Ganti dengan nilai model__max_depth
        'min_samples_split': 2 # Ganti dengan nilai model__min_samples_split
    }
    
    print("Membangun arsitektur Pipeline...")
    # ==========================================
    # 4. REKONSTRUKSI PIPELINE PEMENANG
    # ==========================================
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        # Feature Selection (Embedded Method)
        ('feature_selection', SelectFromModel(
            RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            max_features=best_params['max_features']
        )),
        # Model Utama
        ('model', RandomForestClassifier(
            n_estimators=best_params['n_estimators'],
            max_depth=best_params['max_depth'],
            min_samples_split=best_params['min_samples_split'],
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    # ==========================================
    # 5. PELATIHAN DAN EVALUASI
    # ==========================================
    print("Melatih pipeline secara statis (Harap tunggu)...")
    pipeline.fit(X_train, y_train)
    
    print("Mengeksekusi prediksi pada Test Set...")
    y_pred = pipeline.predict(X_test)
    
    # Menghitung metrik performa
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'f1_score_macro': f1_score(y_test, y_pred, average='macro'),
        'precision_macro': precision_score(y_test, y_pred, average='macro'),
        'recall_macro': recall_score(y_test, y_pred, average='macro')
    }
    
    # ==========================================
    # 6. LOGGING KE MLFLOW
    # ==========================================
    print("Mencatat (logging) parameter dan metrik ke MLflow...")
    # Mencatat hyperparameter
    mlflow.log_params(best_params)
    # Mencatat skor metrik
    mlflow.log_metrics(metrics)
    
    # Menyimpan Artifact Model (Pipeline utuh) ke dalam MLflow
    mlflow.sklearn.log_model(pipeline, "best_pipeline_model")
    
    print("\n" + "="*50)
    print("✅ EKSEKUSI MLFLOW BERHASIL!")
    print("="*50)
    print(f"Akurasi Final yang tercatat : {metrics['accuracy']:.4f}")
    print(f"F1-Score Final yang tercatat: {metrics['f1_score_macro']:.4f}")