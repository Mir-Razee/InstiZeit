# from imgurpython import ImgurClient
#
#
# client = ImgurClient(client_id, client_secret)
#
# print(client)
#
# path = 'D:\pic4.jpg'
#
#
# def upload(client, img_path):
#     print("Uploading image... ")
#     image = client.upload_from_path(img_path, anon=False)
#     print("Done")
#     return image['link']
#
# z = upload(client, path)
# print(z)
# from datetime import datetime
#
# # datetime object containing current date and time
# now = datetime.now()
#
# print("now =", now)
#
# # dd/mm/YY H:M:S
# dt_string = now.strftime("%H:%M, %B %d")
# print("date and time =", dt_string)
#
# # from webd import db
# #
# # z = db.execute("SELECT * FROM profile where").fetchall()
# # print(z)

import os
from werkzeug.utils import secure_filename

print(os.path)
s = "image.jpeg"
filename = secure_filename(s.filename)
