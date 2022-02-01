from web import create_app
import uuid

app=create_app(str(uuid.uuid4()))
app.config['TESTING'] = True
app.run('127.0.0.1',port=8080,debug=True,load_dotenv=True)