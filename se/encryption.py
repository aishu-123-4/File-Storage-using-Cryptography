import tool
import os
from rsa import encrypt,generate_keypair
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.aead import AESCCM

def Algo1(data, key):
	f = Fernet(key)
	with open("raw_data/store_in_me.enc","wb") as target_file:
		secret_data = f.encrypt(data)
		target_file.write(secret_data)

def Algo1_extend(filename, key1, key2):
	f = MultiFernet([Fernet(key1),Fernet(key2)])
	source_filename = 'files/' + filename
	target_filename = 'encrypted/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename,'rb') as file:
			raw = file.read()
			secret_data = f.encrypt(raw)
			target_file.write(secret_data)
def Algo2(filename, key, nonce):
	aad = "authenticated but unencrypted data"
	associated_data = aad.encode('utf-8')
	chacha = ChaCha20Poly1305(key)
	source_filename = 'files/' + filename
	target_filename = 'encrypted/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename,'rb') as file:
			raw = file.read()
			secret_data = chacha.encrypt(nonce, raw, associated_data)
			target_file.write(secret_data)

def Algo3(filename, key, nonce):
	aad = "authenticated but unencrypted data"
	associated_data = aad.encode('utf-8')
	aesgcm = AESGCM(key)
	source_filename = 'files/' + filename
	target_filename = 'encrypted/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename,'rb') as file:
			raw = file.read()
			secret_data = aesgcm.encrypt(nonce, raw, associated_data)
			target_file.write(secret_data)

def Algo4(filename, key, nonce):
	aad = "authenticated but unencrypted data"
	associated_data = aad.encode('utf-8')
	aesccm = AESCCM(key)
	source_filename = 'files/' + filename
	target_filename = 'encrypted/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename,'rb') as file:
			raw = file.read()
			secret_data = aesccm.encrypt(nonce, raw, associated_data)
			target_file.write(secret_data)
def rsa_encrypt(filename, key):
	source_filename = 'files/' + filename
	target_filename = 'encrypted/' + filename
	with open(target_filename,'wb') as target_file:
		with open(source_filename,'rb') as file:
			raw = file.read()
			secret_data = encrypt(raw, key)
			target_file.write(secret_data)

def encryption(filename):
	filename = filename.split(".")[0]
	tool.empty_folder('key')
	tool.empty_folder('encrypted')
	key_1 = Fernet.generate_key()
	key_1_1 = Fernet.generate_key()
	key_1_2 = Fernet.generate_key()
	key_2 = ChaCha20Poly1305.generate_key()
	key_3 = AESGCM.generate_key(bit_length=128)
	key_4 = AESCCM.generate_key(bit_length=128)
	rsa_public_key, rsa_private_key = generate_keypair(nbits=12)
	nonce13 = os.urandom(13)
	nonce12 = os.urandom(12)
	rsa_key = str(rsa_private_key[0]) + ";;;" + str(rsa_private_key[1])
	res_key_bytes = rsa_key.encode('utf-8')
	files = sorted(tool.list_dir('files'))
	print(len(files))
	print(files)
	for index in range(len(files)):
		if index%5 == 0:
			Algo1_extend(files[index],key_1_1,key_1_2)
		elif index%5 == 1:
			Algo2(files[index],key_2,nonce12)
		elif index%5 == 2:
			Algo3(files[index],key_3,nonce12)
		elif index%5 == 3:
			rsa_encrypt(files[index], rsa_public_key)
		else:
			Algo4(files[index],key_4,nonce13)
	
	split_key = ":::::"
	split_key_bytes = split_key.encode('utf-8')

	secret_information = (res_key_bytes) + split_key_bytes + (key_1_1)+ split_key_bytes +(key_1_2)+split_key_bytes+(key_2)+split_key_bytes+(key_3)+split_key_bytes+(key_4)+split_key_bytes+(nonce12)+split_key_bytes+(nonce13)
	
	Algo1(secret_information, key_1)
	file_path = f"./key/{filename}.pem"
	with open(file_path,"wb") as public_key:
		public_key.write(key_1)

	tool.empty_folder('files')