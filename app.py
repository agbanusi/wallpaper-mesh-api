"""Make some requests to OpenAI's chatbot"""
import hashlib
from PIL import Image
import io
import time
import flask
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import g,  request, jsonify
import os
import openai
from flask_cors import CORS, cross_origin
from sdiff import *
from dalle import *
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

prompts = {}
openai.api_key = os.environ["OPENAI"]
# Connect to the MongoDB database
client = MongoClient(os.environ["USERDB"])
db = client["Cluster0"]
# Get the salt value from the environment variable
salt = os.environ["PASSWORD_SALT"]
app = flask.Flask(__name__)
CORS(app)
cloudinary.config( 
  cloud_name = os.environ["CLD_NAME"], 
  api_key = os.environ["CLD_KEY"], 
  api_secret = os.environ["CLD_SECRET"],
  secure = True)

def get_response(message, messages, funcs):
     for func in funcs:
      try:
        # Try the function and return the result if it succeeds
        return func(message, messages)
      except:
        # Catch any exceptions and continue trying the next function
        continue

@app.route('/generate_image', methods=['POST','OPTIONS'])
@cross_origin()
def generate_image():
  try:
    data = request.json
    if not data:
      return jsonify({"status": "failed"}), 400
    text = data['text']
    ip = data['ip']
    if 'size' in data:
      size = data['size']
    else:
      size='512x512'
    
    user = db.chatUsers.find_one({"user": ip})
    resp = generate_image_text_first_source_dalle(text.lower(), size)
    ress = []

    for i in resp:
      res = cloudinary.uploader.upload(i, upload_preset="wallpaper")
      ress.append(res['secure_url'])

    if user:
      db.chatUsers.update_one({"user":ip}, {"$push": {"images": {"$each":ress}}})
    else:
      db.chatUsers.insert_one({"user": ip, "images": ress})
    
    return jsonify({"status": "success", "images": ress})
  except:
    return jsonify({"status": "failed"}), 500


@app.route('/generate_image_2', methods=['POST','OPTIONS'])
@cross_origin()
def generate_image_2():
  try:
    first = time.time()
    data = request.json
    if not data:
        return jsonify({"status": "failed"}), 400
    text = data['text']
    ip = data['ip']
    
    user = db.chatUsers.find_one({"user": ip})
    resp = []
    try:
      resp = generate_image_text_first_source(text.lower(), 896, 512)
    except Exception as e:
      print('error',e)

    ress = []
    for i in resp:
      res = cloudinary.uploader.upload(i, upload_preset="wallpaper")
      ress.append(res['secure_url'])

    if user:
      db.chatUsers.update_one({"user":ip}, {"$push": {"images": {"$each":ress}}})
    else:
      db.chatUsers.insert_one({"user": ip, "images": ress})
    
    second = time.time()
    print(second-first)
    return jsonify({"status": "success", "images": ress})
  except:
    return jsonify({"status": "failed"}), 500

@app.route('/generate_image_3', methods=['POST','OPTIONS'])
@cross_origin()
def generate_image_3():
  try:
    first = time.time()
    data = request.json
    if not data:
        return jsonify({"status": "failed"}), 400
    text = data['text']
    ip = data['ip']
    
    user = db.chatUsers.find_one({"user": ip})
    resp = []
    try:
      resp = generate_image_text_first_source(text.lower()+", anime style, comic style", 896, 512) 
    except Exception as e:
      print('error',e)

    ress = []
    for i in resp:
      res = cloudinary.uploader.upload(i, upload_preset="wallpaper")
      ress.append(res['secure_url'])

    if user:
      db.chatUsers.update_one({"user":ip}, {"$push": {"images": {"$each":ress}}})
    else:
      db.chatUsers.insert_one({"user": ip, "images": ress})
    
    second = time.time()
    print(second-first)
    return jsonify({"status": "success", "images": ress})
  except:
    return jsonify({"status": "failed"}), 500

@app.route('/generate_image_4', methods=['POST','OPTIONS'])
@cross_origin()
def generate_image_4():
  try:
    first = time.time()
    data = request.json
    if not data:
        return jsonify({"status": "failed"}), 400
    text = data['text']
    ip = data['ip']
    
    user = db.chatUsers.find_one({"user": ip})
    resp = []
    try:
      resp = generate_image_text_first_source_anm(text.lower()) 
    except Exception as e:
      print('error',e)
    print(resp)
      
    ress = []

    for i in resp:
      res = cloudinary.uploader.upload(i, upload_preset="wallpaper")
      ress.append(res['secure_url'])

    if user:
      db.chatUsers.update_one({"user":ip}, {"$push": {"images": {"$each":ress}}})
    else:
      db.chatUsers.insert_one({"user": ip, "images": ress})
    
    second = time.time()
    print(second-first)
    return jsonify({"status": "success", "images": ress})
  except:
    return jsonify({"status": "failed"}), 500

def convertImageFormat(imgObj, outputFormat="PNG"):
    newImgObj = imgObj
    if outputFormat and (imgObj.format != outputFormat):
        imageBytesIO = io.BytesIO()
        imgObj.save(imageBytesIO, outputFormat)
        newImgObj = Image.open(imageBytesIO)
    return newImgObj

def image_to_byte_array(image: Image):
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format="PNG")
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

def get_image_dalle(image):
  # Open the image file using Pillow
    width, height = image.size
    crop = min(width, height)
    image = image.crop(
        (
            (width - crop) // 2,
            (height - crop) // 2,
            (width + crop) // 2,
            (height + crop) // 2,
        )
    )
    image_data = image_to_byte_array(image)
    return image_data

@app.route('/modify_image', methods=['POST'])
def modify_image():
    data = request.form
    # if not data:
    #     return jsonify({"status": "failed"}), 400
    # Get the image file from the request
    image_file = request.files.get('file')
    image = Image.open(io.BytesIO(image_file.read()))
    # Open the image file using Pillow
    image_dalle = get_image_dalle(image)
    image = convertImageFormat(image)
    #ip = data['ip']
    if 'size' in data:
      size = data['size']
    else:
      size='1024x1024'

    #user = db.chatUsers.find_one({"user": ip})
    resp1 = generate_image_variations_dalle(image_dalle, size)
    # resp2 = generate_image_text_second_source_dalle("", size, image_dalle)
    #resp2 = generate_image_text_first_source("",  832, 448, io.BytesIO(image_file.read()))
    resp = resp1#+resp2
    ress = []
    for i in resp:
      res = cloudinary.uploader.upload(i, upload_preset="wallpaper")
      ress.append(res['secure_url'])

    # if user:
    #   db.chatUsers.update_one({"user":ip}, {"$push": {"images": {"$each":ress}}})
    # else:
    #   db.chatUsers.insert_one({"user": ip, "images": ress})
    
    return jsonify({"status": "success", "images": ress})


@app.route("/favourites", methods=["GET"])
def favourites():
  # Get the username and password from the request body
  ip = request.args.get('ip')
  # Check if the username is already taken
  user = db.chatUsers.find_one({"user": ip})
  if not user:
    return jsonify({"status": "error", "images": []})
  else:
    resp = db.chatUsers.find_one({'user':ip}, { "images": { "$slice": -50 } })
    return jsonify({"status": "success", "images": resp['images']})


@app.route("/latest", methods=["GET"])
def latest():
  resp = db.chatUsers.aggregate([
      {
          '$unwind': {
              'path': '$images'
          }
      }, {
          '$sort': {
              'images': -1
          }
      }, {
          '$limit': 100
      }
  ])
  resp = list(resp)
  resp = [item['images'] for item in resp]
  return jsonify({"status": "success", "images": resp})

# @app.route('/variance_image', methods=['POST'])
# def variance_image():
#     data = request.json
#     # Get the image file from the request
#     image_file = request.files['image_file']
#     # Open the image file using Pillow
#     image = Image.open(io.BytesIO(image_file.read()))
#     # Convert the image to a format that the DALL-E 2 model can accept
#     image_data = image.tobytes()
#     modifications = data['modifications']
#     size = data['size']

#     # Use the DALL-E 2 model to modify the image based on the given modifications
#     response = openai.Image.create_variation(
#         image=image_data,
#         prompt=modifications+"4k, detailed, high resolution",
#         n=1,
#         size=size
#     )
#     image_urls = [item['url'] for item in response['data']]
#     return jsonify({"status": "success", "images": image_urls})

if __name__ == "__main__":
    #start_browser()
    app.run(port=5001, threaded=False)
