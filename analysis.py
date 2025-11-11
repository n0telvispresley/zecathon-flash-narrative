import nltk
from nltk.probability import FreqDist
from collections import Counter
import re
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
import pandas as pd # Make sure pandas is imported for pd.isna

# --- NLTK Setup ---
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("NLTK data not found. Downloading...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

stop_words = set(nltk.corpus.stopwords.words('english'))
stop_words.update(['com', 'www', 'http', 'https', 'co', 'uk', 'amp', 'rt', 'via'])

# --- 1. KEYWORD SENTIMENT ANALYSIS ---
def analyze_sentiment_keywords(text):
    """
    Analyzes sentiment based on keywords.
    Returns a single sentiment string.
    """
    if not text: return 'neutral'
    text_lower = str(text).lower()

    positive_kws = ['good', 'great', 'excellent', 'positive', 'love', 'awesome', 'best', 'happy', 'like', 'amazing', 'superb', 'fantastic', 'recommend', 'perfect', 'honoured', 'lauds', 'empower', 'support', 'champions', 'wins', 'upgrades', 'successful', 'oversubscribed', 'confidence']
    negative_kws = ['bad', 'poor', 'terrible', 'negative', 'hate', 'awful', 'worst', 'sad', 'dislike', 'broken', 'fail', 'issue', 'problem', 'disappointed', 'avoid', 'scam', 'fraud', 'downtime', 'glitches', 'fume', 'arrest', 'rift', 'vanished', 'failed', 'undersubscribed', 'loss']
    anger_kws = ['angry', 'furious', 'rage', 'mad', 'outrage', 'pissed', 'fuming', 'livid', 'worst!']
    appreciation_kws = ['thank', 'appreciate', 'grateful', 'thanks', 'kudos', 'cheers', 'props', 'helpful', 'honoured', 'lauds', 'legacy', 'honoring']
    mixed_kws = ['but', 'however', 'although', 'yet', 'still', 'despite']

    pos_count = sum(1 for k in positive_kws if re.search(r'\b' + re.escape(k) + r'\b', text_lower))
    neg_count = sum(1 for k in negative_kws if re.search(r'\b' + re.escape(k) + r'\b', text_lower))
    anger_count = sum(1 for k in anger_kws if re.search(r'\b' + re.escape(k) + r'\b', text_lower))
    app_count = sum(1 for k in appreciation_kws if re.search(r'\b' + re.escape(k) + r'\b', text_lower))
    has_mixed = any(re.search(r'\b' + re.escape(k) + r'\b', text_lower) for k in mixed_kws)

    # Prioritize sentiment
    if anger_count > 0: return 'anger'
    if (pos_count > 0 and neg_count > 0) or (has_mixed and (pos_count > 0 or neg_count > 0)): return 'mixed'
    if neg_count > 0: return 'negative'
    if pos_count > 0: return 'positive'
    if app_count > 0: return 'appreciation'
    return 'neutral'

# --- 2. KEYWORD/PHRASE EXTRACTION ---
def extract_keywords(all_text, brand, competitors):
    """
    Extracts top single keywords and two-word phrases (bigrams).
    """
    tokens = nltk.word_tokenize(all_text.lower())
    
    dynamic_stop_words = stop_words.copy()
    dynamic_stop_words.add(brand.lower())
    for c in competitors:
        dynamic_stop_words.add(c.lower())
    # Add generic bank words
    dynamic_stop_words.update(['bank', 'plc', 'ltd', 'group', 'holdings', 'zenith', 'access', 'gtco', 'first', 'cbn'])

    filtered_tokens = [t for t in tokens if len(t) > 2 and t.isalpha() and t not in dynamic_stop_words]
    
    unigram_freq = FreqDist(filtered_tokens)
    finder = BigramCollocationFinder.from_words(filtered_tokens)
    finder.apply_freq_filter(2) # Only show phrases that appear >= 2 times
    bigram_freq = finder.ngram_fd

    combined_freq = Counter()
    for word, freq in unigram_freq.items():
        combined_freq[word] += freq
    for phrase_tuple, freq in bigram_freq.items():
        combined_freq[" ".join(phrase_tuple)] += freq

    return combined_freq.most_common(10)

# --- 3. MAIN KPI CALCULATION ENGINE ---
def compute_kpis(full_data, campaign_messages, brand, competitors):
    """
    Calculates all KPIs. This function NOW PERFORMS
    sentiment and brand analysis.
    """
    if not full_data: return {}

    total_mentions = len(full_data)
    all_brands_list = [brand] + competitors
    
    tones = []
    themes = []
    brand_counts = Counter()
    
    # --- Main Analysis Loop ---
    for item in full_data:
        text = item.get('text', '')
        text_lower = str(text).lower()

        # 1. Perform Sentiment Analysis (Live)
        sentiment = analyze_sentiment_keywords(text)
        item['sentiment'] = sentiment
        tones.append(sentiment)
        
        # 2. Perform Thematic Analysis (Live)
        if any(kw in text_lower for kw in ['csr', 'esg', 'donation', 'community', 'foundation', 'initiative']):
            item['theme'] = 'CSR/ESG'
        elif any(kw in text_lower for kw in ['ceo', 'gmd', 'profit', 'results', 'acquisition', 'corporate', 'raise', 'capital', 'bond']):
            item['theme'] = 'Corporate'
        elif any(kw in text_lower for kw in ['partner', 'sponsorship', 'marathon']):
            item['theme'] = 'Partnership/Sponsorship'
        elif any(kw in text_lower for kw in ['app', 'loan', 'card', 'customer service', 'downtime', 'glitch', 'e-channel', 'transfer']):
            item['theme'] = 'Product/Service'
        elif any(kw in text_lower for kw in ['fraud', 'cbn', 'efcc', 'fine', 'court', 'scam', 'allegation', 'rift']):
            item['theme'] = 'Legal/Risk'
        else:
            item['theme'] = 'General News'
        themes.append(item['theme'])

        # 3. Find Mentioned Brands (for SOV)
        present_brands_in_item = set()
        for b_name in all_brands_list:
            if re.search(r'\b' + re.escape(b_name.lower()) + r'\b', text_lower):
                present_brands_in_item.add(b_name)
        
        item['mentioned_brands'] = list(present_brands_in_item) # Save to item
        
        for b_name in present_brands_in_item:
            brand_counts[b_name] += 1
    # --- End of Loop ---

    total_appearances = sum(brand_counts.values())
    sov = [(brand_counts[b] / total_appearances * 100) if total_appearances > 0 else 0 for b in all_brands_list]

    sentiment_counts = Counter(tones)
    sentiment_ratio = {tone: count / total_mentions * 100 for tone, count in sentiment_counts.items()}

    theme_counts = Counter(themes)
    theme_ratio = {theme: count / total_mentions * 100 for theme, count in theme_counts.items()}

    # --- Other KPIs ---
    mis = sum(item.get('authority', 5) for item in full_data if item.get('sentiment') in ['positive', 'appreciation'])
    
    matches = 0
    if campaign_messages:
        lower_campaign_messages = [msg.lower() for msg in campaign_messages]
        for item in full_data:
            if any(msg in item.get('text', '').lower() for msg in lower_campaign_messages):
                matches += 1
        mpi = (matches / total_mentions) * 100 if total_mentions > 0 else 0
    else: mpi = 0

    # --- Safe Engagement Calculation ---
    social_sources = ['reddit.com', 'fb', 'ig', 'threads', 'twitter', 'x']
    total_engagement = 0
    num_social_mentions = 0
    for item in full_data:
        if any(s in item.get('source', '').lower() for s in social_sources):
            try:
                likes = int(item.get('likes', 0))
                comments = int(item.get('comments', 0))
                total_engagement += (likes + comments)
                num_social_mentions += 1
            except (ValueError, TypeError): continue
                
    engagement_rate = total_engagement / num_social_mentions if num_social_mentions > 0 else 0
    
    # --- Safe Reach Calculation ---
    reach = 0
    for item in full_data:
        try:
            reach_val = item.get('reach', 0)
            if pd.isna(reach_val): # Handle NaN
                reach_val = 0
            reach += int(reach_val)
        except (ValueError, TypeError):
            continue

    return {
        'sentiment_ratio': sentiment_ratio,
        'theme_ratio': theme_ratio,
        'sov': sov,
        'mis': mis,
        'mpi': mpi,
        'engagement_rate': engagement_rate,
        'reach': reach,
        'all_brands': all_brands_list,
        'analyzed_data': full_data # Return the data with sentiments/themes added
    }