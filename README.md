# Ponyfin

### In order to run project:
- Copy repository:
  - ```git clone https://github.com/selvaro/ponyfin.git```
- Go to copied directory:
  - ```cd ponyfin```
- Create .env and redact file for your app:
  - Your .env file must contain following:
    - ```BOT_TOKEN="<your_token>"``` - token of telegram bot
    - ```DB_NAME="<your_database_name>"``` - name for your database
    - ```DB_USER="<your_user_name>"``` - name for admin user
    - ```DB_USER_PASSWORD="<your_password>"``` - password for admin user
    - ```MODEL_NAME="<your_model_name>"``` - model name you are using, in my case llama-3.1-8b-instant
    - ```GROQ_API_KEY="your_key"``` - groq api key to connect to
- Install docker and docker-compose (if not installed)
- Start docker-compose:
  - ```sudo docker-compose up --build -d```
### You should be able to use bot now

If any errors occur, and they most likely will, run ```sudo docker-compose logs <container_name>```. Most errors come from api container, wich is where the AI at, so start looking from there
