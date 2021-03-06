import scipy.stats
import numpy as np
'''
Reference:
Hahn, Gerald J., and Meeker, William Q. "Statistical Intervals: A Guide for 
    Practitioners." Germany, Wiley, 1991.
'''


def pct2sig(p, bound='2-sided'):
    # Converts a to a percentile to a gaussian sigma value (1-sided), or to the 
    # sigma value for which the range (-sigma, +sigma) bounds that percent of 
    # the normal distribution (2-sided)
    if p <= 0 or p >= 1:
        raise ValueError(f'{p=} must be 0 < p < 1')            
        return None
    if bound == '2-sided':
        if p >= 0.5:
            return scipy.stats.norm.ppf(1-(1-p)/2)
        else:
            return scipy.stats.norm.ppf(p/2)
    if bound == '1-sided':
        return scipy.stats.norm.ppf(p)



def sig2pct(sig, bound='2-sided'):
    # Converts a gaussian sigma value to a percentile (1-sided), or to the percent
    # of the normal distribution bounded by (-sigma, +sigma) (2-sided)
    if bound == '2-sided':
        p = 1-(1-scipy.stats.norm.cdf(sig))*2
    elif bound == '1-sided':
        p = scipy.stats.norm.cdf(sig)
    return p



def order_stat_TI_n(k, p, c, nmax=int(1e7), bound='2-sided'):
    '''
    Order Statistic Tolerance Interval, find n
    This function returns the number of cases n necessary to say that the true 
    result of a measurement x will be bounded by the k'th order statistic with 
    a probability p and confidence c. Variables l and u below indicate lower 
    and upper indices of the order statistic.
    
    For example, if I want to use my 2nd highest measurement as a bound on 99% 
    of all future samples with 90% confidence:
        n = order_stat_TI_n(k=2, p=0.99, c=0.90, bound='1-sided') = 389
    The 388th value of x when sorted from low to high, or sorted(x)[-2], will 
    bound the upper end of the measurement with P99/90. 
    
    '2-sided' gives the result for the measurement lying between the k'th lowest 
    and k'th highest measurements. If we run the above function with 
    bound='2-sided', then n = 668, and we can say that the true measurement lies 
    between sorted(x)[1] and sorted(x)[-2] with P99/90.
    
    See chapter 5 of Reference at the top of this file for statistical 
    background.
    '''
    order_stat_var_check(p=p, k=k, c=c, nmax=nmax)
    
    if bound == '2-sided':
        l = k  # we won't be using assymmetrical order stats
    elif bound == '1-sided':
        l = 0

    # use bisection to get minimum n (secant method is unstable due to flat portions of curve)
    n = [1,nmax]
    maxsteps = 1000 # nmax hard limit of 2^1000
    u = n[1] + 1 - k
    if EPTI(n[1], l, u, p) < c:
        print(f'n exceeded {nmax=} for P{100*p}/{c*100}. Increase nmax or loosen constraints.')
        return None

    for i in range(maxsteps):
        step = (n[1]-n[0])/2
        ntemp = n[0] + np.ceil(step)
        if step < 1:
            return int(n[1])
        else:
            u = ntemp + 1 - k
            if EPTI(ntemp, l, u, p) <= c:
                n[0] = ntemp
            else:
                n[1] = ntemp
    raise ValueError(f'With {n=}, could not converge in {maxsteps=} steps. Is {nmax=} > 2^{maxsteps}?')        



def order_stat_TI_p(n, k, c, ptol=1e-9, bound='2-sided'):
    # Order Statistic Tolerance Interval, find p
    order_stat_var_check(n=n, k=k, c=c)
    
    if bound == '2-sided':
        l = k  # we won't be using assymmetrical order stats
    elif bound == '1-sided':
        l = 0
    u = n + 1 - k

    # use bisection to get n (secant method is unstable due to flat portions of curve)
    p = [0,1]
    maxsteps = 1000 # p hard tolerance of 2^-1000
    for i in range(maxsteps):
        step = (p[1]-p[0])/2
        ptemp = p[0] + step
        if step <= ptol:
            return p[1]
        else:
            if EPTI(n, l, u, ptemp) >= c:
                p[0] = ptemp
            else:
                p[1] = ptemp
    raise ValueError(f'With {p=}, could not converge under {ptol=} in {maxsteps=} steps.')        



def order_stat_TI_k(n, p, c, bound='2-sided'):
    # Order Statistic Tolerance Interval, find maximum k
    order_stat_var_check(n=n, p=p, c=c)
    
    if bound == '2-sided':
        l = 1  # we won't be using assymmetrical order stats
    elif bound == '1-sided':
        l = 0
    if EPTI(n, l, n, p) < c:
        print(f'Warning: {n=} is too small to meet {p=} at {c=} for {bound} tolerance interval at any order statistic')
        return None

    # use bisection to get n (secant method is unstable due to flat portions of curve)
    k = [1,np.ceil(n/2)]
    maxsteps = 1000 # nmax hard limit of 2^1000
    for i in range(maxsteps):
        step = (k[1]-k[0])/2
        ktemp = k[0] + np.ceil(step)
        if step < 1:
            return int(k[1])-1
        else:
            if bound == '2-sided':
                l = ktemp  # we won't be using assymmetrical order stats
            elif bound == '1-sided':
                l = 0
            u = n + 1 - ktemp
            
            if EPTI(n, l, u, p) > c:
                k[0] = ktemp
            else:
                k[1] = ktemp
    raise ValueError(f'With {n=}, could not converge in {maxsteps=} steps. Is n > 2^{maxsteps}?') 
       


def order_stat_TI_c(n, k, p, bound='2-sided'):
    # Order Statistic Tolerance Interval, find c
    order_stat_var_check(n=n, p=p, k=k)
    
    if bound == '2-sided':
        l = k  # we won't be using assymmetrical order stats
    elif bound == '1-sided':
        l = 0
    u = n + 1 - k
    
    c = EPTI(n, l, u, p)
    return c



def order_stat_P_n(k, P, c, nmax=int(1e7), bound='2-sided'):
    '''
    Order Statistic Percentile, find n
    This function returns the number of cases n necessary to say that the true 
    Pth percentile located at or between indices iPl and iPu of a measurement x
    will be bounded by the k'th order statistic with confidence c. 
    
    For example, if I want to use my 5th nearest measurement as a bound on the 
    50th Percentile with 90% confidence:
        n = order_stat_P_n(k=5, P=0.50, c=0.90, bound='2-sided') = 38
        iPl = np.floor(P*(n + 1)) = 19
        iPu = np.ceil(P*(n + 1)) = 20
    The 19-5 = 14th and 20+5= 25th values of x when sorted from low to high, 
    or [sorted(x)[13], sorted(x)[24]] will bound the 50th percentile with 90%
    confidence. 
    
    '2-sided' gives the upper and lower bounds. '1-sided lower' and 
    '1-sided upper' give the respective lower or upper bound of the Pth 
    percentile over the entire rest of the distribution. 
    
    See chapter 5 of Reference at the top of this file for statistical 
    background.
    '''
    order_stat_var_check(p=P, k=k, c=c, nmax=nmax)
    
    # use bisection to get minimum n (secant method is unstable due to flat portions of curve)
    nmin = np.ceil(max(k/P - 1, k/(1-P) - 1))
    ntemp = nmin
    n = [nmin,nmax]
    maxsteps = 1000 # nmax hard limit of 2^1000
    
    (iPl, iP, iPu) = get_iP(n[0], P)
    if bound == '2-sided':
        l = iPl - k + 1 # we won't be using assymmetrical order stats
        u = iPu + k - 1
        if l <= 0 or u >= n[1] + 1 or EPYP(n[0], l, u, P) < c:
            print(f'n ouside bounds of {nmin=}:{nmax=} for {P=} with {k=} at {c=}. Increase nmax, raise k, or loosen constraints.')
            return None
    elif bound == '1-sided upper':
        l = 0
        u = iPu + k -1
        if u >= n[1] + 1 or EPYP(n[0], l, u, P) < c:
            print(f'n ouside bounds of {nmin=}:{nmax=} for {P=} with {k=} at {c=}. Increase nmax, raise k, or loosen constraints.')
            return None
    elif bound == '1-sided lower':
        l = iPl - k + 1
        u = n[0] + 1
        if l <= 0 or EPYP(n[0], l, u, P) < c:
            print(f'n ouside bounds of {nmin=}:{nmax=} for {P=} with {k=} at {c=}. Increase nmax, raise k, or loosen constraints.')
            return None

    for i in range(maxsteps):
        step = (n[1]-n[0])/2
        if step < 1:
            return int(n[0])
        else:
            ntemp = n[0] + np.ceil(step)
            (iPl, iP, iPu) = get_iP(ntemp, P)    
            if bound == '2-sided':
                l = iPl - k  # we won't be using assymmetrical order stats
                u = iPu + k
            elif bound == '1-sided upper':
                l = 0
                u = iPu + k
            elif bound == '1-sided lower':
                l = iPl - k
                u = ntemp + 1
            if EPYP(ntemp, l, u, P) > c:
                n[0] = ntemp
            else:
                n[1] = ntemp
        #print(ntemp, ':', EPYP(ntemp, l, u, P), l, iP, u, n, step)
    raise ValueError(f'With {n=}, could not converge in {maxsteps=} steps. Is {nmax=} > 2^{maxsteps}?')    



def order_stat_P_k(n, P, c, bound='2-sided'):
    # Order Statistic Percentile, find maximum k
    order_stat_var_check(n=n, p=P, c=c)
    
    (iPl, iP, iPu) = get_iP(n, P)    
    if bound == '2-sided':
        k = [1, min(iPl, n + 1 - iPu)]
        l = iPl - k[1] + 1 # we won't be using assymmetrical order stats
        u = iPu + k[1] - 1
        if l <= 0 or u >= n+1 or EPYP(n, l, u, P) < c:
            print(f'Warning: {n=} is too small to meet {P=} at {c=} for {bound} percentile confidence interval at any order statistic')
            return None

    elif bound == '1-sided upper':
        k = [1, n + 1 - iPu]
        l = 0
        u = iPu + k[1] - 1
        if u >= n + 1 or EPYP(n, l, u, P) < c:
            print(f'Warning: {n=} is too small to meet {P=} at {c=} for {bound} percentile confidence interval at any order statistic')
            return None

    elif bound == '1-sided lower':
        k = [1, iPl]
        l = iPl - k[1] + 1
        u = n + 1
        if EPYP(n, l, u, P) < c:
            print(f'Warning: {n=} is too small to meet {P=} at {c=} for {bound} percentile confidence interval at any order statistic')
            return None

    # use bisection to get n (secant method is unstable due to flat portions of curve)
    maxsteps = 1000 # nmax hard limit of 2^1000
    for i in range(maxsteps):
        step = (k[1]-k[0])/2
        ktemp = k[0] + np.ceil(step)

        if step < 1:
            return int(k[1])
        
        else:
            if bound == '2-sided':
                l = iPl - ktemp
                u = iPu + ktemp
            elif bound == '1-sided upper':
                l = 0
                u = iPu + ktemp
            elif bound == '1-sided lower':
                l = iPl - ktemp
                u = n + 1
                
            if EPYP(n, l, u, P) > c:
                k[1] = ktemp
            else:
                k[0] = ktemp
                
    raise ValueError(f'With {n=}, could not converge in {maxsteps=} steps. Is n > 2^{maxsteps}?')



def order_stat_P_c(n, k, P, bound='2-sided'):
    # Order Statistic Percentile, find c
    order_stat_var_check(n=n, p=P, k=k)

    (iPl, iP, iPu) = get_iP(n, P)    
    if bound == '2-sided':
        l = iPl - k  # we won't be using assymmetrical order stats
        u = iPu + k 
    elif bound == '1-sided upper':
        l = 0
        u = iPu + k
    elif bound == '1-sided lower':
        l = iPl - k
        u = n + 1
        
    if l < 0 or u > n+1:
        raise ValueError(f'{l=} or {u=} are outside the valid bounds of (0, {n+1}) (check: {iP=}, {k=})') 
    
    c = EPYP(n, l, u, P)
    return c



def EPYP(n, l, u, p):
    # Estimated Probabiliity for the Y'th Percentile, see Chp. 5.2 of Reference
    order_stat_var_check(n=n, l=l, u=u, p=p)
    c = scipy.stats.binom.cdf(u-1, n, p) - scipy.stats.binom.cdf(l-1, n, p)
    return c



def EPTI(n, l, u, p):
    # Estimated Probabiliity for a Tolerance Interval, see Chp. 5.3 of Reference
    order_stat_var_check(n=n, l=l, u=u, p=p)
    c = scipy.stats.binom.cdf(u-l-1, n, p)
    return c


def get_iP(n, P):
    # Index of Percentile (1-based indexing)
    iP = P*(n + 1) 
    iPl = int(np.floor(iP))
    iPu = int(np.ceil(iP))
    iP = int(np.round(iP))
    return (iPl, iP, iPu)



def order_stat_var_check(n=None, l=None, u=None, p=None, k=None, c=None, nmax=None):
    if n is not None and n < 1:
        raise ValueError(f'{n=} must be >= 1')
    if l is not None and l < 0:
        raise ValueError(f'{l=} must be >= 0')
    if u is not None and n is not None and u > n+1:
        raise ValueError(f'{u=} must be >= {n+1}')
    if u is not None and l is not None and u < l:
        raise ValueError(f'{u=} must be >= {l=}')
    if p is not None and (p <= 0 or p >=1):
        raise ValueError(f'{p=} must be in the range 0 < p < 1')
    if k is not None and k < 1:
        raise ValueError(f'{k=} must be >= 1')
    if c is not None and (c <= 0 or c >=1):
        raise ValueError(f'{c=} must be in the range 0 < c < 1')
    if nmax is not None and nmax < 1:
        raise ValueError(f'{nmax=} must be >= 1')    



'''
### Test ###
if __name__ == '__main__':
    print(sig2pct(-3, bound='2-sided'), sig2pct(3, bound='1-sided')) # -0.99730, 0.99865
    print(pct2sig(0.9973002, bound='2-sided'), pct2sig(0.0013499, bound='1-sided')) # 3, -3
    print('TI')
    print(order_stat_TI_n(k=2, p=0.99, c=0.90, bound='2-sided')) # 667
    print(order_stat_TI_p(n=667, k=2, c=0.90, bound='2-sided')) # 0.99001
    print(order_stat_TI_c(n=667, k=2, p=0.99, bound='2-sided')) # 0.90047
    print(order_stat_TI_k(n=667, p=0.99, c=0.90, bound='2-sided')) # 2
    print(order_stat_TI_k(n=20, p=0.99, c=0.90, bound='2-sided')) # Warning message, None
    print('P')
    print(order_stat_P_c(n=1000, k=3, P=0.01, bound='2-sided')) # 0.7367, Table A.15a
    print(order_stat_P_c(n=1000, k=11, P=0.95, bound='1-sided upper')) # 0.9566, Table A.16, 39+11=50
    print(order_stat_P_c(n=1000, k=11, P=0.05, bound='1-sided lower')) # 0.9566, Table A.16, 39+11=50
    print(order_stat_P_k(n=100, c=0.95, P=0.50, bound='2-sided')) # 10, Table A.15g
    print(order_stat_P_k(n=100, c=0.95, P=0.90, bound='1-sided upper')) # 5, Table A.16
    print(order_stat_P_k(n=100, c=0.95, P=0.10, bound='1-sided lower')) # 5, Table A.16
    print(order_stat_P_k(n=10, c=0.999, P=0.05, bound='1-sided lower')) # Warning message, None
    print(order_stat_P_n(k=10, c=0.950, P=0.50, bound='2-sided')) # 108, Table A.15g (conservative)
    print(order_stat_P_n(k=11, c=0.9566, P=0.95, bound='1-sided upper')) # 1018, Table A.16 (conservative)
    print(order_stat_P_n(k=11, c=0.9566, P=0.05, bound='1-sided lower')) # 1018, Table A.16 (conservative)
#'''
