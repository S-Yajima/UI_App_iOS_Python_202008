from ctypes import *
from Matrix import *
from Color import *
from file_readline import *


class Vector3(Structure):
	_fields_ = [('x', c_float), 
							('y', c_float),
							('z', c_float)]


# 頂点を意味するクラス(構造体のように利用)
# 入力無しでインスタンス出来るか？
# 	→ 出来る
class Vertex():
	# self.point # Vecter3
	def __init__(self, x=0, y=0, z=0):
		self.point = Vector3(x, y, z)



# 三角形を意味するクラス。
# 三角形メッシュの内部で使用すること。
class Triangle():
	
	# 3つの頂点のindex番号の配列
	# 三角形のインスタンスを直接格納しない事
	# self.vertex_indexes
	
	def __init__(self, vertex_indexes=[]):
		self.vertex_indexes = vertex_indexes


# 三角形メッシュ
# 頂点座標の配列
# 三角形クラスの配列(index番号)
# ToDo: 使い方を考察する
# まず、頂点の配列を生成する
# 次に三角形の配列を生成する
'''
class TriangleMesh():
	
	# 頂点の実体の配列。
	# self.vertexes
	# 三角形の配列
	# self.triangles
	
	def __init__(self, vertexes=[], triangles=[]):
		self.vertexes = vertexes
		self.triangles = triangles
	
	
	def add_vertex(self, vertex):
		self.vertexes.append(vertex)
	
	
	def add_triangle(self, triangle):
		self.triangles.append(triangle)
'''

# 図形
class MyFigure():
	# 三角形メッシュ
	# 頂点の実体の配列。
	# self.vertexes
	# 三角形の配列
	# self.triangles
	
	# 球の中心
	#center =  Vector3(0, 0, 0)
	
	# 進行ベクトル
	#proceed_vector = Vector3(0, 0, 0)
	
	# 回転角度
	rotate_angle_x = 0
	rotate_angle_y = 0
	rotate_angle_z = 0
	
	# スケーリング行列処理の倍率
	magnification = 0
	
	# 鏡面度　10 〜 20
	specular = 20
	
	
	def __init__(self, path, radius=10, center_x=0, center_y=0, center_z=0, is_hide=False):
		self.vertexes = []
		self.triangles = []
		
		self.center =  Vector3(0, 0, 0)
		self.set_center(center_x, center_y, center_z)
		self.proceed_vector = Vector3(0, 0, 0)
		
		self.face_color = Color(0.0, 0.0, 0.0, 1.0)
		self.is_hide = is_hide
		
		# objファイル読み込み
		lines = read_file_line(path)
		vertexes = vertex_list(lines)
		triangles = triangle_list(lines)
		
		# 頂点座標
		for vertex in vertexes:
			x = vertex[0]
			y = vertex[1]
			z = vertex[2]
			self.add_vertex(Vertex(x, y, z))
		
		# 三角形を生成する
		for triangle in triangles:
			# 頂点x,y,z座標の配列を格納する
			self.add_triangle(Triangle(triangle))
		
		
	
	def add_vertex(self, vertex):
		self.vertexes.append(vertex)
	
	
	def add_triangle(self, triangle):
		self.triangles.append(triangle)
	
	
	def set_face_color(self, r, g, b, a=1.0):
		self.face_color.r = r
		self.face_color.g = g
		self.face_color.b = b
		self.face_color.a = a
	
	
	def face_color_value(self):
		return (
			self.face_color.r, self.face_color.g, self.face_color.b, self.face_color.a)
		

	# 頂点座標を全て返す
	# 配列：[[[x,y,z],[x,y,z],[x,y,z]],[[]...
	# 
	def points(self):
		result = []
		
		for triangle in self.triangles:
			triangle_vertexes = []
			for index in triangle.vertex_indexes:
				vertex = self.vertexes[int(index)]
				triangle_vertexes.append([vertex.point.x, vertex.point.y, vertex.point.z])
				
			result.append(triangle_vertexes)
		
		return result
	
	
	# 回転、移動を反映した座標を返す
	# 配列：[[[x,y,z],[x,y,z],[x,y,z]],[[]...
	def local_points(self):
		result = []
		
		# 行列計算の関数で移動した座標を算出する
		# 円図形の頂点を算出する
		trans_matrix = [[0, 0, 0, 0], 
										[0, 0, 0, 0], 
										[0, 0, 0, 0]]
		trans_matrix = make_Translation_Matrix(trans_matrix, self.center.x, self.center.y, self.center.z)
		
		
		# 行列計算の関数でX軸に回転した座標を算出する
		rotat_matrix_x = [[0, 0, 0, 0], 
											[0, 0, 0, 0], 
											[0, 0, 0, 0]]
		rotat_matrix_x = make_Rotation_X_Matrix(rotat_matrix_x, self.rotate_angle_x)
		
		
		# 行列計算の関数でY軸に回転した座標を算出する
		rotat_matrix_y = [[0, 0, 0, 0], 
											[0, 0, 0, 0], 
											[0, 0, 0, 0]]
		rotat_matrix_y = make_Rotation_Y_Matrix(rotat_matrix_y, self.rotate_angle_y)
		
		# 行列計算の関数でZ軸に回転した座標を算出する
		rotat_matrix_z = [[0, 0, 0, 0], 
											[0, 0, 0, 0], 
											[0, 0, 0, 0]]
		rotat_matrix_z = make_Rotation_Z_Matrix(rotat_matrix_z, self.rotate_angle_z)
		
		'''
		# Todo: 回転行列を一つにまとめる -----------
		rotat_matrix_xy = [[0, 0, 0, 0], 
										[0, 0, 0, 0], 
										[0, 0, 0, 0]]
		# x、yを行列同士の掛け算でまとめる
		for i in range(0, 3):
			for j in range(0, 3):
				rotat_matrix_xy[i][j] = rotat_matrix_x[i][0] * rotat_matrix_y[0][j] + rotat_matrix_x[i][1] * rotat_matrix_y[1][j] + rotat_matrix_x[i][2] * rotat_matrix_y[2][j]
				
		rotat_matrix = [[0, 0, 0, 0], 
										[0, 0, 0, 0], 
										[0, 0, 0, 0]]
		for i in range(0, 3):
			for j in range(0, 3):
				rotat_matrix[i][j] = rotat_matrix_xy[i][0] * rotat_matrix_z[0][j] + rotat_matrix_xy[i][1] * rotat_matrix_z[1][j] + rotat_matrix_xy[i][2] * rotat_matrix_z[2][j]
		# -----------------------------------
		'''
		triangles = self.points()
		
		for triangle in triangles:
			triangle_vertexes = []
			for point in triangle:
				
				# X軸回転
				r_x, r_y, r_z = transform3D(point, rotat_matrix_x)
				# Y軸回転
				r_x, r_y, r_z = transform3D([r_x, r_y, r_z], rotat_matrix_y)
				# Z軸回転
				r_x, r_y, r_z = transform3D([r_x, r_y, r_z], rotat_matrix_z)
				
				'''
				# Todo: 回転行列を一つにまとめる -----------
				r_x, r_y, r_z = transform3D(point, rotat_matrix)
				'''
				# 移動
				r_x, r_y, r_z = transform3D([r_x, r_y, r_z], trans_matrix)
				triangle_vertexes.append([r_x, r_y, r_z])
				
			result.append(triangle_vertexes)
				
		return result
		
	
	# 球の中心座標を設定する
	# 初期設定、減り込み対応などに使用する
	def set_center(self, x, y, z):
		self.center.x = x
		self.center.y = y
		self.center.z = z
		
	
	# 進行ベクトルを設定する
	def set_proceed_vector(self, x, y, z):
		self.proceed_vector.x = x
		self.proceed_vector.y = y
		self.proceed_vector.z = z
	
	
	# 進行ベクトルによる球の移動
	def proceed(self):
		self.set_center(
			self.center.x + self.proceed_vector.x,
			self.center.y + self.proceed_vector.y,
			self.center.z + self.proceed_vector.z)
	


if __name__ == '__main__':
	
	pass
