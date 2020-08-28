from ctypes import *
from Matrix import *
from Indexes import *

class Vector3(Structure):
	_fields_ = [
		('x', c_float),
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
	
	
# 球
class MySphere():
	# 三角形メッシュ
	# 頂点の実体の配列。
	# self.vertexes
	# 三角形の配列
	# self.triangles
	
	# 球の中心
	#center =  Vector3(0, 0, 0)
	# 球の半径
	radius = 0
	
	# 進行ベクトル
	#proceed_vector = Vector3(0, 0, 0)
	# Y軸を軸にスピンする回転角度
	spin_angle = 0
	
	# 鏡面度　10 〜 20
	specular = 20
	
	
	def __init__(self, radius=10, center_x=0, center_y=0, center_z=0, is_hide=False):
		
		self.vertexes = []
		self.triangles = []

		self.radius = radius
		self.center =  Vector3(0, 0, 0)
		self.proceed_vector = Vector3(0, 0, 0)
		
		step = 18
		
		# 円図形の頂点を算出する
		# ToDo : 重複する頂点座標を無くす
		matrix = [[0, 0, 0, 0], 
					[0, 0, 0, 0],
					[0, 0, 0, 0]]
		
		# 頂点座標
		self.add_vertex(Vertex(0, -1 * radius, 0))
		
		for colmn in range(0, 360, step):
			for angle in range(step, 180, step):
				# 頂点座標の x,y,z 数値を算出する
				x = radius * cos(radians(int(angle) + 270))
				y = radius * sin(radians(int(angle) + 270))
				z = 0
				
				# 行列計算の関数でY軸に回転した座標を算出する
				matrix = make_Rotation_Y_Matrix(matrix, colmn)
				r_x, r_y, r_z = transform3D([x, y, z], matrix)
				# 座標クラスを格納する
				self.add_vertex(Vertex(r_x, r_y, r_z))
				
		# 頂点座標
		self.add_vertex(Vertex(0, radius, 0))
		
		# 三角形を生成する
		triangle_indexes = sphere_index()
		for indexes in triangle_indexes:
			# 頂点x,y,z座標の配列を格納する
			self.add_triangle(Triangle(indexes))

		self.set_center(center_x, center_y, center_z)
	
	
	def add_vertex(self, vertex):
		self.vertexes.append(vertex)
	
	
	def add_triangle(self, triangle):
		self.triangles.append(triangle)
		

	# 頂点座標を全て返す
	# 配列：[[[x,y,z],[x,y,z],[x,y,z]],[[]...
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
		
		# 行列計算の関数でY軸に回転した座標を算出する
		rotat_matrix_y = [[0, 0, 0, 0], 
											[0, 0, 0, 0], 
											[0, 0, 0, 0]]
		rotat_matrix_y = make_Rotation_Y_Matrix(rotat_matrix_y, self.spin_angle)
		
		triangles = self.points()
		
		for triangle in triangles:
			triangle_vertexes = []
			for point in triangle:
				# Y軸回転
				r_x, r_y, r_z = transform3D(point, rotat_matrix_y)
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
	
	
	# 球をスピンする
	def spin(self):
		self.spin_angle += 1


