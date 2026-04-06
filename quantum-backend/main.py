from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit import QuantumCircuit

app = FastAPI()

# GitHub Pages'ten gelen isteklere izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Güvenlik için buraya kendi github.io adresini yazabilirsin
    allow_methods=["*"],
    allow_headers=["*"],
)

service = QiskitRuntimeService(channel="ibm_quantum", token="SENIN_IBM_TOKENIN")

@app.get("/run-quantum")
async def run_quantum():
    # En az yoğun gerçek cihazı seç
    backend = service.least_busy(simulator=False, operational=True)
    
    # Devre: 3 Qubit, her birine H kapısı (0-7 arası rastgelelik)
    qc = QuantumCircuit(3)
    qc.h([0, 1, 2])
    qc.measure_all()
    
    sampler = SamplerV2(backend)
    job = sampler.run([qc])
    result = job.result()[0]
    
    # Rastgele ölçülen bit dizisini al
    counts = result.data.meas.get_counts()
    bitstring = list(counts.keys())[0]
    decimal_value = int(bitstring, 2)
    
    return {"number": decimal_value, "device": backend.name, "job_id": job.job_id()}
