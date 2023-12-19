from os import getenv, path
from dotenv import load_dotenv
from publishers.FacebookPublisher import FacebookPublisher
import requests
from utils.Utils import urlify

load_dotenv()

if __name__ == "__main__":
    # publisher = FacebookPublisher(getenv('FBIG_PAGE_ID'))
    # publisher.publish()

    image_urls = [
        'https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/ec1e8a13-4e03-4674-93c8-c6073b6fbb1b-0.png'
        , 'https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/62dcc3e8-3492-4b6e-aa47-a396151f41f2-0.png'
        , 'https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/1c43271e-7a48-47d8-b3a2-0c45ac2be8d8-0.png'
    ]

    for count, image_url in enumerate(image_urls):
        img_data = requests.get(image_url).content
        scenery_title = "Scenery {number}".format(number=(count + 1))
        img_name = './images/' + urlify(scenery_title) + '.png'
        print("Saving image to: ", img_name)
        output_path = path.join(img_name)
        with open(output_path, 'wb') as fh:
            fh.write(img_data)


