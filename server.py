"""Make some requests to OpenAI's chatbot"""
import hashlib
from PIL import Image
import io
import flask
import base64
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import cloudinary.api
from bson import ObjectId
import jwt
from flask import g,  request, jsonify
import os
import openai
from flask_cors import CORS, cross_origin
from sdiff import *
from dalle import *
import json
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

prompts = {}
openai.api_key = os.environ["OPENAI"]
# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017")
db = client["dev"]
# Get the salt value from the environment variable
salt = os.environ["PASSWORD_SALT"]
APP = flask.Flask(__name__)
CORS(APP)
cloudinary.config( 
  cloud_name = "johnny11", 
  api_key = "276948169559494", 
  api_secret = "uoFEfon8NgujDHmyJ91zmRQ4PP4",
  secure = True)

def get_response(message, messages, funcs):
     for func in funcs:
      try:
        # Try the function and return the result if it succeeds
        return func(message, messages)
      except:
        # Catch any exceptions and continue trying the next function
        continue

# @APP.route("/chat", methods=["POST"])
# def chat():
#     # Get the user ID and message from the request body
#     data = request.json
#     token = data["token"]
#     message = data["message"]

#     # Decode the JWT token
#     claims = jwt.decode(token, APP.config["SECRET_KEY"], algorithms=["HS256"])

#     # Retrieve the user's details from the database
#     user = db.chatUsers.find_one({"_id": ObjectId(claims["user_id"])})
#     if user:
#         # Update the user's message in the database
#         response = get_response(message, user["messages"], [best, next_best, lower_last])
#         print("Response: ", response)
#         db.chatUsers.update_one({"_id": ObjectId(claims["user_id"])}, {"$push": {"messages": {"input":message, "response":response}}})
#         return jsonify({"status": "success", "response":response})
#     else:
#          return jsonify({"status": "error", "message": "Invalid username or password"})
    
# # Define the routes for the login, register, and user storage functionality
# @APP.route("/login", methods=["POST"])
# def login():
#   # Get the username and password from the request body
#   data = request.json
#   username = data["username"]
#   password = data["password"]

#   # Hash the password using SHA-256 and the salt value
#   password_hash = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

#   # Check if the username and password are valid
#   user = db.chatUsers.find_one({"username": username, "password": password_hash})
#   if user:
#     return jsonify({"status": "success", "message": "Login successful", "user_id": str(user["_id"])})
#   else:
#     return jsonify({"status": "error", "message": "Invalid username or password"})

@APP.route("/register", methods=["POST"])
def register():
  # Get the username and password from the request body
  data = request.json
  username = data["username"]
  password = data["password"]

  # Check if the username is already taken
  user = db.chatUsers.find_one({"username": username})
  if user:
    return jsonify({"status": "error", "message": "Username is already taken"})
  else:
      # Hash the password using SHA-256 and the salt value
    password_hash = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    # Insert the new user into the database
    result = db.chatUsers.insert_one({"username": username, "password": password_hash, "messages":[]})
    # Create a JWT token for the user
    token = jwt.encode({"user_id": str(result.inserted_id)}, APP.config["SECRET_KEY"], algorithm="HS256")
    return jsonify({"status": "success", "message": "Registration successful", "user_id": str(result.inserted_id), "token":token})

@APP.route('/generate_image', methods=['POST','OPTIONS'])
@cross_origin()
def generate_image():
    data = request.json
    if not data:
        return jsonify({"status": "failed"}), 400
    text = data['text']
    ip = data['ip']
    if 'size' in data:
      size = data['size']
    else:
      size='1024x1024'
    
    user = db.chatUsers.find_one({"user": ip})
    resp1 = generate_image_text_first_source_dalle(text.lower(), size)
    resp2 = []
    try:
      resp2 = generate_image_text_first_source(text.lower(), 832, 448) + generate_image_text_first_source(text.lower(), 832, 448)
    except:
      print('error')
    resp = resp1 +resp2
    ress = []

    for i in resp:
      res = cloudinary.uploader.upload(i, upload_preset="wallpaper")
      ress.append(res['secure_url'])

    if user:
      db.chatUsers.update_one({"user":ip}, {"$push": {"images": {"$each":ress}}})
    else:
      db.chatUsers.insert_one({"user": ip, "images": ress})
    
    return jsonify({"status": "success", "images": ress})

def convertImageFormat(imgObj, outputFormat="PNG"):
    """Convert image format
    Args:
        imgObj (Image): the Pillow Image instance
        outputFormat (str): Image format, eg: "JPEG"/"PNG"/"BMP"/"TIFF"/...
            more refer: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
    Returns:
        bytes, binary data of Image
    Raises:
    """
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

@APP.route('/modify_image', methods=['POST'])
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


@APP.route("/favourites", methods=["GET"])
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


@APP.route("/latest", methods=["GET"])
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

# @APP.route('/variance_image', methods=['POST'])
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
    APP.run(port=5001, threaded=False)
