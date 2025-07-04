from os import getenv, path, makedirs
from dotenv import load_dotenv
from publishers.FacebookPublisher import FacebookPublisher
import requests
import time, torch
from utils.Utils import urlify
from openai import OpenAI
import json
from diffusers import DiffusionPipeline

from exceptions import ImageGenerationException, ConfigurationException

load_dotenv()

def run_text_to_image(save_image_path: str = "output.png"):
    # Use a publicly available Stable Diffusion model instead of the gated one
    from diffusers import StableDiffusionPipeline
    
    # Use the standard Stable Diffusion 1.5 model which is publicly accessible
    pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    
    # Use CPU if CUDA is not available, otherwise use CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)
    
    print(f"Generating image, using device: {device}")

    image = pipe(
        "Sunlight filters through a dense canopy of broad leaves, dappling the forest floor in shades of emerald and gold.",
        num_inference_steps=20,  # Reduced for faster generation
        guidance_scale=7.5,      # Standard guidance scale for SD 1.5
    ).images[0].save(save_image_path)

    print(f"Image saved to: {save_image_path}")

def get_api_key() -> str:
    api_key = getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("ERROR: Create an API key from openrouter.com and set it in your .env file as OPENROUTER_API_KEY!")
        exit(1)

def _create_aihorde_payload(prompt: str) -> dict:
    """Create the payload for AI Horde image generation request."""
    return {
        "prompt": prompt,
        "params": {
            "sampler_name": "k_euler",
            "cfg_scale": 7.5,
            "denoising_strength": 1.0,
            "seed": "342",
            "height": 512,
            "width": 512,
            "steps": 30
        },
        "nsfw": True,
        "trusted_workers": True,
        "slow_workers": True,
        "censor_nsfw": False,
        "workers": [],
        "worker_blacklist": False,
        "models": ["stable_diffusion"],
        "source_image": "",
        "source_processing": "img2img",
        "source_mask": "",
        "r2": True,
        "shared": False,
        "replacement_filter": True
    }

def _poll_aihorde_job_completion(job_id: str, api_key: str, prompt: str) -> None:
    """Poll AI Horde job until completion or failure."""
    check_url = f"https://stablehorde.net/api/v2/generate/check/{job_id}"
    headers = {"apikey": api_key}
    
    while True:
        check_response = requests.get(check_url, headers=headers)
        check_response.raise_for_status()
        check_result = check_response.json()
        
        if check_result.get("done", False):
            print("Image generation completed!")
            break
        elif check_result.get("faulted", False):
            raise ImageGenerationException(
                "Image generation failed on AI Horde",
                prompt=prompt[:100] + "...",
                details={"job_id": job_id, "status": check_result}
            )
        else:
            wait_time = check_result.get("wait_time", 30)
            print(f"Still processing... waiting {wait_time} seconds")
            time.sleep(min(wait_time, 30))  # Wait max 30 seconds between checks

def _download_and_save_image(image_url: str, prompt: str) -> str:
    """Download image from URL and save to local file."""
    print(f"Downloading image from: {image_url}")
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    
    # Generate filename based on prompt
    safe_filename = urlify(prompt[:50]) + ".png"  # Limit filename length
    image_path = f"./output/images/{safe_filename}"
    
    # Ensure images directory exists
    makedirs("./output/images", exist_ok=True)
    
    with open(image_path, 'wb') as f:
        f.write(image_response.content)
    
    print(f"Image saved to: {image_path}")
    return image_path

def get_image(method: str, from_text: str) -> str:
    """Generate an image from text using the specified method."""
    if method == "aihorde":
        return _generate_image_with_aihorde(from_text)
    else:
        raise ImageGenerationException(
            f"Unknown image generation method: {method}",
            details={"method": method, "supported_methods": ["aihorde"]}
        )

def _generate_image_with_aihorde(from_text: str) -> str:
    """Generate image using AI Horde service."""
    aihorde_api_key = getenv('AIHORDE_API_KEY')
    if not aihorde_api_key:
        raise ConfigurationException(
            "AI Horde API key is not set",
            config_key="AIHORDE_API_KEY",
            details={"solution": "Create an API key from AI Horde and set it in your .env file"}
        )
    
    api_url = "https://stablehorde.net/api/v2/generate/async"
    
    try:
        # Create request payload and headers
        payload = _create_aihorde_payload(from_text)
        headers = {
            "apikey": aihorde_api_key,
            "Content-Type": "application/json"
        }
        
        # Submit the generation request
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        job_id = result.get("id")
        
        if not job_id:
            raise ImageGenerationException(
                "Failed to get job ID from AI Horde",
                prompt=from_text[:100] + "...",
                details={"api_response": result}
            )
        
        # Poll for completion
        _poll_aihorde_job_completion(job_id, aihorde_api_key, from_text)
        
        # Get the generated image URL
        status_url = f"https://stablehorde.net/api/v2/generate/status/{job_id}"
        status_response = requests.get(status_url, headers={"apikey": aihorde_api_key})
        status_response.raise_for_status()
        status_result = status_response.json()
        
        generations = status_result.get("generations", [])
        if not generations:
            raise ImageGenerationException(
                "No generated images found",
                prompt=from_text[:100] + "...",
                details={"job_id": job_id, "status_result": status_result}
            )
        
        image_url = generations[0].get("img")
        if not image_url:
            raise ImageGenerationException(
                "No image URL found in response",
                prompt=from_text[:100] + "...",
                details={"job_id": job_id, "generations": generations}
            )
        
        # Download and save the image
        return _download_and_save_image(image_url, from_text)
        
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        raise ImageGenerationException(
            f"AI Horde image generation failed: {str(e)}",
            prompt=from_text[:100] + "...",
            details={"error": str(e), "method": "aihorde"}
        )
    except ImageGenerationException:
        # Re-raise our specific exceptions
        raise
    except Exception as e:
        raise ImageGenerationException(
            f"Unexpected error during AI Horde image generation: {str(e)}",
            prompt=from_text[:100] + "...",
            details={"error": str(e), "method": "aihorde"}
        )        

if __name__ == "__main__":
    # publisher = FacebookPublisher(getenv('FBIG_PAGE_ID'))
    # publisher.publish()

    # image_urls = [
    #     'https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/ec1e8a13-4e03-4674-93c8-c6073b6fbb1b-0.png'
    #     , 'https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/62dcc3e8-3492-4b6e-aa47-a396151f41f2-0.png'
    #     , 'https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/1c43271e-7a48-47d8-b3a2-0c45ac2be8d8-0.png'
    # ]

    # for count, image_url in enumerate(image_urls):
    #     img_data = requests.get(image_url).content
    #     scenery_title = "Scenery {number}".format(number=(count + 1))
    #     img_name = './images/' + urlify(scenery_title) + '.png'
    #     print("Saving image to: ", img_name)
    #     output_path = path.join(img_name)
    #     with open(output_path, 'wb') as fh:
    #         fh.write(img_data)

    # api_key = get_api_key()
    
    # # Debug: Print the full authorization header
    # auth_header = f"Bearer {api_key}"
    
    # response = requests.post(
    #     url="https://openrouter.ai/api/v1/chat/completions",
    #     headers={
    #         "Authorization": auth_header,
    #         "Content-Type": "application/json",
    #         "HTTP-Referer": "https://localhost:8501",
    #         "X-Title": "Story Teller App",
    #     },
    #     data=json.dumps({
    #         "model": "google/gemma-3-27b-it:free", 
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": "Hello, can you respond with 'API working'?"
    #             }
    #         ],
    #     })
    # )

    # run_text_to_image()
    get_image("aihorde", "Create ultra-detailed and hyper-realistic scene with cinematic lightning, 8k resolution and sharp focus, described as: A nimble monkey enjoys fruits among the trees, while a pair of crocodiles lurk in the water.")
