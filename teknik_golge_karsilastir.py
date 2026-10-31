import pandas as pd
A = pd.read_csv("teknik_golge_referans.csv"); B = pd.read_csv("teknik_golge_dogrula.csv")
a, b = set(zip(A.t.str[:19], A.coin)), set(zip(B.t.str[:19], B.coin))
print(f"referans {len(a)} · canlı kod {len(b)} · ortak {len(a & b)} · yalnız referans {sorted(a - b)[:10]} · yalnız canlı {sorted(b - a)[:10]}")
