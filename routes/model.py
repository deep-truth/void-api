import torch
import nemo.collections.asr as nemo_asr

model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(
    "nvidia/speakerverification_en_titanet_large"
)


def predict(audio_file1, audio_file2, use_get_score=False):
    emb1 = model.get_embedding(audio_file1)
    emb2 = model.get_embedding(audio_file2)

    if use_get_score:
        return get_score(emb1, emb2)

    return get_cosine_similariy(emb1, emb2)


def get_cosine_similariy(embs1, embs2):
    cosine_sim = torch.nn.CosineSimilarity(dim=-1)
    similarity = cosine_sim(embs1, embs2)

    return similarity


def get_score(embs1, embs2):
    X = embs1 / torch.linalg.norm(embs1)
    Y = embs2 / torch.linalg.norm(embs2)

    # Score
    similarity_score = torch.dot(X, Y) / ((torch.dot(X, X) * torch.dot(Y, Y)) ** 0.5)
    similarity_score = (similarity_score + 1) / 2
    print(similarity_score)
    return similarity_score
