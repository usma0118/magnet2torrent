from web import create_app
import uuid

app=create_app(str(uuid.uuid4()))
app.config['TESTING'] = True
app.run('127.0.0.1',port=8080,debug=True,load_dotenv=True)



# if __name__ == '__main__':
#     tr=transmission_client()
#     t=tr.list()
#     for tort in t:
#         print(tort.name)
#         print(tort.hashString)
#         trackers=tort._fields.get("trackers")
#         for t1 in trackers[0]:
#             print(t1.get("announce"))
#         tr.update_trackers(tort.id,["udp://open.tracker.cl:1337/announce"])
#         print()