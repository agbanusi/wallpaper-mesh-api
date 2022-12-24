import openai

def generate_image_text_first_source_dalle(prompt, size='1024x1024'):
  print('here')
  prompt="Generate a description of "+prompt+", digital art, illustration, picture, 4k, detailed, high resolution, Hyper Detail, 8K, HD, full hd, dramatic lighting, anime style, comic style"
  prompt = enhance_prompt(prompt)
  prompt="Generate a photo of "+prompt+", digital art, illustration, picture, 4k, detailed, high resolution, Hyper Detail, 8K, HD, full hd, dramatic lighting, anime style, comic style"
  response = openai.Image.create(
      prompt=prompt,
      n=9,
      size=size
  )
  image_urls = [item['url'] for item in response['data']]
  return image_urls


def generate_image_text_second_source_dalle(prompt, size='1024x1024', image_data=None):
  prompt="Generate a description of "+prompt+", digital art, illustration, 4k, picture, detailed, high resolution, Hyper Detail, 8K, HD, full hd, dramatic lighting, anime style, comic style",
  prompt = enhance_prompt(prompt)
  prompt="Generate a photo of "+prompt+", digital art, illustration, picture, 4k, detailed, high resolution, Hyper Detail, 8K, HD, full hd, dramatic lighting, anime style, comic style"
  response = openai.Image.create_edit(
    image=image_data,
    prompt=prompt,
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

def enhance_prompt(prompt):
  try:
    model_engine = "text-davinci-003"
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=2048,
        temperature=0.7
    )
    generated_text = completion['choices'][0]['text'].strip()
    return generated_text
  except:
    return prompt