import tool

def divide(username: str):
	tool.empty_folder('files')
	tool.empty_folder('raw_data')
	FILE = tool.list_dir('uploads')
	FILE = './uploads/'+FILE[0]

	max = 1024*32						
	buff  = 50*1024*1024*1024  			

	chapters = 0
	uglybuf  = ''
	with open('raw_data/meta_data.txt','w') as meta_data:
		with open('file_details/meta_data.txt','a') as file_data:
			file__name = FILE.split('/')
			file__name = file__name[-1]
			print(file__name)
			meta_data.write(f"File_Name={file__name}\n")
			file_data.write(f"File_Name={file__name}\n")
			with open(FILE, 'rb') as src:
				while True:
					target_file = open('files/SECRET' + '%07d' % chapters, 'wb')
					written = 0
					while written < max:
						if len(uglybuf) > 0:
							target_file.write(uglybuf)
						target_file.write(src.read(min(buff, max - written)))
						written += min(buff, max - written)
						uglybuf = src.read(1)
						if len(uglybuf) == 0:
							break
					target_file.close()
					if len(uglybuf) == 0:
						break
					chapters += 1
			meta_data.write(f"chapters={(chapters+1)}\n")
			meta_data.write(f"user={username}\n")
			file_data.write(f"chapters={(chapters+1)}\n")
			file_data.write(f"user={username}\n")
	return file__name