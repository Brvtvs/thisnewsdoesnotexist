## What is this?

This is a fake news site that uses artificial intelligence to generate false news and commentary. Throughout the day, it automatically generates and publishes fake articles on topical subjects. The articles on this site are not written, edited, or curated by humans. Everything is automated.

![Alt](/thisnewsdoesnotexist.gif "")
  

## Why make this?

We built this site to raise awareness of the threat from fake news generated by artificial intelligence. Recent advances in AI have made it cheap and easy to automatically generate realistic fake news stories ([Radford et al., 2019](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf); [Zellers et al., 2019](https://arxiv.org/pdf/1905.12616.pdf)), and these methods could easily be used for malicious purposes.

Bad actors could use this technology to generate realistic fake content on an unprecedented scale. Unlike human propagandists, AI algorithms can create fake stories in truly massive quantities, potentially flooding the internet with fake content. In an environment where fake news already spreads farther and faster than the truth ([Vosoughi et al., 2018](https://science.sciencemag.org/content/359/6380/1146)), fake stories could soon outnumber real ones, at a fraction of the cost.

Researchers have started to develop algorithms to automatically detect if text was generated by AI or written by a human ([Gehrmann et al., 2019](http://gltr.io)), but there is no purely technical solution to this problem. Algorithms will never be able to detect fake text perfectly, and generators are likely to get more reliable and better at avoiding detection. Addressing the dangers of AI-generated fake text will require collaboration between academia, industry, and government to raise awareness, develop mitigations, establish ethical guidelines, and deter malicious behavior.

  

## Wouldn't a site like this just make the problem worse?

We think the chances are low that this site will be misused. As written, all of the content is clearly marked as machine generated. More importantly, the algorithm that we use to generate fake articles is already [easily accessible](https://grover.allenai.org/) and offers more control on its own than this site does. This site also does not generate enough fake content to save anyone a meaningful amount of money or computing power if they were trying to create large quantities of fake news.

Still, we believe that developers and researchers should carefully consider the ethical impact of their work and welcome critique. 

  

## How does the site work?

To generate articles, this site uses the Grover Mega model from [Zellers et al.](https://arxiv.org/pdf/1905.12616.pdf) Throughout the day, the site pulls real headlines from the internet and uses them to seed Grover so that it generates fake articles on subjects in today’s headlines. To generate op-eds and other commentary, the site seeds Grover with editorials and configures it to produce text in the style of outlets with strong political leanings.

Once the site generates an article, it matches that article with an image using [Google’s custom search engine API](https://cse.google.com/cse/).

  

## Disclaimers:

This site is a personal project of its creators and does not represent the views of the United States Government or any other organization. We make no claims to own any of the content or images on this site. The stories on this site are automatically generated and do not reflect the views of the site's creators in any way. There is no intent to defame any real people. This site is for educational purposes only. 


## Example fake story:
* **Fake headline, prompted by a real headline:** Blast-hit tankers to be assessed off UAE coast
* **Corresponding fake body:** The UAE General Services Authority announced on Thursday that two tankers that were hit in a bombing near Sabrah port in May will soon be examined off the country’s coast. Twenty-three people were killed and 12 more were injured in the attack and both tankers are now on the verge of being checked for damage and casualties, reported the British daily, The National. The news comes hours after the UAE announced it would continue to lead a military coalition fighting Houthi rebels based in Yemen in its bid to overthrow the government of President Abd Rabbuh Mansur Hadi. A spokeswoman for the country said that the interception of weapons such as ballistic missiles and surface-to-air missiles was “of vital importance to Yemen.” Meanwhile, the oil shipping line Maersk reportedly halted shipping to the UAE earlier this week because of security concerns after it became the target of a missile attack. “Maersk stopped shipping through the Al Hudaydah strait on Sunday because of the continued threats of piracy and violence across the Bab al-Mandab strait in the Red Sea,” a company spokesman told Reuters. Maersk also says it has reduced oil shipments from the UAE to be processed in its Europe terminal.

## Funny example fake story: 
* **Fake headline, prompted by a real headline:** Zuckerberg Completes His Tidal Wave of Loneliness 
* **Corresponding fake body:** Facebook co-founder Mark Zuckerberg has opened up about how loneliness has affected him. After a recent biographical documentary chronicled his life, it emerged that Zuckerberg often "cried uncontrollably" because he was in such a "deep place of loneliness". He confessed to The Washington Post: "I’m lonely when I’m away from Facebook. "I cry uncontrollably sometimes — like, 'Man, why do I feel this way?'" Last October, Facebook launched a new initiative to tackle loneliness by encouraging people to connect more with people in their community. The initiative was dubbed "Community Help", and provided tools for people to help others in distress on its platform. Zuckerberg agreed with the scheme and said: "We have to do better. We have a responsibility to do a better job of enabling people to be good neighbours, a great neighbour. And we have to find new ways to encourage that in our own culture. Seeing people I care about in the newsfeed, what I feel around seeing my friends and family is a big part of this." But it seems that this kind of influence can be a double-edged sword as Facebook has also been criticised for its effects on many in society, including 'fake news', sexualisation of children and the manipulation of news.
