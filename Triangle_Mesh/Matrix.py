from math import cos
from math import sin
from math import radians
from math import degrees
from math import isclose
from math import sqrt
#from math import sqrt


# X軸三次元回転行列を返す
# matrix : 3 * 3 の行列計算の配列
# 				ToDo: 4*4も検討する
# angle : x軸回転角度
def make_Rotation_X_Matrix(matrix, angle):
	radian = radians(angle)
	r_sin = sin(radian)
	r_cos = cos(radian)
	
	matrix[0][0] = 1; matrix[0][1] = 0; matrix[0][2] = 0; matrix[0][3] = 0
	matrix[1][0] = 0; matrix[1][1] = r_cos; matrix[1][2] = -1 * r_sin; matrix[1][3] = 0
	matrix[2][0] = 0; matrix[2][1] = r_sin; matrix[2][2] = r_cos; matrix[2][3] = 0
	
	return matrix


# Y軸三次元回転行列を返す
# matrix : 3 * 3 の行列計算の配列
# 				ToDo: 4*4も検討する
# angle : y軸回転角度
def make_Rotation_Y_Matrix(matrix, angle):
	radian = radians(angle)
	r_sin = sin(radian)
	r_cos = cos(radian)
	
	matrix[0][0] = r_cos; matrix[0][1] = 0; matrix[0][2] = r_sin; matrix[0][3] = 0
	matrix[1][0] = 0; matrix[1][1] = 1; matrix[1][2] = 0; matrix[1][3] = 0
	matrix[2][0] = -1 * r_sin; matrix[2][1] = 0; matrix[2][2] = r_cos; matrix[2][3] = 0
	
	return matrix


# Z軸三次元回転行列を返す
# matrix : 3 * 3 の行列計算の配列
# 				ToDo: 4*4も検討する
# angle : z軸回転角度
def make_Rotation_Z_Matrix(matrix, angle):
	radian = radians(angle)
	r_sin = sin(radian)
	r_cos = cos(radian)
	
	matrix[0][0] = r_cos; matrix[0][1] = -1 * r_sin; matrix[0][2] = 0; matrix[0][3] = 0
	matrix[1][0] = r_sin; matrix[1][1] = r_cos; matrix[1][2] = 0; matrix[1][3] = 0
	matrix[2][0] = 0; matrix[2][1] = 0; matrix[2][2] = 1; matrix[2][3] = 0
	
	return matrix
	


# 拡大縮小行列を返す
# matrix : 3 * 3 の行列計算の配列
# 				ToDo: 4*4も検討する

def make_Scale_Matrix(matrix, scale_x, scale_y, scale_z):
	
	matrix[0][0] = scale_x; matrix[0][1] = 0; matrix[0][2] = 0; matrix[0][3] = 0
	matrix[1][0] = 0; matrix[1][1] = scale_y; matrix[1][2] = 0; matrix[1][3] = 0
	matrix[2][0] = 0; matrix[2][1] = 0; matrix[2][2] = scale_z; matrix[2][3] = 0
	
	return matrix
	

# 移動行列を返す
# matrix : 3 * 3 の行列計算の配列
# 				ToDo: 4*4も検討する

def make_Translation_Matrix(matrix, trans_x, trans_y, trans_z):
	
	matrix[0][0] = 1; matrix[0][1] = 0; matrix[0][2] = 0; matrix[0][3] = trans_x
	matrix[1][0] = 0; matrix[1][1] = 1; matrix[1][2] = 0; matrix[1][3] = trans_y
	matrix[2][0] = 0; matrix[2][1] = 0; matrix[2][2] = 1; matrix[2][3] = trans_z
	
	return matrix


# 行列計算
# vertex : 頂点座標の配列[x,y,z]
# matrix : 4 * 3 の行列計算
# 				ToDo: 4*4も検討する
def transform3D(vertex, matrix):
	tmp_x = vertex[0]
	tmp_y = vertex[1]
	tmp_z = vertex[2]
	
	for i in range(0, 3):	# x, y, z
		vertex[i] = tmp_x * matrix[i][0] + tmp_y * matrix[i][1] + tmp_z * matrix[i][2] + 1.0 * matrix[i][3]
	
	return vertex



# 二つのベクトルの内積を求める
# ベクトルの長さで正規化されたベクトル同士の内積は
# 2つのベクトル同士のなす角cosθと同値になる
# v1 [x, y, z]
# v2 [x, y, z]
def dot_product(v1, v2):
	return v1[0] * v2[0] + v1[1] * v2[1] + \
					v1[2] * v2[2]
					
	

# 二つのベクトルの外積を計算して返す
# v1 [x, y, z]
# v2 [x, y, z]
def cross_product(v1, v2):
	return [v1[1] * v2[2] - v1[2] * v2[1],
					v1[2] * v2[0] - v1[0] * v2[2],
					v1[0] * v2[1] - v1[1] * v2[0]]


# ベクトルの長さから正規化を行い返す
# vector [x, y, z]
def normalize(vector):
	# ベクトルの長さを算出
	length = sqrt(
			vector[0] ** 2 + \
			vector[1] ** 2 + \
			vector[2] ** 2)
	
	# 法線ベクトルの正規化を実行し返す
	return  [vector[0] / length, 
						vector[1] / length, 
						vector[2] / length]
						
						
