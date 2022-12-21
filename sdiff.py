# from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import replicate
# import torch
# model_id = "stabilityai/stable-diffusion-2"

# def generate_image_text_first_source_main(prompt, height, width):
#   # Use the Euler scheduler here instead
#   scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
#   pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, revision="fp16", torch_dtype=torch.float16)
#   pipe = pipe.to("cuda")
#   prompt = prompt+", highly detailed, 8k uhd, ultra realistic, Digital art,"
#   images = pipe(prompt, height=height, width=width, num_outputs=5).images[0:5]
#   print(images)
#   return images


def generate_image_text_first_source(prompt, height, width, image=None):
  model = replicate.models.get("cjwbw/stable-diffusion-v2")
  version = model.versions.get("e5e1fd333a08c8035974a01dd42f799f1cca4625aec374643d716d9ae40cf2e4")
  prompt = "Generate a photo of "+prompt+", highly detailed, 4k, 8k, uhd, ultra realistic, digital art, photo, illustration, elegant, hyperrealistic, concept art, dramatic lighting, "
  if image:
    output = version.predict(prompt=prompt, num_outputs=3, num_inference_steps=50, height=height, width=width, init_image=image, scheduler="DPMSolverMultistep")
  else:
    output = version.predict(prompt=prompt, num_outputs=3, num_inference_steps=50, height=height, width=width, scheduler="DPMSolverMultistep")
  return output

def generate_image_text_first_source_anm(prompt):
  model2 = replicate.models.get("cjwbw/anything-v3.0")
  version2 = model2.versions.get("f410ed4c6a0c3bf8b76747860b3a3c9e4c8b5a827a16eac9dd5ad9642edce9a2")
  prompt = "Generate a photo of "+prompt+", highly detailed, 4k, 8k, uhd, ultra realistic, digital art, photo, illustration, elegant, hyperrealistic, concept art, dramatic lighting, "
  output2 = version2.predict(prompt=prompt, num_outputs=4, num_inference_steps=50, height=768, width=512)
  return output2


def generate_image_variations_diff(image):
  model = replicate.models.get("lambdal/stable-diffusion-image-variation")
  version = model.versions.get("c5e9076afdeb0121f2f2bf427285c2a09abefe1f7413b3c751abe626731b50cb")
  output = version.predict(input_image=image, num_outputs=3, num_inference_steps=30)
  return output