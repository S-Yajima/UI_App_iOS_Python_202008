from math import cos
from math import sin
from math import radians
from math import degrees
from math import isclose
from math import sqrt


# 4×4正方行列同士の掛け算をし、一つの行列にまとめ返す
# 4×4限定
# mat_a : 4×4 行列 A
# mat_b : 4×4 行列 B
# mat_a の行とmat_b の列の内積の値を算出し、戻り値の行列の要素とする。
# mat_aとmat_bは不可逆。前後逆で結果が異なる。
def multipl_Matrix(mat_a, mat_b):
	
	new_mat = [[0] * 4 for i in range(4)]
	
	for i in range(0, 4):
		for j in range(0, 4):
			new_mat[i][j] = mat_a[i][0] * mat_b[0][j] + mat_a[i][1] * mat_b[1][j] + mat_a[i][2] * mat_b[2][j] + mat_a[i][3] * mat_b[3][j]
				
	return new_mat


# 光源に対する地面の影を描画する行列
# light_v3: オブジェクトからの光源の方向.
# 光源の位置ではない点に注意
def make_Shadow_With_LightPos_Matrix(light_v3):
	matrix = [[0] * 4 for i in range(4)]
	
	l_x = light_v3[0]
	l_y = light_v3[1]
	l_z = light_v3[2]
	
	# Todo: 0割り算に対応
	if l_y == 0:
		l_y = 0.000001
	
	matrix[0][0] = 1; matrix[0][1] = -1 * (l_x / l_y); matrix[0][2] = 0; matrix[0][3] = 0
	matrix[1][0] = 0; matrix[1][1] = 0; matrix[1][2] = 0; matrix[1][3] = 0
	matrix[2][0] = 0; matrix[2][1] = -1 * (l_z / l_y); matrix[2][2] = 1; matrix[2][3] = 0
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1

	return matrix


# normalで指定した方向に図形をスケーリングする
# normal スケーリングする方向の単位ベクトル
# k 倍率 > 0 スケーリング
# 			= 0 正投影　、　< 0 リフレクション
def make_Scale_With_Vector_Matrix(normal, k):
	matrix = [[0] * 4 for i in range(4)]
	
	n_x = normal[0]
	n_y = normal[1]
	n_z = normal[2]
	
	matrix[0][0] = 1 + (k - 1) * (n_x**2); matrix[0][1] = (k - 1) * n_x * n_y; matrix[0][2] = (k - 1) * n_x * n_z; matrix[0][3] = 0
	matrix[1][0] = (k - 1) * n_x * n_y; matrix[1][1] = 1 + (k - 1) * n_y**2; matrix[1][2] = (k - 1) * n_y * n_z; matrix[1][3] = 0
	matrix[2][0] = (k - 1) * n_x * n_z; matrix[2][1] = (k - 1) * n_y * n_z; matrix[2][2] = 1 + (k - 1) * n_z**2; matrix[2][3] = 0
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1
	
	return matrix
	

# normalで指定した平面に図形を投影する
# normal 投影する平面に垂直な単位ベクトル
def make_Projection_Matrix(normal):
	matrix = [[0] * 4 for i in range(4)]
	
	n_x = normal[0]
	n_y = normal[1]
	n_z = normal[2]
	
	matrix[0][0] = 1 - n_x**2; matrix[0][1] = -1 * n_x * n_y; matrix[0][2] = -1 * n_x * n_z; matrix[0][3] = 0
	matrix[1][0] = -1 * n_x * n_y; matrix[1][1] = 1 - n_y**2; matrix[1][2] = -1 * n_y * n_z; matrix[1][3] = 0
	matrix[2][0] = -1 * n_x * n_z; matrix[2][1] = -1 * n_y * n_z; matrix[2][2] = 1 - n_z**2; matrix[2][3] = 0
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1
	
	return matrix
	

# X軸三次元回転行列を返す
# matrix : 4*4 の行列計算の配列
# 
# angle : x軸回転角度
def make_Rotation_X_Matrix(angle):
	matrix = [[0] * 4 for i in range(4)]
	
	radian = radians(angle)
	r_sin = sin(radian)
	r_cos = cos(radian)
	
	matrix[0][0] = 1; matrix[0][1] = 0; matrix[0][2] = 0; matrix[0][3] = 0
	matrix[1][0] = 0; matrix[1][1] = r_cos; matrix[1][2] = -1 * r_sin; matrix[1][3] = 0
	matrix[2][0] = 0; matrix[2][1] = r_sin; matrix[2][2] = r_cos; matrix[2][3] = 0
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1
	
	return matrix


# Y軸三次元回転行列を返す
# matrix : 4*4 の行列計算の配列
# angle : y軸回転角度
def make_Rotation_Y_Matrix(angle):
	matrix = [[0] * 4 for i in range(4)]
	
	radian = radians(angle)
	r_sin = sin(radian)
	r_cos = cos(radian)
	
	matrix[0][0] = r_cos; matrix[0][1] = 0; matrix[0][2] = r_sin; matrix[0][3] = 0
	matrix[1][0] = 0; matrix[1][1] = 1; matrix[1][2] = 0; matrix[1][3] = 0
	matrix[2][0] = -1 * r_sin; matrix[2][1] = 0; matrix[2][2] = r_cos; matrix[2][3] = 0
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1
	
	return matrix


# Z軸三次元回転行列を返す
# matrix : 4*4 の行列計算の配列
# angle : z軸回転角度
def make_Rotation_Z_Matrix(angle):
	matrix = [[0] * 4 for i in range(4)]
	
	radian = radians(angle)
	r_sin = sin(radian)
	r_cos = cos(radian)
	
	matrix[0][0] = r_cos; matrix[0][1] = -1 * r_sin; matrix[0][2] = 0; matrix[0][3] = 0
	matrix[1][0] = r_sin; matrix[1][1] = r_cos; matrix[1][2] = 0; matrix[1][3] = 0
	matrix[2][0] = 0; matrix[2][1] = 0; matrix[2][2] = 1; matrix[2][3] = 0
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1
	
	return matrix
	


# 拡大縮小行列を返す
# matrix : 4*4 の行列計算の配列

def make_Scale_Matrix(scale_x, scale_y, scale_z):
	matrix = [[0] * 4 for i in range(4)]
	
	matrix[0][0] = scale_x; matrix[0][1] = 0; matrix[0][2] = 0; matrix[0][3] = 0
	matrix[1][0] = 0; matrix[1][1] = scale_y; matrix[1][2] = 0; matrix[1][3] = 0
	matrix[2][0] = 0; matrix[2][1] = 0; matrix[2][2] = scale_z; matrix[2][3] = 0
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1
	
	return matrix
	

# 移動行列を返す
# matrix : 4 * 4 の行列計算の配列

def make_Translation_Matrix(trans_x, trans_y, trans_z):
	matrix = [[0] * 4 for i in range(4)]
	
	matrix[0][0] = 1; matrix[0][1] = 0; matrix[0][2] = 0; matrix[0][3] = trans_x
	matrix[1][0] = 0; matrix[1][1] = 1; matrix[1][2] = 0; matrix[1][3] = trans_y
	matrix[2][0] = 0; matrix[2][1] = 0; matrix[2][2] = 1; matrix[2][3] = trans_z
	matrix[3][0] = 0; matrix[3][1] = 0; matrix[3][2] = 0; matrix[3][3] = 1
	
	return matrix


# 行列計算
# vertex : 頂点座標の配列 [x, y, z]
# matrix : 4 * 4 の行列
# return : 線形変換後の3D座標配列　[x, y, z]

# Todo : 4 * 3 から 4 * 4 に変更する
#				 戻り値は4*3 のままで良いか？
# 			 入力は三次元のままで良いか？
#				 
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
# 注意:v1 v2 に渡すベクトルの順序が逆だと
# 計算の意味が変わり結果が異なる
def cross_product(v1, v2):
	return [v1[1] * v2[2] - v1[2] * v2[1],
					v1[2] * v2[0] - v1[0] * v2[2],
					v1[0] * v2[1] - v1[1] * v2[0]]


# ベクトルの長さから正規化を行い返す
# vector [x, y, z]
def normalize(vector):
	normal_v = [0, 0, 0]
	# ベクトルの長さを算出
	length = sqrt(
			vector[0] ** 2 + \
			vector[1] ** 2 + \
			vector[2] ** 2)
	
	if length > 0:
		normal_v[0] = vector[0] / length
		normal_v[1] =	vector[1] / length
		normal_v[2]	= vector[2] / length
	# 法線ベクトルの正規化を実行し返す
	return normal_v
						
						
