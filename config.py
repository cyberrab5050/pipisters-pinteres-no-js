import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JPG_QUALITY = 80
    COUNT_IMAGES = 100
    
    BASE_SIZE_PIXELS = 236
    MOBILE_SIZE_PIXELS = 170
