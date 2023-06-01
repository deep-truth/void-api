import os
import requests

import torch
import nemo.collections.asr as nemo_asr

model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(
    "nvidia/speakerverification_en_titanet_large"
)


def process_and_score(url1, url2):
    req1 = requests.get(url1)
    req2 = requests.get(url2)
    AUDIO1 = "tmp/audio1.wav"
    AUDIO2 = "tmp/audio2.wav"

    with open(AUDIO1, "wb") as file:
        file.write(req1.content)

    with open(AUDIO2, "wb") as file:
        file.write(req2.content)

    score = get_score(AUDIO1, AUDIO2)
    os.remove(AUDIO1)
    os.remove(AUDIO2)

    return score


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
