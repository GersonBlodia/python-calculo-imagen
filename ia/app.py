from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re

# Librerías para resolver ecuaciones
from sympy import symbols, Eq, solve

# Configurar ruta si Tesseract no está en el PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI()

# Permitir CORS para pruebas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def insertar_multiplicaciones_implicitas(expr: str) -> str:
    # Inserta * entre número y letra: 2x → 2*x
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)
    # También entre letra y número: x2 → x*2 (por si acaso)
    expr = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", expr)
    return expr


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    text = pytesseract.image_to_string(image)
    print("Texto extraído:", repr(text))

    operation = text.strip()
    operation = operation.replace("÷", "/").replace(",", ".")
    operation = re.sub(r"[^0-9a-zA-Z\+\-\*/\.\=\(\) ]", "", operation)

    try:
        if "=" in operation:
            # Resolver ecuación (no reemplazamos X por *)
            x = symbols('x')
            operation = operation.replace("X", "x")
            operation = insertar_multiplicaciones_implicitas(operation)  # 👈 Aquí la usamos
            left, right = operation.split("=")
            equation = Eq(eval(left), eval(right))
            result = solve(equation, x)
            return {
                "tipo": "ecuacion",
                "operacion": operation,
                "resultado": [str(r) for r in result]
            }
        else:
            # Reemplazar X por * en caso de operaciones (no ecuaciones)
            operation = operation.replace("X", "x")
            operation = insertar_multiplicaciones_implicitas(operation)  # 👈 también aquí
            operation = operation.replace("x", "*")
            result = eval(operation)
            return {
                "tipo": "operacion",
                "operacion": operation,
                "resultado": result
            }
    except Exception as e:
        return {
            "error": "No se pudo resolver",
            "mensaje": str(e),
            "operacion_detectada": operation
        }
