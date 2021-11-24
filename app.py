from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import json
import re
import flask
from shelljob import proc

app = Flask(__name__)

MIME_TYPE = 'text/javascript'

@app.route("/", methods=['GET','POST'])
def view_home():
    return render_template("index.html", title="Home Page")

@app.route("/aws")
def aws():
	return render_template("aws.html", title="Aws")

def show_real_time_output(directory,initialize_proc,terraform_apply_proc,demo_proc,terraform_destroy_proc,applyCommand,destroyCommand):

		os.chdir(directory)
		initialize_proc.run('terraform init')

		while initialize_proc.is_pending():
			lines = initialize_proc.readlines()
			for proc, line in lines:
				yield line+"\n".encode("utf-8")

		terraform_apply_proc.run(applyCommand)

		while terraform_apply_proc.is_pending():
			lines = terraform_apply_proc.readlines()
			for proc, line in lines:
				yield line

		terraform_destroy_proc.run(destroyCommand)

		while terraform_destroy_proc.is_pending():
			lines = terraform_destroy_proc.readlines()
			for proc, line in lines:
				yield line

		os.chdir('..')

def generateApplyCommand(terraform_command_variables_and_value,st="apply"):
    str = "terraform " + st +" --auto-approve  -lock=false "
    for key,value in terraform_command_variables_and_value.items():
    	str += " -var "+key+"=\""+value+"\""
    return str

@app.route("/aws", methods=['POST'])
def aws_post():
	directory = "aws"

	terraform_command_variables_and_value={}

	# configures providers.tf
	if len(request.form.getlist("AlreadyConfigured")) == 0:
		file = request.files['file']
		filename = secure_filename(file.filename)
		file.save(filename)

		lines =[]
		with open(filename) as f:
			lines = f.readlines()

		access_key=None
		secret_key=None

		for line in lines:
			if re.search("access",line,re.IGNORECASE) and re.search("key",line,re.IGNORECASE) and re.search("secret",line,re.IGNORECASE) == None:
				tmp = line.replace(' ','')[:-1]
				result = tmp.find('=')
				access_key=tmp[result+1:]
			if re.search("key",line,re.IGNORECASE) and re.search("secret",line,re.IGNORECASE):
				tmp = line.replace(' ','')
				result = tmp.find('=')
				secret_key=tmp[result+1:]

		if access_key == None or secret_key == None:
			print("Unable to configure aws keys")
			return render_template("aws.html",title="Aws")

		content = '''
			provider "aws" {{
				access_key = "{access_key}"
				secret_key = "{secret_key}"
				region = "us-east-2"
			}}
		'''
		os.chdir(directory)
		provider_file = open("providers.tf", "w")
		provider_file.write(content.format(access_key=access_key,secret_key=secret_key,region="us-east-2"))
		provider_file.close()
		os.chdir("..")
		os.remove(filename)
	else:
		content = '''
			provider "aws" {{
				region = "us-east-2"
			}}
		'''
		os.chdir(directory)
		provider_file = open("providers.tf", "w")
		provider_file.write(content.format(region="us-east-2"))
		provider_file.close()
		os.chdir("..")

	applyCommand=generateApplyCommand(terraform_command_variables_and_value)
	destroyCommand= generateApplyCommand(terraform_command_variables_and_value,"destroy")

	print(applyCommand,destroyCommand)

	return flask.Response( show_real_time_output(directory,proc.Group(),proc.Group(),proc.Group(),proc.Group(),applyCommand,destroyCommand), mimetype= MIME_TYPE )

@app.route("/azure",methods=['GET'])
def azure():
	data = json.loads(open("data/azure_images.json").read())

	lines=[]
	for i in data:
		lines.append({ 'offer' : i['offer'] + i['sku'], 'urn' : i['urn']})

	credentials=[]
	try:
		data2 = json.loads(open("data/azure_credentials.json").read())
		for i in data2['azure_credentials']:
			credentials.append(i['client_id'])
	except:
		print("Please provide azure_credentials.json")

	return render_template("azure.html", title="Azure",opt=lines,credential=credentials)

@app.route("/azure", methods=['POST'])
def azure_post():
	directory = 'azure'

	terraform_command_variables_and_value={}
	cred=request.form['cred']
	
	try:
		data2 = json.loads(open("data/azure_credentials.json").read())
		for i in data2['azure_credentials']:
			if cred==i['client_id']:

				subscription_id = i['subscription_id'].replace(' ','')
				client_id = i['client_id'].replace(' ','')
				client_secret = i['client_secret'].replace(' ','')
				tenant_id = i['tenant_id'].replace(' ','')

				terraform_command_variables_and_value['client_id'] = client_id
				terraform_command_variables_and_value['client_secret'] = client_secret
				terraform_command_variables_and_value['tenant_id'] = tenant_id

				content = '''
					provider "azurerm" {{
						features {{}}
						subscription_id   =  "{subscription_id}"
						client_id         =  "{client_id}"
						client_secret     =  "{client_secret}"
						tenant_id         =  "{tenant_id}"
					}}
				'''
				str = content.format(subscription_id =subscription_id,tenant_id=tenant_id,client_id =client_id,client_secret=client_secret)

				os.chdir(directory)
				provider_file = open('providers.tf','w')
				provider_file.write(str)
				provider_file.close()
				os.chdir('..')

		applyCommand=generateApplyCommand(terraform_command_variables_and_value)
		destroyCommand=generateApplyCommand(terraform_command_variables_and_value,"destroy")
		print(applyCommand,destroyCommand)

		return flask.Response(show_real_time_output(directory,proc.Group(),proc.Group(),proc.Group(),proc.Group(),applyCommand,destroyCommand), mimetype= MIME_TYPE )
	except:
		print("Please provide azure_credentials.json")
		return render_template('error.html')

@app.route("/gcp")
def gcp():
	return render_template("gcp.html",title="gcp")

@app.route("/gcp",methods=["POST"])
def gcp_post():
	directory = "gcp"
	filename = None

	terraform_command_variables_and_value={}

	if len(request.form.getlist("AlreadyConfigured")) == 0:
		file=request.files['file']
		filename = secure_filename(file.filename)
		file.save(os.path.join(os.getcwd() ,directory,filename))
		content = '''
			provider "google" {{
				project     = "{project}"
				credentials = "{filename}"
				region      = "asia-south1"
				zone        = "asia-south1-a"
			}}

			provider "google-beta" {{
				project     = "{project}"
				credentials = "{filename}"
				region      = "asia-south1"
				zone        = "asia-south1-a"
			}}
		'''
		os.chdir(directory)
		provider_file = open("providers.tf", "w")
		provider_file.write(content.format(filename=filename))
		provider_file.close()
		os.chdir("..")
	else:
		content = '''
			provider "google" {}

			provider "google-beta" {}
		'''
		os.chdir(directory)
		provider_file = open("providers.tf", "w")
		provider_file.write(content)
		provider_file.close()
		os.chdir("..")

	applyCommand=generateApplyCommand(terraform_command_variables_and_value)
	destroyCommand= generateApplyCommand(terraform_command_variables_and_value,"destroy")
	print(applyCommand,destroyCommand)

	return flask.Response( show_real_time_output(directory,proc.Group(),proc.Group(),proc.Group(),proc.Group(),applyCommand,destroyCommand), mimetype= MIME_TYPE )

if __name__ == '__main__':
   app.config["TEMPLATES_AUTO_RELOAD"] = True
   app.run(debug = True ,port=2000)
