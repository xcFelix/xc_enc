def progressbar(i, n, bar_length=100):
    progress = float(i) / n
    print(f"\r[%-{bar_length}s] %.2f%%" % ('-' * int(progress * bar_length), progress * 100), end='', flush=True)
