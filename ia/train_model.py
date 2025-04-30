from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib

# Cargar el dataset de dígitos
digits = datasets.load_digits()
X = digits.data
y = digits.target

# Dividir los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear y entrenar un modelo SVM
model = SVC(gamma=0.001)
model.fit(X_train, y_train)

# Guardar el modelo entrenado
joblib.dump(model, 'svm_digit_model.pkl')

print("Modelo SVM entrenado y guardado como svm_digit_model.pkl en el directorio actual.")