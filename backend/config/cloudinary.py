import os
import cloudinary


def connect_cloudinary():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_SECRET_KEY"),
    )
    print("Cloudinary Connected")
