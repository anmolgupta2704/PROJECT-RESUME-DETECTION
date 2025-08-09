from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def encode_text(text):
    return model.encode(text, convert_to_tensor=True)

def compute_similarity(text1, text2):
    emb1 = encode_text(text1)
    emb2 = encode_text(text2)
    return util.cos_sim(emb1, emb2).item()
