import numpy as np

from svca.models.model1 import Model1
# import useful limix functions
from limix.utils.preprocess import covar_rescaling_factor_efficient
from limix.core.covar import ZKZCov


class FromRealSimulation(object):
    def __init__(self, X, Y, kin_from):
        self.X = X
        self.Y = Y
        self.kin_from = kin_from

    def simulate(self, cterms=['intrinsic', 'environmental', 'interactions'], interactions_size=None):
        # train gp with requested terms
        model = Model1(self.Y, self.X, norm='quantile', oos_predictions=0.,
                       cov_terms=cterms, kin_from=self.kin_from)
        model.reset_params()
        model.train_gp(grid_size=10)

        # simulate from gp after removing interactions term
        k = model.covar_terms['intrinsic'].K() + \
            model.covar_terms['environmental'].K() + \
            model.covar_terms['noise'].K()
        k *= covar_rescaling_factor_efficient(k)

        # manually add a cross-talk term
        if interactions_size is not None:
            assert 0. < interactions_size < 1., 'interactions size must be between 0 and 1 '
            tmp = model.covar_terms['interactions'].K()
            tmp *= covar_rescaling_factor_efficient(tmp)

            tmp *= (interactions_size / (1. - interactions_size))
            k += tmp

        res = np.random.multivariate_normal([0.]*k.shape[0], k)

        return res


if __name__ == '__main__':
    x = np.reshape(np.random.randn(20), [10,2])
    y = np.random.randn(10)
    kin_from = np.reshape(np.random.randn(70), [10,7])

    tmp = FromRealSimulation(x, y, kin_from)
    tmp_sim  = tmp.simulate()
    print(tmp_sim)
