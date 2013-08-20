import numpy as np
import json
import pandas as pd
import scipy.sparse as sparse
class bayesSets():
    def __init__(self):
        """
        Basic class for BS modeling

        """

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
        nfeatures = len(features_index)

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
        :param C: hyperparameter coefficient set to 2 by defualt
        """
        self.alpha = C * self.X.mean(0)
        self.beta = C - self.alpha
        self.alpha_plus_beta = self.alpha + self.beta
        self.log_alpha = np.log(self.alpha)
        self.log_beta = np.log(self.beta)
        self.log_alpha_plus_beta = np.log(self.alpha_plus_beta)


    def query(self, queryItemList):

        N = len(queryItemList)





        sum_x = XX[self.item_reverse_index[queryItemList[0]]]
        for item in queryItemList[1:]:
            sum_x = sum_x + XX[self.item_reverse_index[item]]

        alpha_tilde = sum_x + self.alpha
        beta_tilde = self.beta + N - sum_x
        log_alpha_tilde = np.log(alpha_tilde)
        log_beta_tilde = np.log(beta_tilde)
        c = (np.log(alpha+beta) - np.log(alpha+beta+N) + log_beta_tilde - np.log(beta)).sum()
        #print locals()
        q = log_alpha_tilde - np.log(alpha) - log_beta_tilde + np.log(beta)

        return c,q


if __name__ == "__main__":
    bs = bayesSets()
    bs.loadBinarizedDataFromJSON(jsonFile)




