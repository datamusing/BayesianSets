import numpy as np
import json
import pandas as pd
import scipy.sparse as sparse
class bayesSets():
    def __init__(self):
        """
        Basic class for BS modeling

        """
        self.alpha = None
        self.beta = None
        pass

    def loadBinarizedDataFromJSON(self, jsonFile):
        """
        load binarized data from a JSON file. The file is
        :param jsonFile: string
        assumed to have to be structured as:
         {'item0':[tag10, tag23, ...], 'item1':[tag2, tag13,..],...}
        where the tags are the features for an item.
        """
        data = json.load(open(jsonFile, "r"))

        # infer the union set containing all features
        all_features = []
        for v in data.values():
            all_features += v
        features = np.unique(all_features)
        s = pd.Series(features)
        #create indexed features and reverse lookup dict
        self.features_index = s.to_dict()
        self.features_reverse_index = {v:k for k, v in self.features_index.items()}

        # Now create the sparse data matrix
        nitems = len(data.keys())
        nfeatures = len(self.features_index)

        self.X = sparse.lil_matrix((nitems, nfeatures))
        self.item_index = {}
        self.item_reverse_index = {}

        i = 0

        for item, features in data.items():
                self.item_index[i] = item
                self.item_reverse_index[item] = i
                self.X[i, [self.features_reverse_index[f] for f in features]] = 1.
                i += 1

        self.X = self.X.tocsr()

    def setHyperParams(self, C=2):
        """
        Set alpha and beta for the multinomial conjugate prior.
        :param C: hyperparameter coefficient set to 2 by default
        """
        self.alpha = C * self.X.mean(0)
        self.beta = C - self.alpha
        self.alpha_plus_beta = self.alpha + self.beta
        self.log_alpha = np.log(self.alpha)
        self.log_beta = np.log(self.beta)
        self.log_alpha_plus_beta = np.log(self.alpha_plus_beta)


    def query(self, queryItemList):
        assert(self.alpha is not None), 'Hyperparameters not set yet'
        assert(self.beta is not None), 'Hyperparameters not set yet'
        assert(self._validate_query(queryItemList)), 'Query not in source items'
        c, q = self._computeQueryParams(queryItemList)
        log_scores = c + self.X*q.transpose()
        log_scores = np.asarray(log_scores.flatten())[0]
        ranked_ids = np.argsort(log_scores)[::-1]

        return results(queryItemList,self.item_index, ranked_ids, log_scores)




    def _validate_query(self, queryItemList):
        return set(queryItemList).issubset(set(self.item_index.values()))

    def _computeQueryParams(self, queryItemList):
        N = len(queryItemList)

        sum_x = self.X[self.item_reverse_index[queryItemList[0]]]
        for item in queryItemList[1:]:
            sum_x = sum_x + self.X[self.item_reverse_index[item]]

        alpha_tilde = sum_x + self.alpha
        beta_tilde = self.beta + N - sum_x
        log_alpha_tilde = np.log(alpha_tilde)
        log_beta_tilde = np.log(beta_tilde)
        c = (self.alpha_plus_beta - np.log(self.alpha + self.beta + N) + log_beta_tilde - self.log_beta).sum()
        q = log_alpha_tilde - self.log_alpha - log_beta_tilde + self.log_beta

        return c, q

class results():
    def __init__(self, queryItemList, item_index, ranked_ids, log_scores):
        self.queryItemList = queryItemList
        self.item_index = item_index
        self.ranked_ids = ranked_ids
        self.log_scores = log_scores
        self.res_pandas = pd.DataFrame(self._to_dict())

    def _to_dict(self, maxItems=1000):
        if maxItems is None:
            maxItems = len(self.log_scores)
        resDict = {
                    'item_id': [self.item_index.keys()[r] for r in self.ranked_ids[:maxItems]],
                    'item_desc': [self.item_index[r] for r in self.ranked_ids[:maxItems]],
                    'log_score': [self.log_scores[r] for r in self.ranked_ids[:maxItems]]
                    }
        return resDict

    def prettyPrint(self, maxItems = 50):
        """
        print the results
        """

        print "Your Query:"
        print
        for item in self.queryItemList:
            print item
        print " Bayesian Sets Algorithm recommends:"
        #res = pd.DataFrame(self._to_dict())
        print self.res_pandas.head(maxItems)

    def dump(self):
        pass





