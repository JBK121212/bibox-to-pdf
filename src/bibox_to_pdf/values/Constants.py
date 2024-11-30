import os


class Constants:
    biboxOauthLoginUrl = 'https://mein.westermann.de/auth/login'
    biboxOauthTokenUrl = 'https://backend.bibox2.westermann.de/token'
    biboxOauthClientId = 'Nvw0ZA8Z'
    biboxBookInfoUrl = 'https://backend.bibox2.westermann.de/v1/api/sync/{}?materialtypes[]=default&materialtypes[]=addon'

    baseOutputPath = os.getenv('BASE_OUTPUT_PATH', default='.')
    bookBaseOutputDir = baseOutputPath + '/books/{}'
    imageOutputDir = bookBaseOutputDir + '/images/'
    imageOutputFile = imageOutputDir + '{}.png'
    pdfOutputDir = bookBaseOutputDir + '/pdfs/'
    pdfOutputFile = pdfOutputDir + '{}.pdf'
