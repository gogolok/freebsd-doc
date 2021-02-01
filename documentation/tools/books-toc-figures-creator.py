# -*- coding: utf-8 -*-
"""
BSD 2-Clause License

Copyright (c) 2020-2021, The FreeBSD Project
Copyright (c) 2020-2021, Sergio Carlavilla <carlavilla@FreeBSD.org>

This script will generate the Table of Contents of the Handbook
"""
#!/usr/bin/env python3

import sys, getopt
import re

languages = []

"""
To determine if a chapter is a chapter we are going to check if it is
anything else, an appendix, a part, the preface ... and if it is not
any of those, it will be a chapter.

It may not be the best option, but it works :)
"""
def checkIsChapter(chapter, chapterContent):
  if "part" in chapter:
    return False
  elif "[preface]" in chapterContent:
    return False
  elif "[appendix]" in chapterContent:
    return False
  else:
    return True

def setTOCTitle(language):
  languages = {
    'en': 'List of Figures',
    'de': 'Abbildungsverzeichnis',
    'el': 'Κατάλογος Σχημάτων',
    'es': 'Lista de figuras',
    'fr': 'Liste des illustrations',
    'hu': 'Az ábrák listája',
    'it': 'Lista delle figure',
    'ja': '図の一覧',
    'mn': 'Зургийн жагсаалт',
    'nl': 'Lijst van afbeeldingen',
    'pl': 'Spis rysunków',
    'pt-br': 'Lista de Figuras',
    'ru': 'Список иллюстраций',
    'zh-cn': '插图清单',
    'zh-tw': '附圖目錄'
  }

  return languages.get(language)

def main(argv):

  try:
    opts, args = getopt.getopt(argv,"hl:",["language="])
  except getopt.GetoptError:
    print('books-toc-figures-creator.py -l <language>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('books-toc-figures-creator.py -l <language>')
      sys.exit()
    elif opt in ("-l", "--language"):
      languages = arg.split(',')

  for language in languages:

    with open('./content/{}/books/books.adoc'.format(language), 'r', encoding = 'utf-8') as booksFile:
      books = [line.strip() for line in booksFile]

      for book in books:
        with open('./content/{0}/books/{1}/chapters-order.adoc'.format(language, book), 'r', encoding = 'utf-8') as chaptersFile:
          chapters = [line.strip() for line in chaptersFile]

        toc =  "// Code @" + "generated by the FreeBSD Documentation toolchain. DO NOT EDIT.\n"
        toc += "// Please don't change this file manually but run `make` to update it.\n"
        toc += "// For more information, please read the FreeBSD Documentation Project Primer\n\n"
        toc += "[.toc]\n"
        toc += "--\n"
        toc += '[.toc-title]\n'
        toc += setTOCTitle(language) + '\n\n'

        chapterCounter = 1
        figureCounter = 1
        for chapter in chapters:
          with open('./content/{0}/books/{1}/{2}'.format(language, book, chapter), 'r', encoding = 'utf-8') as chapterFile:
            chapterContent = chapterFile.read().splitlines()
            chapterFile.close()
            chapter = chapter.replace("/_index.adoc", "").replace(".adoc", "").replace("/chapter.adoc", "")

            figureId = ""
            figureTitle = ""
            for lineNumber, chapterLine in enumerate(chapterContent, 1):
              if re.match(r"^image::+", chapterLine) and re.match(r"^[.]{1}[^\n]+", chapterContent[lineNumber-2]) and re.match(r"^\[\[[^\n]+\]\]", chapterContent[lineNumber-3]):
                  figureTitle = chapterContent[lineNumber-2]
                  figureId = chapterContent[lineNumber-3]

                  if book == "handbook":
                    toc += "* {0}.{1}  link:{2}#{3}[{4}]\n".format(chapterCounter, figureCounter, chapter, figureId.replace("[[", "").replace("]]", ""), figureTitle[1:])
                  else:
                      toc += "* {0}.{1}  link:{2}#{3}[{4}]\n".format(chapterCounter, figureCounter, "", figureId.replace("[[", "").replace("]]", ""), figureTitle[1:])

                  figureCounter += 1
              else:
                figureId = ""
                figureTitle = ""

            if checkIsChapter(chapter, chapterContent):
              chapterCounter += 1
            figureCounter = 1 # Reset figure counter

        toc += "--\n"

        with open('./content/{0}/books/{1}/toc-figures.adoc'.format(language, book), 'w', encoding = 'utf-8') as tocFile:
          tocFile.write(toc)

if __name__ == "__main__":
  main(sys.argv[1:])
