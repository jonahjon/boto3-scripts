def dangerous_bug(gimme, dat, loot):
    response = badstuff.send_data(
        user     = gimme
        password = dat
        value    = loot
    )
    return response