from Matrix import *

# 壁
class  Wall():
	
	a_x = 0
	a_y = -400
	a_z = 300
	b_x = 0
	b_y = 200
	b_z = 300
	c_x = 0
	c_y = 200
	c_z = -300
	d_x = 0
	d_y = -400
	d_z = -300
	
	
	def __init__(self, x=0, y=0, z=0):
		self.rotate_angle_y = 0
		self.position = [x, y, z]
		self.normal = [1, 0, 0]
	
	
	# 回転角度を設定し、法線を更新する
	def set_angle_y(self, angle_y):
		self.rotate_angle_y = angle_y
		
		# 行列計算の関数でY軸に回転した座標を算出する
		'''
		rotat_matrix_y = [[0, 0, 0, 0], 
											[0, 0, 0, 0], 
											[0, 0, 0, 0],
											[0, 0, 0, 0]]
		'''
		rotat_matrix_y = make_Rotation_Y_Matrix(self.rotate_angle_y)
		point_a = transform3D([self.a_x, self.a_y, self.a_z], rotat_matrix_y)
		point_b = transform3D([self.b_x, self.b_y, self.b_z], rotat_matrix_y)
		point_c = transform3D([self.c_x, self.c_y, self.c_z], rotat_matrix_y)
		
		vector_AB = [point_b[0] - point_a[0], 
								point_b[1] - point_a[1], 
								point_b[2] - point_a[2]]
		vector_AC = [point_c[0] - point_a[0], 
								point_c[1] - point_a[1], 
								point_c[2] - point_a[2]]
		cross_vector = cross_product(vector_AB, vector_AC)
		# 法線を算出し設定する
		normal = normalize(cross_vector)
		self.normal = [normal[0], normal[1], normal[2]]
	
	
		
	# 四辺の座標を二次元配列で返す
	# return [[A_x,A_y,A_x],[B_x,B_y,B_z],
	#					[C_x,C_y,C_x],[D_x,D_y,D_z]]
	def points(self):
		r_points = []
		
		# 行列計算の関数でY軸に回転した座標を算出する
		rotat_matrix_y = make_Rotation_Y_Matrix(self.rotate_angle_y)
		
		point_a = transform3D([self.a_x, self.a_y, self.a_z], rotat_matrix_y)
		point_b = transform3D([self.b_x, self.b_y, self.b_z], rotat_matrix_y)
		point_c = transform3D([self.c_x, self.c_y, self.c_z], rotat_matrix_y)
		point_d = transform3D([self.d_x, self.d_y, self.d_z], rotat_matrix_y)
		
		r_points.append(point_a)
		r_points.append(point_b)
		r_points.append(point_c)
		r_points.append(point_d)
		
		return r_points
		
