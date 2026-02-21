* CTF용 취약 구현 포함, 실서비스 사용 금지
Setup (Windows PowerShell)

1) Create venv and install
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt

2) Set env
copy .env.example .env

3) Init DB
$env:FLASK_APP="app.py"
flask db init
flask db migrate -m "init schema"
flask db upgrade

4) Seed
flask seed

5) Run
flask run

Default accounts:
- admin / admin1234
- user1 / user1234
- user2 / user1234