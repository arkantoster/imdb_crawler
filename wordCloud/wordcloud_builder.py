import jsonlines
from stop_words import get_stop_words
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt

quotesText = ''

with jsonlines.open('./imdbTop.jl') as reader:
  for jsonLine in reader:
    for q in jsonLine['quotes']:
      quotesText += q['content']

stop_words = get_stop_words('english')
mask = np.array(Image.open('./cloudWords/clapper-icon.jpg'))

quoteCloud = WordCloud(
  stopwords=stop_words,
  mask=mask,
  background_color="white",
  max_words=200,
  max_font_size=256,
  random_state=42,
  width=1000,
  height=1000
)

quoteCloud.generate(quotesText)
plt.imshow(quoteCloud, interpolation="bilinear")
plt.axis('off')
plt.show()