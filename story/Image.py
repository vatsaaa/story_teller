from dotenv import load_dotenv
from os import getenv, path, makedirs
import requests, time
from string import punctuation
from utils.Utils import make_api_request
from utils.Utils import urlify
from exceptions import ConfigurationException, ImageGenerationException

load_dotenv()

class Image:
    def __init__(self, title: str, path: str, description: str, sentiments: list):
        self.path = path
        self.description = description
        self.sentiments = sentiments
        self.title = title
        self.width = 512
        self.height = 512
        self.t2i_url = getenv('TEXT_TO_IMAGE_URL', "https://stablehorde.net/api/v2/generate/async")
        self.aihorde_api_key = getenv('AIHORDE_API_KEY')
    
    def _create_aihorde_payload(self, prompt: str) -> dict:
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
    
    def _poll_aihorde_job_completion(self, job_id: str, api_key: str, prompt: str) -> None:
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

    def _download_and_save_image(self, image_url: str, prompt: str) -> str:
        print(f"Downloading image from: {image_url}")
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Generate filename based on prompt
        safe_filename = urlify(prompt[:50]) + ".png"  # Limit filename length
        image_path = self.path + f"{safe_filename}"
        
        # Ensure images directory exists
        makedirs(self.path, exist_ok=True)
        
        with open(image_path, 'wb') as f:
            f.write(image_response.content)
        
        print(f"Image saved to: {image_path}")
        return image_path

    def _generate_image_with_aihorde(self, from_text: str) -> str:
        if not self.aihorde_api_key:
            raise ConfigurationException(
                "AI Horde API key is not set",
                config_key="AIHORDE_API_KEY",
                details={"solution": "Create an API key from AI Horde and set it in your .env file"}
            )
        
        api_url = "https://stablehorde.net/api/v2/generate/async"
        
        try:
            # Create request payload and headers
            payload = self._create_aihorde_payload(from_text)
            headers = {
                "apikey": self.aihorde_api_key,
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
            self._poll_aihorde_job_completion(job_id, self.aihorde_api_key, from_text)
            
            # Get the generated image URL
            status_url = f"https://stablehorde.net/api/v2/generate/status/{job_id}"
            status_response = requests.get(status_url, headers={"apikey": self.aihorde_api_key})
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
            return self._download_and_save_image(image_url, from_text)
            
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

    def create(self):
        if not self.t2i_url:
            raise ConfigurationException(
                "TEXT_TO_IMAGE_URL is not set. Please configure it to use Stable Diffusion.",
                config_key="TEXT_TO_IMAGE_URL"
            )

        # Create the scenery prompt using description and sentiments
        scenery_prompt = '''Generate ultra-detailed and hyper-realistic picture in 8k resolution with cinematic lightning and sharp focus for the scene described as: {description}. 
                            Scene sentiments are explained by words such as {sentiments}.
                            '''.format(description=self.description, sentiments=self.sentiments)

        # Use AI Horde for image generation
        try:
            image_path = self._generate_image_with_aihorde(scenery_prompt)
            
            # Use the title to create a better filename
            if self.title:
                scenery_title = urlify(self.title.replace(" ", '').translate(str.maketrans('', '', punctuation)))
                new_image_path = f"./output/images/{scenery_title}.png"
                
                # Rename the file to use the title
                import os
                if os.path.exists(image_path):
                    os.rename(image_path, new_image_path)
                    self.path = new_image_path
                else:
                    self.path = image_path
            else:
                self.path = image_path
                
            return self.path
            
        except (ConfigurationException, ImageGenerationException):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            raise ImageGenerationException(
                "Image generation failed in create method",
                prompt=scenery_prompt[:100] + "...",
                details={"error": str(e)}
            )
    

