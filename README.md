## Telegram Auth Backend for FastAPI/Starlette

### INSTALL

In your FastAPI/Starlette app:
```bash
pip install xtg-auth
```

Add your Telegram Bot API Token to `.env` file as `TgBotToken`:
```dotenv
TgBotToken=0000000000:AAaaaAaAAAaaAAAAaaAAAaAAAaaAaaaaaAA
```

Before running add AuthenticationMiddleware to your app, and set TgAuth object with passed token as backend
```python
from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from tg_ath import TgAuth

app = FastAPI()
TOKEN = env('TgBotToken')
app.add_middleware(AuthenticationMiddleware, backend=TgAuth(TOKEN))
```

### Using:
Protected endpoints expect `Telegram.WebApp.initData` string in `Authorization` header afrer `Tg` prefix in each request.

example:
```
Authorization: Tg user=%7B%22id%22%3A1038938370%2C%22first_name%22%3A%22Crypto%E2%86%94%EF%B8%8FFiat%22%2C%22last_name%22%3A%22%F0%9F%92%B5%F0%9F%92%B6%F0%9F%92%B3%22%2C%22username%22%3A%22ex212%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&chat_instance=-6786124926491770465&chat_type=sender&auth_date=1729138692&hash=32e367eb6019007fdb2bd8f9a08628fb14ebc737df4a0dad3ecd2910b342f488 
```

---
Made with ❤ on top of the [X-Model](https://github.com/XyncNet/x-model) and [Aiogram](https://github.com/aiogram/aiogram).
