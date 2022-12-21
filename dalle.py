import openai

def generate_image_text_first_source_dalle(prompt, size='1024x1024'):
  response = openai.Image.create(
      prompt="Generate a photo of "+prompt+", digital art, illustration, picture, 4k, detailed, high resolution, Hyper Detail, 8K, HD, full hd, dramatic lighting, ",
      n=9,
      size=size
  )
  image_urls = [item['url'] for item in response['data']]
  return image_urls


def generate_image_text_second_source_dalle(prompt, size='1024x1024', image_data=None):
  response = openai.Image.create_edit(
    image=image_data,
    prompt="Generate a photo of "+prompt+", digital art, illustration, 4k, picture, detailed, high resolution, Hyper Detail, 8K, HD, full hd, dramatic lighting, ",
    n=9,
    size=size
  )
  image_urls = [item['url'] for item in response['data']]
  return image_urls


def generate_image_variations_dalle(image, size='1024x1024'):
  # Use the DALL-E 2 model to modify the image based on the given modifications
  response = openai.Image.create_variation(
      image=image,
      n=9,
      size=size
  )
  image_urls = [item['url'] for item in response['data']]
  return image_urls