import csv
import time
import os
import json
import ast
import pickle
import matplotlib.pylab as plt
import pandas as pd
from itertools import combinations
import math
import pandas as pd
from tqdm import tqdm

class Paper:
    name_abbr = {"PR": "PhysRev", "PRA": "PhysRevA", "PRAB": "PhysRevAccelBeams", "PRAPPLIED": "PhysRevApplied",
                 "PRB": "PhysRevB", "PRC": "PhysRevC", "PRD": "PhysRevD", "PRE": "PhysRevE",
                 "PRFLUIDS": "PhysRevFluids", "PRI": "PhysRevSeriesI", "PRL": "PhysRevLett",
                 "PRMATERIALS": "PhysRevMaterials", "PRPER": "PhysRevPhysEducRes", "PRRESEARCH": "PhysRevResearch",
                 "PRSTAB": "PhysRevSTAB", "PRSTPER": "PhysRevSTPER", "PRX": "PhysRevX", "PRXQUANTUM": "PRXQuantum",
                 "RMP": "RevModPhys"}

    def __init__(self, doi):
        self.doi = doi
        self.title = None
        self.journal = None
        self.volume = None
        self.date = None
        self.numPages = None
        self.articleType = None
        self.authors = None
        self.affiliations = None
        self.year=None
        self.journal_abbr = {v: k for k, v in self.name_abbr.items()}  # reverse name map
        self.exist = self.getPaper()

    def getPaper(self):
        info = self.doi.split('/')[1].split('.')
        self.journal = info[0]
        self.volume = info[1]
        if self.journal not in self.journal_abbr:
            return False
        path = "/Users/shemingrong/project1_gender_differences_physics/Python_codes/python_dataset/name_disambiguation/aps-dataset-metadata-2020/" + self.journal_abbr[self.journal] + '/' + \
               str(self.volume) + "/" + '.'.join(info) + ".json"
        if os.path.exists(path) is False:
            return False
        with open(path, 'r', encoding='utf-8') as f:
            paper_json = json.load(f)
            self.title = paper_json['title']['value']
            self.date = paper_json['date']
            self.year = paper_json['date'].split('-')[0]
            self.numPages = paper_json['numPages'] if "numPages" in paper_json else None
            self.articleType = paper_json['articleType'] if "articleType" in paper_json else None
            if "authors" in paper_json:
                self.numAuthor = len(paper_json['authors'])
                self.authors = paper_json['authors']
                surnames = []
                for author in self.authors:
                    if "surname" in author.keys():
                        surnames.append(author["surname"].lower())
                if len(self.authors) >= 2 and surnames == sorted(surnames):
                    self.is_alpha = True
                else:
                    self.is_alpha = False
            self.affiliations = paper_json['affiliations'] if "affiliations" in paper_json else None
        return True

    def printPaperInfo(self):
        print(self.doi, end=' ')
        print(self.title)
        print(self.date, end=' ')
        print(str(self.numPages) + "pages", self.articleType)
        print(self.authors)
        print(self.affiliations)

    def __str__(self):
        return json.dumps({'doi': self.doi, 'authors': self.authors})

class Author:
    def __init__(self, name, doi):
        self.name = name
        self.doi = doi
        paper = Paper(doi)
        self.coauthor = []
        affiliationIds = None
        if len(paper.authors) > 1:
            if paper.authors[-1]['name'] == name:
                self.last_author = True
            else:
                self.last_author = False
        else:
            self.last_author = False

        for author in paper.authors:
            if author['name'] != name:
                self.coauthor.append(author['name'])
            else:
                self.author_name = author['name']
                # find affiliation
                affiliationIds = author["affiliationIds"]
        self.affiliation = []
        # some paper dont have affiliation
        if paper.affiliations is not None:
            affiliation_map = dict()
            for a in paper.affiliations:
                affiliation_map[a['id']] = a['name']
            for id in affiliationIds:
                if id in affiliation_map.keys():
                    self.affiliation.append(affiliation_map[id])
                else:
                    # some user's affiliationId dont have affiliation_map name
                    pass

with open("/Users/shemingrong/Desktop/Jan_dateset/focal_authors.pkl", 'rb') as f:
    focal_authors = pickle.load(f)

def get_focal_authors_info():
    with open('/Users/shemingrong/Desktop/Jan_dateset/total_author_infos.csv', 'r') as f:
        with open('/Users/shemingrong/Desktop/Jan_dateset/focal_author_infos.csv', 'w') as fw:
            writer = csv.writer(fw)
            writer.writerow(["id", "name", "gender", 'doi', 'journal', 'is_alpha', "year", 'numAuthor', 'coauthors', 'last_author'])
            for i, row in tqdm(enumerate(csv.reader(f))):
                if i != 0:
                    if row[1] in focal_authors:
                        if row[1] == '137098':
                            # row[2] = row[2] +' '
                            last_author = Author(row[2] +' ', row[3]).last_author
                        else:
                            last_author = Author(row[2], row[3]).last_author
                        writer.writerow([row[1], row[2], row[6], row[3], Paper(row[3]).journal, Paper(row[3]).is_alpha, row[5], Paper(row[3]).numAuthor, row[4], last_author])





get_focal_authors_info()