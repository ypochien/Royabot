import config
import shioaji as sj

api = sj.Shioaji()
api.login(config.API_KEY,config.SECRET_KEY,fetch_contract=False)
daily_quote = api.daily_quotes()
print(daily_quote)
