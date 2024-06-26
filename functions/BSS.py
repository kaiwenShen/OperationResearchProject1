import cvxpy as cp
import numpy as np
from scipy.stats import gmean

from functions.helper import cal_Q, adjusted_r_squared_w_0,cal_vcov


def bss_one_asset(y, x, k=4):
    beta = cp.Variable(x.shape[1])
    z = cp.Variable(x.shape[1], boolean=True)
    resid = y - x @ beta
    obj = cp.Minimize(cp.sum_squares(resid))
    M_u = 9
    constraints = [-M_u * z <= beta, beta <= M_u * z]
    constraints += [cp.sum(z) <= k]
    prob = cp.Problem(obj, constraints)
    prob.solve()
    return beta.value

def BSS(returns, factRet, OOS_return, OOS_factRet, lambda_, K):
    """
    % Use this function for the BSS model. Note that you will not use
    % lambda in this model (lambda is for LASSO).
    %
    % You should use an optimizer to solve this problem. Be sure to comment
    % on your code to (briefly) explain your procedure.
    """

    # *************** WRITE YOUR CODE HERE ***************
    # ----------------------------------------------------------------------

    # mu =          % n x 1 vector of asset exp. returns
    # Q  =          % n x n asset covariance matrix
    # ----------------------------------------------------------------------
    factRet = np.hstack([np.ones((len(factRet), 1)), factRet])
    sol_beta = []
    for i in range(returns.shape[1]):
        beta = bss_one_asset(returns.iloc[:, i].values, factRet, K)
        sol_beta.append(beta)
    beta = np.array(sol_beta).T
    if np.sum(beta != 0) != K*returns.shape[1]:
        # print warning that upper/lower bound is incorrect
        print('Warning: BSS did not find the desired number of non-zero betas')
        print('correct number of non-zero betas:', K*returns.shape[1])
        print('number of non-zero betas found:', np.sum(beta != 0))
    factor_mu = gmean(factRet + 1) - 1
    mu = np.dot(factor_mu, beta)
    Q = cal_Q(beta, factRet, returns - factRet @ beta)
    # Q = cal_vcov(returns)
    adj_r2 = adjusted_r_squared_w_0(returns.values, np.dot(factRet, beta), beta, factRet.shape)
    OOS_factRet = np.hstack([np.ones((len(OOS_factRet), 1)), OOS_factRet])
    oos_adj_r2 = adjusted_r_squared_w_0(OOS_return.values, np.dot(OOS_factRet, beta), beta, OOS_factRet.shape)
    return mu, Q, adj_r2, oos_adj_r2
