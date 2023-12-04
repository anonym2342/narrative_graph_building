# -*- coding: utf-8 -*-
"""
Interface to query a KG - format compressed HDT
"""
import os
import fnmatch
import yaml

from hdt import HDTDocument

from src.interface import Interface
from settings import FOLDER_PATH

HDT_DBPEDIA = \
    os.path.join(FOLDER_PATH, "dbpedia-snapshot-2021-09")

DEFAULT_PRED = \
    ["http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
     "http://dbpedia.org/ontology/date",
     "http://dbpedia.org/ontology/startDate",
     "http://dbpedia.org/ontology/endDate",
     "http://dbpedia.org/property/birthDate",
     "http://dbpedia.org/property/deathDate"]

with open(os.path.join(FOLDER_PATH, "dataset-config", "dbpedia.yaml"),
          encoding='utf-8') as file:
    dbpedia_dataset_config = yaml.load(file, Loader=yaml.FullLoader)

class HDTInterface(Interface):
    """
    Format of dataset = HDT, where you can do "simple" queries only, but much faster
    """
    def __init__(self, dataset_config: dict = dbpedia_dataset_config,
                 dates: list[str] = [None, None], default_pred: list[str] = DEFAULT_PRED,
                 folder_hdt: str = HDT_DBPEDIA, nested_dataset: bool = True, filter_kb: bool = 1):
        """
        - `dataset_config`: dict, dataset config, example in `dataset-config` folder
        - `dates`: list of two strings, start and end dates of the event
        - `default_pred`: list of strings, predicates for rdf:type and dates
        - `folder_hdt`: string, path to the HDT dataset
        - `nested_dataset`: boolean, whether the dataset is chunked down in folders
        - `filter_kb`: boolean, whether to exclude some types of predicates or not
        """
        Interface.__init__(self, dataset_config=dataset_config, dates=dates,
                           default_pred=default_pred, filter_kb=filter_kb)

        if nested_dataset:
            dirs = [os.path.join(folder_hdt, file) for file in os.listdir(folder_hdt)]
            dirs = [elt for elt in dirs if not elt.split('/')[-1].startswith(".")]
            dirs = [os.path.join(old_dir, new_dir, "hdt") \
                for old_dir in dirs for new_dir in os.listdir(old_dir)]
            dirs = [elt for elt in dirs if not elt.split('/')[-2].startswith(".")]
            dirs = [elt for elt in dirs if os.path.exists(elt)]
            self.docs = [HDTDocument(file) for file in dirs]
        else:
            files = [os.path.join(folder_hdt, file) for file in os.listdir(folder_hdt) \
                        if fnmatch.fnmatch(file, "*.hdt")]
            self.docs = [HDTDocument(file) for file in files]

    def get_triples(self, **params: dict) -> list[(str, str, str)]:
        """ Querying HDT dataset """
        subject_t = params["subject"] if "subject" in params else ""
        predicate_t = params["predicate"] if "predicate" in params else ""
        object_t = params["object"] if "object" in params else ""

        triples = []
        for doc in self.docs:
            curr_triples, _ = doc.search_triples(subject_t, predicate_t, object_t)
            triples += list(curr_triples)

        return triples



if __name__ == '__main__':
    NODE = "http://dbpedia.org/resource/André_Masséna"
    PREDICATE = ["http://dbpedia.org/ontology/wikiPageWikiLink",
                    "http://dbpedia.org/ontology/wikiPageRedirects",
                    "http://dbpedia.org/ontology/wikiPageDisambiguates",
                    "http://www.w3.org/2000/01/rdf-schema#seeAlso",
                    "http://xmlns.com/foaf/0.1/depiction",
                    "http://xmlns.com/foaf/0.1/isPrimaryTopicOf",
                    "http://dbpedia.org/ontology/thumbnail",
                    "http://dbpedia.org/ontology/wikiPageExternalLink",
                    "http://dbpedia.org/ontology/wikiPageID",
                    "http://dbpedia.org/ontology/wikiPageLength",
                    "http://dbpedia.org/ontology/wikiPageRevisionID",
                    "http://dbpedia.org/property/wikiPageUsesTemplate",
                    "http://www.w3.org/2002/07/owl#sameAs",
                    "http://www.w3.org/ns/prov#wasDerivedFrom",
                    "http://dbpedia.org/ontology/wikiPageWikiLinkText",
                    "http://dbpedia.org/ontology/wikiPageOutDegree",
                    "http://dbpedia.org/ontology/abstract",
                    "http://www.w3.org/2000/01/rdf-schema#comment",
                    "http://www.w3.org/2000/01/rdf-schema#label"]

    interface = HDTInterface()
    ingoing_test, outgoing_test, types_test = interface(node=NODE, predicate=PREDICATE)
    print(f"{ingoing_test}\n{outgoing_test}\n{types_test}")

    ingoing_test.to_csv(f"{FOLDER_PATH}/hdt_ingoing.csv")
    outgoing_test.to_csv(f"{FOLDER_PATH}/hdt_outgoing.csv")
    types_test.to_csv(f"{FOLDER_PATH}/hdt_types.csv")
