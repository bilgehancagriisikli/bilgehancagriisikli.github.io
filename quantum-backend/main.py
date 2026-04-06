import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit import QuantumCircuit

app = FastAPI()

# GÜVENLİK AYARI (CORS): GitHub Pages'ten gelen isteklere izin verir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# KRİTİK SATIR: Anahtarı kodun içine yazmıyoruz, "IBM_QUANTUM_TOKEN" adıyla sistemden çekiyoruz
IBM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")

# Servisi bu gizli anahtar ile başlatıyoruz
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_TOKEN)

@app.get("/run-quantum")
async def run_quantum():
    # En az yoğun gerçek cihazı seç
    backend = service.least_busy(simulator=False, operational=True)
    
    # 3 Qubitlik Zar Devresi
    qc = QuantumCircuit(3)
    qc.h([0, 1, 2])
    qc.measure_all()
    
    sampler = SamplerV2(backend)
    job = sampler.run([qc])
    result = job.result()[0]
    
    # Sonucu al ve sayıya çevir
    counts = result.data.meas.get_counts()
    bitstring = list(counts.keys())[0]
    decimal_value = int(bitstring, 2)
    
    return {
        "number": decimal_value, 
        "device": backend.name, 
        "status": "Success"
    }
