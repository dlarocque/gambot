BUILDING THE BOT LOCALLY

1. Initializing the Python environment

    `python3 venv .venv`

    `source .venv/bin/activate`

    `pip install -r requirements.txt`

2. Setting up environment variables

    create a '.env' file in /gambot with the following contents

    `DISCORD_TOKEN=<YOUR DISCORD BOT TOKEN>`
    `DISCORD_GUILDS="<GUILDS THE BOT IS CONNECTED TO>"`
    `PSQL_PASS=<YOUR PSQL PASSWORD>`

3. Initializing the PostgresSQL database from command line

    coming soon...

    (for now you have to initialize all the tables and rows yourself)
