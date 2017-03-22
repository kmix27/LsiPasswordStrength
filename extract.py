
__all__=["extract_features",
        "extract_list"]



def extract_features(test_pw, overall_char_freq, population_stats):
    assert type(test_pw) == str
    char_freq_mean = pd.Series(overall_char_freq).mean()
    char_freq_std = pd.Series(overall_char_freq).std()
    test_pw = str(test_pw)
    pw_len = len(test_pw)
    dl = distance_list(test_pw)
    medKBD = np.median(dl)
    meanKBD = np.mean(dl)
    stdKBD = np.std(dl)
    upr = len(upperalpha.findall(test_pw))
    lwr = len(loweralpha.findall(test_pw))
    num = len(numeric.findall(test_pw))
    sym = len(symbols.findall(test_pw))
    not_lwr = num + sym + upr
    commonality = testPW_lsi(test_pw)
    not_lwr_prp = not_lwr/pw_len
    num_prp = num/pw_len
    sym_prp = sym/pw_len
    lwr_prp = lwr/pw_len
    upr_prp = upr/pw_len
    try:
        entropy = calculate_entropy(test_pw)
    except(ValueError):
        entropy = log(pow(20,pw_len),2)                 
    char_freq_Z = []
    for char in test_pw:
        char_freq_Z.append((overall_char_freq[char] - char_freq_mean)/char_freq_std)
    char_freq_Z = np.mean(char_freq_Z)
    kbd_Z = (meanKBD - population_stats['kbd_m'])/population_stats['kbd_s']
    lwr_Z = ( lwr - population_stats['lwr_cnt_m'])/population_stats['lwr_cnt_s']
    lwr_prp_Z = (lwr_prp - population_stats['lwr_prp_m'])/population_stats['lwr_prp_s']
    upr_Z = (upr - population_stats['upr_cnt_m'])/population_stats['upr_cnt_s']
    upr_prp_Z = (upr_prp - population_stats['upr_prp_m'])/population_stats['upr_prp_s']
    sym_Z = (sym - population_stats['sym_cnt_m'])/population_stats['sym_cnt_s']
    sym_prp_Z = (sym_prp - population_stats['sym_prp_m'])/population_stats['sym_prp_s']
    num_Z = (num - population_stats['num_cnt_m'])/population_stats['num_cnt_s']
    num_prp_Z = (num_prp - population_stats['num_prp_m'])/population_stats['num_prp_s']
    len_Z = (pw_len - population_stats['len_m'])/ population_stats['len_s']
    ent_Z = (entropy - population_stats['ent_m'])/opulation_stats['ent_s']                                
    pwDict = dict(pw_len=pw_len,medKBD=medKBD,
                meanKBD=meanKBD,stdKBD=stdKBD,
                upr_cnt=upr,lwr_cnt=lwr, 
                num_cnt=num,sym_cnt=sym, 
                not_lwr_cnt=not_lwr,
                not_lwr_prp=not_lwr_prp,
                num_prop=num_prp, symbol_prp=sym_prp,
                lwr_prop=lwr_prp, upr_prp=upr_prp,
                char_freq_Z=char_freq_Z, commonality=commonality/10,
                 kbd_Z=kbd_Z, ent=entropy, ent_Z=ent_Z,
                 lwr_prp_Z=lwr_prp_Z,upr_prp_Z=upr_prp_Z,
                 sym_prp_Z=sym_prp_Z,num_prp_Z=num_prp_Z,
                 len_Z=len_Z, lwr_Z=lwr_Z,
                 upr_Z=upr_Z, sym_Z=sym_Z, 
                 num_Z=num_Z)
    return pwDict


def extract_list(pw_list, overall_char_freq, population_stats):
    passDict = {}
    for pw in pw_list:
        passDict['{}'.format(pw)] = extract_features(w,overall_char_freq=overall_char_freq,population_stats=population_stats)
    return passDict


