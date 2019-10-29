from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle, os, re


def load_seen():
    if os.path.getsize("./seen.pickle") > 0:
        with open("./seen.pickle", "rb") as f:
            unpickler = pickle.Unpickler(f)
            return unpickler.load()
    return

def save_seen(seen):
    pickle.dump(seen, open("./seen.pickle", 'wb+'))
    return

def sample(n):
    tweet = pd.read_csv("cleaned_text.csv")
    row_samples = []
    seen = load_seen()
    if seen:
        seen_len = len(seen)
    else:
        seen = []
        seen_len = 0
    while len(row_samples) < n:
        valid_sample = np.random.randint(0, tweet.shape[0])
        if valid_sample not in seen:
            seen.append(valid_sample)
            row_samples.append(valid_sample)
            
    sample = tweet.iloc[row_samples]
    save_seen(seen)
    return sample, seen_len, row_samples



# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
@application.route('/', methods=['GET'])

def render_index():
    s, seen_len, rs = sample(10)
    return render_template('index.html', n_samples=seen_len, sample=list(zip(s['tweet'].tolist(),rs, s['date'].tolist())))

@application.route('/', methods=['POST'])
def receive():
    tags = request.form
    tweet = pd.read_csv("cleaned_text.csv")
    tagged = pd.read_csv("tagged_text.csv")
    for k, v in tags.items():
        row_num = int(k.split("_")[1])
        if row_num in tagged['row'].unique():
            continue
        tagged = tagged.append(tweet.iloc[row_num])
        tagged.loc[row_num,'tag'] = v
        tagged.loc[row_num,'row'] = row_num
    print(tagged)
    tagged.to_csv("tagged_text.csv", index=False)
    return render_index()

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()