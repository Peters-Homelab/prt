# Python-Application-Framework
![Codacy grade](https://img.shields.io/codacy/grade/3ff98c75be81420cba2922ab6a5ed27e?label=Codacy%20Grade&style=for-the-badge)
![GitHub](https://img.shields.io/github/license/justintimperio/paf?style=for-the-badge)

## Abstract
I create tools and projects in python pretty frequently and consolidating my frequently used functions into a submodule is extremely helpful. Typically this module attempts to be as pragmatic as possible. While many pip modules exist that solve many of these problems, PAF has a 'do it yourself' mentality. This usually results in a smaller dependency list for each of my projects and faster speeds as each feature is natively implemented without external calls. I attempt to keep 'hacky' functions out of this module unless python forces my hand.

## Using PAF
To add PAF to your own python project simply add it as a submodule using:\
`git submodule add https://github.com/JustinTimperio/paf.git`

You can now import PAF directly into your project and call functions with the following syntax:
```python
import paf

subdirs = paf.find_subdirs('/path/to/search')

for item in paf.progress_bar(subdirs):
    time.sleep(0.1)
```
