# pip install rouge-score
# pip install pycocoevalcap

import re
import nltk
import pandas as pd
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
from rouge_score import rouge_scorer
from pycocoevalcap.cider.cider import Cider
from nltk.translate.meteor_score import meteor_score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

nltk.download('wordnet')
nltk.download('omw-1.4')

PETER_GENERATED_PATH = 'generated/PETER_generated.txt'
NRT_GENERATED_PATH = 'generated/NRT_generated.txt'
ATT2SEQ_GENERATED_PATH = 'generated/Att2seq_generated.txt'
PEPLER_GENERATED_PATH = 'generated/PEPLERMLP.txt'
LLAMA3_GENERATED_PATH = 'generated/Llama3_generated.txt'


def extract_reviews(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    reviews = []
    review = []

    for line in lines:
        line = line.strip()
        if line.startswith("The video is is the the the"):
            reviews.append(" ".join(review).strip())
            review = []
        else:
            review.append(line)

    if review:
        reviews.append(" ".join(review).strip())

    return reviews

def calculate_bleu1_score(generated_reviews, reference_reviews):

    smoothie = SmoothingFunction().method1
    bleu1_scores = []
    
    for generated, reference in zip(generated_reviews, reference_reviews):
        generated_tokens = generated.split()
        reference_tokens = [reference.split()]
        
        score = sentence_bleu(reference_tokens, generated_tokens, weights=(1, 0, 0, 0), smoothing_function=smoothie)
        bleu1_scores.append(score)

    avg_bleu1_score = sum(bleu1_scores) / len(bleu1_scores) if bleu1_scores else 0.0
    return avg_bleu1_score

def calculate_rouge1_f_score(generated_reviews, reference_reviews):

    scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
    
    rouge1_f_scores = []
    for generated, reference in zip(generated_reviews, reference_reviews):
        score = scorer.score(reference, generated)
        rouge1_f_scores.append(score['rouge1'].fmeasure) 

    avg_rouge1_f_score = sum(rouge1_f_scores) / len(rouge1_f_scores) if rouge1_f_scores else 0.0
    
    return avg_rouge1_f_score

stemmer = PorterStemmer()

def get_word_matches(generated_tokens, reference_tokens):
    exact_matches = set(generated_tokens) & set(reference_tokens)

    stem_matches = set()
    for word in generated_tokens:
        stem = stemmer.stem(word)
        if any(stemmer.stem(ref_word) == stem for ref_word in reference_tokens):
            stem_matches.add(word)

    synonym_matches = set()
    for word in generated_tokens:
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        if any(ref_word in synonyms for ref_word in reference_tokens):
            synonym_matches.add(word)

    all_matches = exact_matches | stem_matches | synonym_matches
    return all_matches

def calculate_meteor_score(generated_review, reference_review):

    generated_tokens = re.findall(r'\w+', generated_review.lower())
    reference_tokens = re.findall(r'\w+', reference_review.lower())

    matches = get_word_matches(generated_tokens, reference_tokens)
    match_count = len(matches)

    precision = match_count / len(generated_tokens) if generated_tokens else 0
    recall = match_count / len(reference_tokens) if reference_tokens else 0

    alpha = 0.9 
    if precision + recall > 0:
        f_mean = (precision * recall) / ((1 - alpha) * precision + alpha * recall)
    else:
        f_mean = 0

    chunks = 0
    in_chunk = False
    for word in generated_tokens:
        if word in matches:
            if not in_chunk:
                chunks += 1
                in_chunk = True
        else:
            in_chunk = False
    penalty = 0.5 * (chunks / match_count) if match_count > 0 else 1

    meteor_score = f_mean * (1 - penalty)
    return meteor_score

def calculate_average_meteor(generated_reviews, reference_reviews):
    scores = []
    for generated, reference in zip(generated_reviews, reference_reviews):
        score = calculate_meteor_score(generated, reference)
        scores.append(score)
    return sum(scores) / len(scores) if scores else 0.0


def calculate_average_meteor_nltk(generated_reviews, reference_reviews):
    
    meteor_scores = []
    
    for generated, reference in zip(generated_reviews, reference_reviews):

        generated_tokens = generated.split()
        reference_tokens = reference.split()
        
        score = meteor_score([reference_tokens], generated_tokens)
        meteor_scores.append(score)

    avg_meteor_score = sum(meteor_scores) / len(meteor_scores) if meteor_scores else 0.0
    return avg_meteor_score

def calculate_cider_d(generated_reviews, reference_reviews):

    gts = {}
    res = {}
    
    for i, (generated, reference) in enumerate(zip(generated_reviews, reference_reviews)):
        gts[i] = [reference]
        res[i] = [generated]

    cider_scorer = Cider()

    cider_score, _ = cider_scorer.compute_score(gts, res)
    
    return cider_score

def separate_reviews_with_spacing(file_path):

    reference_reviews = []
    generated_reviews = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()] 

    for i in range(0, len(lines), 2):
        reference_review = lines[i]
        generated_review = lines[i + 1] if (i + 1) < len(lines) else ''
        
        reference_reviews.append(reference_review)
        generated_reviews.append(generated_review)

    return reference_reviews, generated_reviews

def separate_reviews_with_intermediate_lines(file_path):
    reference_reviews = []
    generated_reviews = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()] 

    for i in range(0, len(lines), 3):
        reference_review = lines[i] 
        generated_review = lines[i + 2] if (i + 2) < len(lines) else '' 

        reference_reviews.append(reference_review)
        generated_reviews.append(generated_review)

    return reference_reviews, generated_reviews


#Att2Seq
file_path = ATT2SEQ_GENERATED_PATH
reference_att2seq_reviews, generated_att2seq_reviews = separate_reviews_with_spacing(file_path)

#NRT
file_path_nrt = NRT_GENERATED_PATH
reference_nrt_reviews, generated_nrt_reviews = separate_reviews_with_spacing(file_path_nrt)

#PETER
file_path = PETER_GENERATED_PATH
reference_peter_reviews, generated_peter_reviews = separate_reviews_with_intermediate_lines(file_path)

#PEPLER(MLP)
file_path = PEPLER_GENERATED_PATH
reference_pepler_reviews, generated_pepler_reviews = separate_reviews_with_spacing(file_path)

#Llama-3
reference_llama3_reviews = pd.read_csv('dataset/3_core/interaction.csv', sep='\t')
reference_llama3_reviews = reference_llama3_reviews['review']

with open(LLAMA3_GENERATED_PATH, "r", encoding="utf-8") as file:
    generated_llama3_reviews = [line.strip() for line in file.readlines()]

#METEOR
meteor_peter = calculate_average_meteor_nltk(generated_peter_reviews, reference_peter_reviews)
meteor_nrt = calculate_average_meteor_nltk(generated_nrt_reviews, reference_nrt_reviews)
meteor_att2seq = calculate_average_meteor_nltk(generated_att2seq_reviews, reference_att2seq_reviews)
meteor_pepler = calculate_average_meteor_nltk(generated_pepler_reviews, reference_pepler_reviews)
meteor_llama3 = calculate_average_meteor_nltk(generated_llama3_reviews, reference_llama3_reviews)


#CIDER
cider_peter = calculate_cider_d(generated_peter_reviews, reference_peter_reviews)
cider_nrt = calculate_cider_d(generated_nrt_reviews, reference_nrt_reviews)
cider_att2seq = calculate_cider_d(generated_att2seq_reviews, reference_att2seq_reviews)
cider_pepler = calculate_cider_d(generated_pepler_reviews, reference_pepler_reviews)
cider_llama3 = calculate_cider_d(generated_llama3_reviews, reference_llama3_reviews)
