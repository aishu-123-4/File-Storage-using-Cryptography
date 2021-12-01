import tool
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from rsa import decrypt

def Algo1(key):
	f = Fernet(key)
	with open("raw_data/store_in_me.enc","rb") as target_file:
		secret_data = target_file.read()
		data = f.decrypt(secret_data)
	return data

def Algo1_extend(filename, key1, key2):
	f = MultiFernet([Fernet(key1),Fernet(key2)])
	source_filename = 'encrypted/' + filename
	target_filename = 'files/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename, 'rb') as file:
			raw = file.read()
			secret_data = f.decrypt(raw)
			target_file.write(secret_data)
	
def Algo2(filename, key, nonce):
	aad = "authenticated but unencrypted data"
	associated_data = aad.encode('utf-8')
	chacha = ChaCha20Poly1305(key)
	source_filename = 'encrypted/' + filename
	target_filename = 'files/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename, 'rb') as file:
			raw = file.read()
			secret_data = chacha.decrypt(nonce, raw, associated_data)
			target_file.write(secret_data)


def Algo3(filename, key, nonce):
	aad = "authenticated but unencrypted data"
	associated_data = aad.encode('utf-8')
	aesgcm = AESGCM(key)
	source_filename = 'encrypted/' + filename
	target_filename = 'files/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename, 'rb') as file:
			raw = file.read()
			secret_data = aesgcm.decrypt(nonce, raw, associated_data)
			target_file.write(secret_data)

	
def Algo4(filename, key, nonce):
	aad = "authenticated but unencrypted data"
	associated_data = aad.encode('utf-8')
	aesccm = AESCCM(key)
	source_filename = 'encrypted/' + filename
	target_filename = 'files/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename, 'rb') as file:
			raw = file.read()
			secret_data = aesccm.decrypt(nonce, raw, associated_data)
			target_file.write(secret_data)
	
def rsa_decrypt(filename, key):
	source_filename = 'encrypted/' + filename
	target_filename = 'files/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename, 'rb') as file:
			raw = file.read()
			secret_data = decrypt(raw, key)
			target_file.write(secret_data)

def decryption():
	tool.empty_folder('files')
	key_1 = ""
	list_directory = tool.list_dir('key')
	filename = './key/' + list_directory[0]
	
	with open(filename,"rb") as public_key:
		key_1 = public_key.read()
	
	secret_information = Algo1(key_1)
	split_key = ":::::"
	split_key_bytes = split_key.encode('utf-8')
	list_information = secret_information.split(split_key_bytes)
	rsa_key_bytes = list_information[0]
	rsa_key  = rsa_key_bytes.decode('utf-8').split(";;;")
	private_key = (int(rsa_key[0]), int(rsa_key[1]))
	key_1_1 = list_information[1]
	key_1_2 = list_information[2]
	key_2 = list_information[3]
	key_3 = list_information[4]
	key_4 = list_information[5]
	nonce12 = list_information[6]
	nonce13 = list_information[7]
	files = sorted(tool.list_dir('encrypted'))
	for index in range(len(files)):
		if index%5 == 0:
			Algo1_extend(files[index],key_1_1,key_1_2)
		elif index%5 == 1:
			Algo2(files[index],key_2,nonce12)
		elif index%5 == 2:
			Algo3(files[index],key_3,nonce12)
		elif index%5 == 3:
			rsa_decrypt(files[index], private_key)
		else:
			Algo4(files[index],key_4,nonce13)