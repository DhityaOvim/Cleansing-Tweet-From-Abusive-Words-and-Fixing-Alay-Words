from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import pandas as pd
import sqlite3
import re

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
db = sqlite3.connect('Gold_Binar.db', check_same_thread=False)

###############################################################################################################
swagger_template = dict(
    info = {
        'title': LazyString(lambda:'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'Dokumentasi API untuk Data Processing dan Modeling')
        }, host = LazyString(lambda: request.host)
    )
swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
    }
swagger = Swagger(app, template=swagger_template, config=swagger_config)


###############################################################################################################

df_abusive = pd.read_sql_query('select * from abusive',db)
df_alay = pd.read_sql_query('select * from new_kamusalay',db)
list_abusive = df_abusive['ABUSIVE'].to_list() 
list_alay = df_alay['ALAY'].to_list()   
list_fixalay = df_alay['FIX_ALAY'].to_list()
###############################################################################################################
# GET 'Welcome to Tweets!'

@swag_from("docs/index.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def test():
	return jsonify({'message' : 'Welcome to Tweets!'})

###############################################################################################################
# GET All Tweet

@swag_from("docs/tweet.yml", methods=['GET'])
@app.route('/tweet', methods=['GET'])
def returnAll():
    df = pd.read_sql_query('SELECT * FROM data_tweet limit 5',db)
    db.commit()
    df_tweet = df.to_dict("records")
    return jsonify(df_tweet) 

###############################################################################################################
# GET Spesifik Tweet
@swag_from("docs/tweet_get.yml", methods=['GET'])
@app.route('/tweet/<id>', methods=['GET'])
def returnOne(id): 
    df = pd.read_sql_query("SELECT * FROM data_tweet where id ='%s'" %(id),db)
    get = df.to_dict("records") 
    db.commit()
    return jsonify(get)

###############################################################################################################
# POST Json
@swag_from("docs/tweet_post.yml", methods=['POST'])
@app.route('/tweet', methods=['POST'])
def addOne():
    teks = request.json
    txt = teks["tweet"]
    txt = str(txt).lower()

    txt = re.sub("[,]", " ,", txt)
    txt = re.sub("[.]", " .", txt)
    txt = re.sub("[?]", " ? ", txt)
    txt = re.sub("[!]", " !", txt)
    txt = re.sub("[\"]", " \"", txt)
    txt = re.sub("[\']", "", txt)
    txt = re.sub("[\\n]", " ", txt)
    txt = re.sub("nya", " nya", txt)
    txt = re.split(' ', txt)

    for kata in txt :
        if kata in list_abusive :
                txt[txt.index(kata)] = txt[txt.index(kata)].replace(kata, '**censored**')
    for kata in txt :
        if kata in list_alay :
            txt[txt.index(kata)] = txt[txt.index(kata)].replace(kata,list_fixalay[list_alay.index(kata)])
    txt = ' '.join(txt)
    txt = re.sub(" ,", ",", txt)
    txt = re.sub(" \.", ".", txt)
    txt = re.sub(" \?", "?", txt)
    txt = re.sub(" \!", "!", txt)
    txt = re.sub(" \"", "\"", txt)
    txt = re.sub(" nya", "nya", txt)

    db.cursor().execute("insert into data_tweet (TWEET, NEW_TWEET) values(?, ?)", (teks["tweet"], txt))
    db.commit()
    return  jsonify(teks["tweet"], txt)


###############################################################################################################
# POST Upload
@swag_from("docs/tweet_upload.yml", methods=['POST'])
@app.route('/tweet/upload', methods=['POST'])
def addUpload():
    file = request.files.get['file']
    txt = pd.read_csv(file, usecols = ['Tweet'], encoding='latin-1')

    for teks in txt["Tweet"] :
        teks = str(teks).lower()
        asli = teks
        teks = re.sub("[,]", " ,", teks)
        teks = re.sub("[.]", " .", teks)
        teks = re.sub("[?]", " ? ", teks)
        teks = re.sub("[!]", " !", teks)
        teks = re.sub("[\"]", " \"", teks)
        teks = re.sub("[\']", "", teks)
        teks = re.sub("[\\n]", " ", teks)
        teks = re.sub("nya", " nya", teks)
        teks = re.split(' ', teks)

        for kata in teks :
            if kata in list_abusive :
                teks[teks.index(kata)] = teks[teks.index(kata)].replace(kata, '**censored**')
        for kata in teks :
            if kata in list_alay :
                a = list_alay.index(kata)
                teks[teks.index(kata)] = teks[teks.index(kata)].replace(kata,list_fixalay[list_alay.index(kata)])
        
        teks = ' '.join(txt)
        teks = re.sub(" ,", ",", teks)
        teks = re.sub(" \.", ".", teks)
        teks = re.sub(" \?", "?", teks)
        teks = re.sub(" \!", "!", teks)
        teks = re.sub(" \"", "\"", teks)
        teks = re.sub(" nya", "nya", teks)

        db.cursor().execute("insert into data_tweet (TWEET, NEW_TWEET) values(?, ?)"(asli, teks))
        db.commit()
    return jsonify ('Berhasil')
###############################################################################################################
# Run Flask
if __name__ == "__main__":
    app.run(debug=True, port=8080)