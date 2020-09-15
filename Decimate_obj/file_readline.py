
# line ファイル読み込み結果の二次元配列(各行の内容はスペース区切りで配列化されている)
#  > [1行目のファイル内容, 2行目のファイル内容,...]
# return 二次元配列 [[x,y,z],[x,y,z],[x,y,z],...]
# 頂点座標xyzを含む二次元配列を返す
# ToDo 0の近似値が不測の値になるので余力があれば対応する
def vertex_list(lines):
	result = []
	for colmn in lines:
		if colmn[0] == 'v' and len(colmn) == 4:
			x = round(float(colmn[1]), 4)
			y = round(float(colmn[2]), 4)
			z = round(float(colmn[3]), 4)
			result.append([x, y, z])
		
	return result
	
	

# line ファイル読み込み結果の二次元配列
#  > [1行目のファイル内容, 2行目のファイル内容,...]
# 頂点インデックス番号を含む二次元配列を返す
#  > return 二次元配列 [[頂点aのindex,頂点bのindex,頂点cのindex],[頂点aのindex,頂点bのindex,頂点cのindex],,...]
def triangle_list(line):
	result = []
	for colmn in line:
		if colmn[0] == 'f' and (len(colmn) == 4 or len(colmn) == 5):
			data_x = colmn[1].split('/')
			x = int(data_x[0]) - 1
			data_y = colmn[3].split('/')
			y = int(data_y[0]) - 1
			data_z = colmn[2].split('/')
			z = int(data_z[0]) - 1
			result.append([x, y, z])
			'''
			data_y = colmn[2].split('/')
			y = int(data_y[0]) - 1
			data_z = colmn[3].split('/')
			z = int(data_z[0]) - 1
			result.append([x, y, z])
			'''
	return result
	

# path 読み込むファイルのパス
# return ファイル内容の二次元配列(各行をスペースで区切り２次元配列にする)
# ['v', '-1.76', '-3.13', '1.00'], ['v', '-1.76', '-3.06', '1.00'], ['v', '-1.56', '-2.82', '1.00']
def read_file_line(path):
	
	output = []
	# ファイルが存在しない場合は
	# FileNotFoundEreor
	try:
		with open(path, 'r', encoding='utf-8') as file:
			for line in file:
				
				# line 内の改行文字\nを対処する
				# スペース区切りで配列化する
				#line = line.replace('\n', '')
				colmn = line.replace('\n', '').split(' ')
				
				# カラムが４つまたは５つ
				# 先頭が'v' または　'f'
				output.append(colmn)
				
	# 指定のファイルが見つからない
	except FileNotFoundError as e:
		print(e)
	# 作成しようとしたファイルが既に存在した
	except FileExistsError as e:
		print(e)
	except IOError as e:
		print(e)
	except OSError as e:
		print(e)
	
	#else:		# 何もエラーが発生しなかった場合
		#print('no except.')
	
	finally:
		return output


if __name__ == '__main__':

	#path = '2_vertex.txt'
	path = '4_vertex.txt'
	line = read_file_line(path)
	vertexes = vertex_list(line)
	print(vertexes)
	triangle = triangle_list(line)
	#print(triangle)
