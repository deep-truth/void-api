import os
import requests

# firebase
from firebase_admin import storage

# model libs
import torch
import nemo.collections.asr as nemo_asr

# utls
from utils.firebase import init_firebase

model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(
    "nvidia/speakerverification_en_titanet_large"
)
init_firebase()
bucket = storage.bucket(name="deeptruth-fb46f.appspot.com")


def process_and_score(url1, url2):
    AUDIO1 = "tmp/audio1.wav"
    AUDIO2 = "tmp/audio2.wav"

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    _download_blob(url1, AUDIO1)
    _download_blob(url2, AUDIO2)

    score = get_score(AUDIO1, AUDIO2)
    os.remove(AUDIO1)
    os.remove(AUDIO2)
    os.removedirs("tmp")

    print(f"score TEST {score}")
    return score


def _download_blob(source, dest):
    blob = bucket.blob(source)
    blob.download_to_filename(dest)


def get_score(audio_file1, audio_file2, use_dot_score=False):
    emb1 = model.get_embedding(audio_file1)
    emb2 = model.get_embedding(audio_file2)

    if use_dot_score:
        return get_dot_score(emb1, emb2)

    return get_cos_score(emb1, emb2)


def get_cos_score(embs1, embs2):
    cosine_sim = torch.nn.CosineSimilarity(dim=-1)
    similarity = cosine_sim(embs1, embs2)

    return similarity


def get_dot_score(embs1, embs2):
    X = embs1 / torch.linalg.norm(embs1)
    Y = embs2 / torch.linalg.norm(embs2)

    # Score
    similarity_score = torch.dot(X, Y) / ((torch.dot(X, X) * torch.dot(Y, Y)) ** 0.5)
    similarity_score = (similarity_score + 1) / 2
    print(similarity_score)
    return similarity_score
