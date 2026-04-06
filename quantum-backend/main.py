import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit import QuantumCircuit, transpile # Transpile eklendi
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IBM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_TOKEN)

@app.get("/run-quantum")
async def run_quantum():
    # En az yoğun gerçek cihazı seçiyoruz
    backend = service.least_busy(simulator=False, operational=True)
    
    # 1. Devreyi oluştur
    qc = QuantumCircuit(3)
    qc.h([0, 1, 2])
    qc.measure_all()
    
    # 2. KRİTİK ADIM: Devreyi hedef donanıma göre dönüştür (Transpile)
    # Bu adım 'h' kapısını donanımın anladığı temel kapılara (örn: sx, rz) çevirir
    transpiled_circuit = transpile(qc, backend=backend)
    
    # 3. Çalıştır (SamplerV2 kullanıyoruz)
    sampler = SamplerV2(backend)
    job = sampler.run([transpiled_circuit])
    result = job.result()[0]
    
    # Sonucu işle
    counts = result.data.meas.get_counts()
    bitstring = list(counts.keys())[0]
    decimal_value = int(bitstring, 2)
    
    return {
        "number": decimal_value, 
        "device": backend.name,
        "status": "Success"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
