from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import json
import re
import flask
from shelljob import proc
import subprocess

app = Flask(__name__)

MIME_TYPE = 'text/javascript'

@app.route("/", methods=['GET','POST'])
def view_home():
    return render_template("index.html", title="Home Page")

@app.route("/aws")
def aws():
	return render_template("aws.html", title="Aws")

def run_command(cmd_line, command):
	cmd_line.run(command)

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

		# terraform_destroy_proc.run(destroyCommand)

		# while terraform_destroy_proc.is_pending():
		# 	lines = terraform_destroy_proc.readlines()
		# 	for proc, line in lines:
		# 		yield line

		os.chdir('..')

		if directory == "aws":
			os.system("aws eks --region $(terraform output -raw region) update-kubeconfig --name $(terraform output -raw cluster_name)")
		elif directory == "azure":
			result = subprocess.run(['az', 'account', 'subscription','list'], stdout=subprocess.PIPE)

			result_stdout = result.stdout
			result_json = result_stdout.decode('utf8').replace("'", '"')
			#print(result_json)
			
			# Load the JSON to a Python list & dump it back out as formatted JSON
			data = json.loads(result_json)
			s = json.dumps(data, indent=4, sort_keys=True)
			#print(s)
			data1 = data[0]
			subscription_id=data1['subscriptionId']
			
			set_subscription_cmd="az account set --subscription " + str(subscription_id)
			os.system(set_subscription_cmd)
			#subprocess.run('az', 'account', 'set', '--', 'subscription', subscription_id)

			result = subprocess.run(['az', 'aks', 'list'], stdout=subprocess.PIPE)

			result_stdout = result.stdout
			result_json = result_stdout.decode('utf8').replace("'", '"')
			#print(result_json)
			
			# Load the JSON to a Python list & dump it back out as formatted JSON
			data = json.loads(result_json)
			s = json.dumps(data, indent=4, sort_keys=True)
			#print(s)
			data1 = data[len(data) -1]
			cluster_name=data1['name']
			cluster_resource_group=data1['resourceGroup']

			#print(cluster_name)
			#print(cluster_resource_group)
			get_name_cmd="az aks get-credentials --resource-group " + cluster_resource_group + " --name " + cluster_name
			os.system(get_name_cmd)
			
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
	destroyCommand=generateApplyCommand(terraform_command_variables_and_value,"destroy")

	#print(applyCommand,destroyCommand)

	return flask.Response(show_real_time_output(directory,proc.Group(),proc.Group(),proc.Group(),proc.Group(),applyCommand,destroyCommand), mimetype=MIME_TYPE)

@app.route("/azurelogin",methods=['POST'])
def azurelogin():
	subprocess.run(['az', 'login'])

@app.route("/azure",methods=['GET'])
def azure():
	return render_template("azure.html", title="Azure")

@app.route("/azure", methods=['POST'])
def azure_post():
	directory = 'azure'

	terraform_command_variables_and_value={}
	
	try:
		result = subprocess.run(['az', 'ad', 'sp', 'create-for-rbac', '--skip-assignment'], stdout=subprocess.PIPE)

		result_stdout = result.stdout
		result_json = result_stdout.decode('utf8').replace("'", '"')
		#print(result_json)
		
		# Load the JSON to a Python list & dump it back out as formatted JSON
		data = json.loads(result_json)
		s = json.dumps(data, indent=4, sort_keys=True)
		#print(s)

		#print(data['appId'])
		#print(data['password'])

		os.chdir(directory)
		provider_file = open('terraform.tfvars', 'w')
		str = 'appId = "' + data['appId'] + '"\n' + 'password = "' + data['password'] + '"'
		#print(str)
		provider_file.write(str)
		provider_file.close()
		os.chdir('..')

		applyCommand=generateApplyCommand(terraform_command_variables_and_value)
		destroyCommand=generateApplyCommand(terraform_command_variables_and_value,"destroy")
		#print(applyCommand,destroyCommand)

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
	#print(applyCommand,destroyCommand)

	return flask.Response( show_real_time_output(directory,proc.Group(),proc.Group(),proc.Group(),proc.Group(),applyCommand,destroyCommand), mimetype= MIME_TYPE )

if __name__ == '__main__':
   app.config["TEMPLATES_AUTO_RELOAD"] = True
   app.run(debug = True ,port=2000)
