import time
import faiss
import numpy as np
# ============== step 1: gen ==========
d = 64
nb = 10000
nq = 5
np.random.seed(123)
# ============== step 2: random ==========
xb = np.random.random((nb, d)).astype('float32')
xb[:, 0] += np.arange(nb) / 1000
xq = np.random.random((nq, d)).astype('float32')
xq[:, 0] += np.arange(nq) / 1000
# =========== step 3: create IVF =====================
nlist = 100
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist)
# ================ step 4: train the index ============
print("training index........")
index.train(xb)
print("Is trained:", index.is_trained)
# ========== step 5: add data vector =========
index.add(xb)
print("Total vector in index:", index.ntotal)
# ========== step 6: search with default nprobe = 1 
k = 4
D, I = index.search(xq, k)
print("\nSearch result (nprobe=1):")
print(I)
# step 7: Increase nprobe to search in more clusters ======
index.nprobe = 10 # seach across 10 clusters
D, I = index.search(xq, k)
print("\nSearch result (nprobe=10):")
print(I)