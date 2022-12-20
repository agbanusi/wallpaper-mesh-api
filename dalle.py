import openai

def generate_image_text_first_source_dalle(prompt, size='1024x1024'):
  response = openai.Image.create(
      prompt=prompt+", digital art, 4k, detailed, high resolution, 3D, Hyper Detail, 8K, HD, Octane Rendering, Unreal Engine, V-Ray, full hd",
      n=6,
      size=size
  )
  image_urls = [item['url'] for item in response['data']]
  return image_urls


def generate_image_text_second_source_dalle(prompt, size='1024x1024', image_data=None):
  response = openai.Image.create_edit(
    image=image_data,
    prompt=prompt+", digital art, 4k, detailed, high resolution, 3D, Hyper Detail, 8K, HD, Octane Rendering, Unreal Engine, V-Ray, full hd",
    n=6,
    size=size
  )
  image_urls = [item['url'] for item in response['data']]
  return image_urls


def generate_image_variations_dalle(image, size='1024x1024'):
  # Use the DALL-E 2 model to modify the image based on the given modifications
  response = openai.Image.create_variation(
      image=image,
      n=6,
      size=size
  )
  image_urls = [item['url'] for item in response['data']]
  return image_urls