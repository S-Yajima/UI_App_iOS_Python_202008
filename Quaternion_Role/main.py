import ui
import threading
import copy
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from TriangleMesh import *
from Matrix import *
from Camera import *
from Color import *
from Wall import *


# 床。タイルにする。
class  MyFloor():
	position = []
	
	dot_size = 40
	dot_gap = 3
	
	dot_row = 20
	dot_col = 20
	
	def __init__(self, x=0, y=0, z=0):
		self.position = [x, y, z]
	
	
	# 縦、横のインデックスから四辺の座標を二次元配列で返す
	# row, colmun
	# return [[A_x,A_y,A_x],[B_x,B_y,B_z],
	#					[C_x,C_y,C_x],[D_x,D_y,D_z]]
	def points(self, row, colmun):
		r_points = []
		
		# A 左上
		a_x = self.position[0] + (self.dot_size + self.dot_gap) * colmun
		a_y = self.position[1] 
		a_z = self.position[2] - (self.dot_size + self.dot_gap) * row
		
		# B 左下
		b_x = a_x 
		b_y = a_y
		b_z = a_z + self.dot_size
		# C 右下
		c_x = b_x + self.dot_size
		c_y = b_y 
		c_z = b_z
		# D 右上
		d_x = c_x
		d_y = c_y
		d_z = a_z
		
		r_points.append([a_x, a_y, a_z])
		r_points.append([b_x, b_y, b_z])
		r_points.append([c_x, c_y, c_z])
		r_points.append([d_x, d_y, d_z])
		
		return r_points

class MyPole(MyFigure):
	pass


# 背景と床を描画する
class BaseView(ui.View):
	
	screen_depth = 400	# 視点から投影面までの距離
	
	# 床
	floor = None
	# 壁
	wall = Wall()
	
	# スケーリング倍率
	magnification = -1
	
	# 物体の配列
	figures = []
	
	# 視点移動用のカメラ
	camera = MyCamera()
	
	# 光源
	light =  None
	light_x = 150
	light_y = -350
	light_z = 0
	
	# クオータニオン回転軸
	quat_axis_v3 = [0.0, -1.0, 0.0]
	quat_axis_rotate_x = 0
	quat_axis_rotate_y = 0
	quat_axis_rotate_z = 0
	
	
	# 物体を追加する
	def add_figure(self, figure):
		if isinstance(figure, MyFigure) is True:
			self.figures.append(figure)
	
	
	# 床を設定する
	def set_floor(self, floor):
		if isinstance(floor, MyFloor) is True:
			self.floor = floor
	
	
	# 光源の玉を設定する
	def set_light(self, figure):
		if isinstance(figure, MyFigure) is True:
			self.light = figure
	
	
	# クオータニオンの回転軸を算出
	# メンバ変数のxyz回転角度から作成した回転行列で
	# 回転した単位ベクトルを返す
	def quat_axis(self):
		matrix_x = make_Rotation_X_Matrix(self.quat_axis_rotate_x)
		matrix_y = make_Rotation_Y_Matrix(self.quat_axis_rotate_y)
		matrix_z = make_Rotation_Z_Matrix(self.quat_axis_rotate_z)
		
		#print(self.quat_axis_rotate_x)
		
		# 行列同士を掛け算して結合する
		matrix_xy = multipl_Matrix(matrix_y, matrix_x)
		matrix_xyz = multipl_Matrix(matrix_z, matrix_xy)
		
		axis_x = self.quat_axis_v3[0]
		axis_y = self.quat_axis_v3[1]
		axis_z = self.quat_axis_v3[2]
		
		# 単位ベクトルを行列で回転する
		r_x, r_y, r_z = transform3D(
					[axis_x, axis_y, axis_z], matrix_xyz)
					
		#print(r_x, r_y, r_z)
		return (r_x, r_y, r_z)
	
	
	# 三次元空間から二次元スクリーンへの投影を反映する
	# 三次元空間の起点座標(0,0,0)と
	# 二次元の起点座標(0,0)との差分を反映する
	def projection(self, x, y, z):
		# 視点からの距離
		depth = self.screen_depth * -1
		
		# 視点の中心座標
		center_x = self.width / 2
		center_y = self.height / 2
		r_x, r_y = x, y
		if z != 0:
			r_x = ((depth / z) * x) + center_x
			r_y = ((depth / z) * y) + center_y
			
		return (r_x, r_y)

	
	# sort
	# ビュー変換前の状態でソートを実装
	def sort_triangle(self, triangle):
		# 三角形の座標を配列に取得する
		corners = triangle[0]
		# 三角形の座標を数値を浮動小数値変数に取得する
		a_x, a_y, a_z = (corners[0][0], corners[0][1], corners[0][2])
		b_x, b_y, b_z = (corners[1][0], corners[1][1], corners[1][2])
		c_x, c_y, c_z = (corners[2][0], corners[2][1], corners[2][2])
		
		# カメラの位置座標から三角形中心までのベクトルを算出
		scr_vector = [
			self.camera.camera_x - (a_x + b_x + c_x) / 3,
			self.camera.camera_y - (a_y + b_y + c_y) / 3,
			self.camera.camera_z - (a_z + b_z + c_z) / 3]
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2
			
		return length
	
	
	# 図形のソート
	# 戻り値をカメラ位置から図形中心座標までの
	# ベクトルx,y,zの各要素を二乗し足した数値に設定する
	def sort_figure(self, figure):
		# 視点焦点までのベクトルを算出する
		scr_vector = [
			self.camera.camera_x - figure.center.x,
			self.camera.camera_y - figure.center.y,
			self.camera.camera_z - figure.center.z]
		
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2

		return length
	

	
	# 光源のx,y,z座標を返す
	def light_point(self):
		#x, y, z = (0, 0, 0)
		x, y, z = (
			self.light_x, self.light_y, self.light_z, 
		)
		return (x, y, z)
	
	
	# 床を描画
	# light_x ,light_y ,light_z
	# 光源の座標
	def draw_floor(self, light_x ,light_y ,light_z):
		dot_row = self.floor.dot_row
		dot_col = self.floor.dot_col
		
		for row in range(0, dot_row):
			for col in range(0, dot_col):
				point = self.floor.points(row, col)
				a_x, a_y, a_z = self.camera.camera_rotation(point[0][0], point[0][1], point[0][2])
				b_x, b_y, b_z = self.camera.camera_rotation(point[1][0], point[1][1], point[1][2])
				c_x, c_y, c_z = self.camera.camera_rotation(point[2][0], point[2][1], point[2][2])
				d_x, d_y, d_z = self.camera.camera_rotation(point[3][0], point[3][1], point[3][2])
				
				# 法線ベクトルから表裏と陰影を算出する
				# 部品の二辺のベクトルを算出する
				AB_vector = [b_x - a_x, b_y - a_y, b_z - a_z]
				AC_vector = [c_x - a_x, c_y - a_y, c_z - a_z]
				# 外積(法線ベクトル)を算出する
				triangle_cross_product = cross_product(AB_vector, AC_vector)
				# 正規化を行う
				triangle_normal = normalize(triangle_cross_product)
				
				# 視点焦点までのベクトルを算出する
				scr_vector = [
					0 - (a_x + b_x + c_x) / 3,
					0 - (a_y + b_y + c_y) / 3,
					self.screen_depth - (a_z + b_z + c_z) / 3]
				scr_normal = normalize(scr_vector)
				scr_inner = dot_product(triangle_normal, scr_normal)
				
				# 光源までのベクトルを算出する
				light_vector = [
					light_x - (a_x + b_x + c_x) / 3,
					light_y - (a_y + b_y + c_y) / 3,
					light_z - (a_z + b_z + c_z) / 3]
				light_normal = normalize(light_vector)
				# 光源との角度を算出する
				light_inner = dot_product(triangle_normal, light_normal)
				
				# 光源までの距離の二乗
				light_distance = light_vector[0] ** 2 + light_vector[1] ** 2 + light_vector[2] ** 2
				# 透視投影
				p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
				p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
				p_c_x, p_c_y = self.projection(c_x, c_y, c_z)
				p_d_x, p_d_y = self.projection(d_x, d_y, d_z)
				# 床を描画
				path_f = ui.Path()
				path_f.move_to(p_a_x, p_a_y)
				path_f.line_to(p_b_x, p_b_y)
				path_f.line_to(p_c_x, p_c_y)
				path_f.line_to(p_d_x, p_d_y)
				path_f.line_to(p_a_x, p_a_y)
				# 描画色を設定する
				if scr_inner < 0.0:
					color = ui_color([0.15, 0.15, 1.0], light_inner)
					ui.set_color((color[0], color[1], color[2], 1.0))
					
				path_f.fill()
		
		pass



	# 描画
	def draw(self):
		# 光源
		g_light_x, g_light_y, g_light_z = self.light_point()
		light_x ,light_y ,light_z = self.camera.camera_rotation(g_light_x, g_light_y, g_light_z)
		# カメラ位置のビュー座標
		camera_x ,camera_y ,camera_z = self.camera.camera_rotation(
			self.camera.camera_x, 
			self.camera.camera_y, 
			self.camera.camera_z)
		
		# クオータニオン回転軸単位ベクトルを取得
		axis_x, axis_y, axis_z = self.quat_axis()
		
		# 床を描画する
		self.draw_floor(light_x ,light_y ,light_z)
		
		# 図形の座標をビュー座標に変換し配列に格納する
		# 図形をソートする
		sorted_figures = sorted(self.figures, key=self.sort_figure, reverse=True)
		
		# 図形毎に繰り返し、三角形ポリゴンを配列に格納する
		for figure in sorted_figures:
			# 描画フラグを判別
			if figure.is_hide is True:
				continue
			
			triangles = []
			
			# ビュー座標を配列に格納
			# todo : pole とその他の図形を判別 
			if isinstance(figure, MyPole) is True:
				local_points = figure.local_points()
			else:
				local_points = figure.local_points_q(
					axis_x, axis_y, axis_z)
			
			
			for triangle in local_points:
				vertexes = []
				prpjection_vertexes = []
				g_prpjection_vertexes = []
				for vertex in triangle:
					# 本体の図形
					x, y, z = (vertex[0], vertex[1], vertex[2])
					vertexes.append([x, y, z])
					
					# 地面に影を描画
					g_x, g_y, g_z = self.ground_projection(vertex[0], vertex[1], vertex[2], [g_light_x - vertex[0], g_light_y - vertex[1], g_light_z - vertex[2]])
					
					g_prpjection_vertexes.append([g_x, g_y, g_z])
				
				triangles.append([vertexes, 0])
				#triangles.append(prpjection_vertexes)
				triangles.append([g_prpjection_vertexes, 1])
				
			# 取得したビュー座標を視点からの距離でソートする
			sorted_triangles = sorted(triangles, key=self.sort_triangle, reverse=True)

			# ソート済の三角形の配列で描画を行う
			for triangle in sorted_triangles:
				corners = triangle[0]
				a_x, a_y, a_z = (corners[0][0], corners[0][1], corners[0][2])
				b_x, b_y, b_z = (corners[1][0], corners[1][1], corners[1][2])
				c_x, c_y, c_z = (corners[2][0], corners[2][1], corners[2][2])
				
				# ビュー変換
				a_x, a_y, a_z = self.camera.camera_rotation(a_x, a_y, a_z)
				b_x, b_y, b_z = self.camera.camera_rotation(b_x, b_y, b_z)
				c_x, c_y, c_z = self.camera.camera_rotation(c_x, c_y, c_z)
				
				# プロジェクション変換
				p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
				p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
				p_c_x, p_c_y = self.projection(c_x, c_y, c_z)
				
				path_t = ui.Path()
				path_t.move_to(p_a_x, p_a_y)
				path_t.line_to(p_b_x, p_b_y)
				path_t.line_to(p_c_x, p_c_y)
				path_t.line_to(p_a_x, p_a_y)
				
				# 法線ベクトルから表裏と陰影を算出する
				# 部品の二辺のベクトルを算出する
				AB_vector = [b_x - a_x, b_y - a_y, b_z - a_z]
				AC_vector = [c_x - a_x, c_y - a_y, c_z - a_z]
				# 外積(法線ベクトル)を算出する
				triangle_cross_product = cross_product(AB_vector, AC_vector)
				# 正規化を行う
				triangle_normal = normalize(triangle_cross_product)
				
				# 視点焦点までのベクトルを算出する
				scr_vector = [
					camera_x - (a_x + b_x + c_x) / 3,
					camera_y - (a_y + b_y + c_y) / 3,
					camera_z - (a_z + b_z + c_z) / 3]
				
				scr_normal = normalize(scr_vector)
				scr_inner = dot_product(triangle_normal, scr_normal)
				
				# 表裏判別し、描画色を設定する
				if scr_inner < 0.0:
					# 光源までのベクトルを算出する
					light_vector = [
					light_x - (a_x + b_x + c_x) / 3,
					light_y - (a_y + b_y + c_y) / 3,
					light_z - (a_z + b_z + c_z) / 3]
					light_normal = normalize(light_vector)
					# 光源との角度を算出する
					light_inner = dot_product(triangle_normal, light_normal)
					
					# 光源までの距離の二乗
					light_distance = light_vector[0] ** 2 + light_vector[1] ** 2 + light_vector[2] ** 2
						
					# 反射光と視線とのなす角度(cos)を取得する
					specular_inner_cos = specular_inner(light_vector, triangle_normal, scr_normal)
					
					# 色の計算
					color = [0.0, 0.0, 0.0]
					if triangle[1] == 0:
						r, g, b, a = figure.face_color_value()
						color = ui_color([r, g, b], light_inner, specular=20, specular_inner=specular_inner_cos)
					
					ui.set_color((color[0], color[1], color[2], 1.0))
					
					path_t.fill()
		
		# 光源を描画する
		self.draw_light()
		
	# ___ 
	
	# 地面に影を行列で描画する
	# light_v3 : オブジェクトから光源の方向
	def ground_projection(self, x, y, z, light_v3):
		p_x, p_y, p_z = (0, 0, 0)
		
		# 光源から地面に投影行列処理
		projection_matrix = make_Shadow_With_LightPos_Matrix(light_v3)
		#print(projection_matrix)
		p_x, p_y, p_z = transform3D([x, y, z], projection_matrix)
		
		return (p_x, p_y, p_z)


	# 座標x,y,zに対しスケーリング、投影処理を行う
	# x,y,z 壁にスケーリング,投影する対象の座標
	# magnification スケーリング行列処理の倍率
	# =0 正投影　<0 リフレクション　>0 スケーリング
	def wall_projection(self, x, y, z, magnification=0):
		p_x, p_y, p_z = (0, 0, 0)
		# 壁の法線
		wall_normal = self.wall.normal
		# スケーリング行列処理
		projection_matrix = make_Scale_With_Vector_Matrix(wall_normal, magnification)
		p_x, p_y, p_z = transform3D([x, y, z], projection_matrix)
		
		return (p_x, p_y, p_z)


	# 光源のを球として描画する
	def draw_light(self):
		if self.light is None:
			return 
		
		light_x, light_y, light_z = self.light_point()
		self.light.center.x = light_x
		self.light.center.y = light_y
		self.light.center.z = light_z
		
		points = self.light.local_points()
		triangles = []
		for p_triangles in points:
			vertexes = []
			for vertex in p_triangles:
				x, y, z = self.camera.camera_rotation(
				vertex[0], vertex[1], vertex[2])
				vertexes.append([x, y, z])
			triangles.append(vertexes)
			
		for vertexes in triangles:
			a_x, a_y = self.projection(vertexes[0][0], vertexes[0][1], vertexes[0][2])
			b_x, b_y = self.projection(vertexes[1][0], vertexes[1][1], vertexes[1][2])
			c_x, c_y = self.projection(vertexes[2][0], vertexes[2][1], vertexes[2][2])
			
			path = ui.Path()
			path.move_to(a_x, a_y)
			path.line_to(b_x, b_y)
			path.line_to(c_x, c_y)
			path.line_to(a_x, a_y)
			ui.set_color((1.0, 1.0, 1.0, 1.0))
			path.fill()
		pass



# カメラの位置上昇下降
# goal_y: カメラ位置目的y座標値
# add_y: 上昇下降移動量
def change_view_y_schedule(main_view, goal_y, add_y, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
		
	lock.acquire()
	
	main_view.camera.camera_y += add_y
	
	if abs(main_view.camera.camera_y - goal_y) < add_y:
		main_view.camera.camera_y = goal_y
	# ビュー座標を更新する
	main_view.camera.set_camera_coodinate_vector()
	
	lock.release()
	
	if main_view.on_screen is True and isclose(main_view.camera.camera_y, goal_y) is False:
		t = threading.Timer(0.02, change_view_y_schedule, args=[main_view, goal_y, add_y, lock])
		t.start()



# カメラが外周を円旋回する
# angle : 開始カメラアングル
# add_angle : 移動毎のカメラアングル移動角度
# count : 残りの処理回数　０まで繰り返す。
def change_view_round_schedule(main_view, angle, add_angle, count, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
	if count <= 0:
		return
	
	round = 500
	angle += add_angle
	count -= 1
	
	lock.acquire()
	
	main_view.camera.camera_x = round * cos(radians(angle))
	main_view.camera.camera_z = round * sin(radians(angle)) + (-250)
	main_view.camera.set_camera_coodinate_vector()
	
	lock.release()
	
	if main_view.on_screen is True and count > 0:
		t = threading.Timer(0.02, change_view_round_schedule, args=[main_view, angle, add_angle, count, lock])
		t.start()
	

# 目的地座標に移動する
# goal_point : 目的地座標xyz
# frame : 移動に要するコマ数。少ないほど速く移動する。
def set_proceed_figure(figure, goal_point, frame, lock):
	if isinstance(figure, MyFigure) is False:
		return
	
	process_v3 = [
		goal_point[0] - figure.center.x,
		goal_point[1] - figure.center.y,
		goal_point[2] - figure.center.z]
	
	lock.acquire()
	figure.proceed_vector.x = process_v3[0] / frame
	figure.proceed_vector.y = process_v3[1] / frame
	figure.proceed_vector.z = process_v3[2] / frame
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(0.012, proceed_figure, args=[figure, goal_point, lock])
		t.start()
	


# 目的地座標に移動する
# figure : 移動対象の図形
# goal_point : 目的地座標 xyz
def proceed_figure(figure, goal_point, lock):
	if isinstance(figure, MyFigure) is False:
		return
	
	# 進行ベクトルの長さ(の二乗)を算出する
	proceed_length = figure.proceed_vector.x ** 2 + figure.proceed_vector.y ** 2 + figure.proceed_vector.z ** 2
	# 目的地までの距離(の二乗)を算出する
	process_v3 = [
		goal_point[0] - figure.center.x,
		goal_point[1] - figure.center.y,
		goal_point[2] - figure.center.z]
	goal_length = process_v3[0] ** 2 + process_v3[1] ** 2 + process_v3[2] ** 2
	
	lock.acquire()
	is_goal = False
	# 進行ベクトルの長さが目的地までの距離より長い場合
	if proceed_length < goal_length:
		figure.proceed()
	else:
		figure.set_center(
			goal_point[0], goal_point[1], goal_point[2])
		
		figure.proceed_vector.x = 0
		figure.proceed_vector.y = 0
		figure.proceed_vector.z = 0
		is_goal = True
	lock.release()
	
	if main_view.on_screen is True and is_goal is False:
		t = threading.Timer(0.012, proceed_figure, args=[figure, goal_point, lock])
		t.start()



# クオータニオンの回転軸の角度を変更する
# 回転軸を表現するポールの角度も変更する
# pole : クオータニオン回転軸を表現する棒
# diff_x, diff_y, diff_z : 
# クオータニオン回転軸の回転角度移動量
# count : 残りの処理回数。 当メソッドが実行される度にデクリメントされる。 0になるまで繰り返す。
def modefy_Quat_Axis_Angle_order(
	main_view, pole, diff_x, diff_y, diff_z, count, lock):
	if isinstance(main_view, BaseView) is False:
		return
	if count <= 0:
		return
	
	lock.acquire()
	
	main_view.quat_axis_rotate_x += diff_x
	main_view.quat_axis_rotate_y += diff_y
	main_view.quat_axis_rotate_z += diff_z
	
	pole.rotate_angle_x = main_view.quat_axis_rotate_x
	pole.rotate_angle_y = main_view.quat_axis_rotate_y
	pole.rotate_angle_z = main_view.quat_axis_rotate_z
	
	lock.release()
	
	count -= 1
	
	#print(main_view.quat_axis_rotate_x, main_view.quat_axis_rotate_y, main_view.quat_axis_rotate_z)
	
	if main_view.on_screen is True and count > 0:
		t = threading.Timer(0.024, modefy_Quat_Axis_Angle_order, args=[main_view, pole, diff_x, diff_y, diff_z, count, lock])
		t.start()
	

# 数字を順序にクオータニオンで一回転させる
# figures: 数字の配列
# infex : 処理対象の配列figuresのインデックス番号
def rotate_Quat_figure_order(figures, index, lock):
	if index >= len(figures):
		index = 0
		
	figure = figures[index]
	if isinstance(figure, MyFigure) is False:
		return
	
	lock.acquire()
	# 文字が未出現なら出現させる
	if figure.is_hide is True:
		figure.is_hide = False
	
	# クオータニオン回転の角度を増加
	figure.quat_rotate_angle += 15
	
	#一周した場合
	if figure.quat_rotate_angle >= 360:
		figure.quat_rotate_angle = 0
		index += 1
		
		if index >= len(figures):
			index = 0
			delay = 3.5
		else:
			delay = 1.5
		
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(0.048, rotate_Quat_figure_order, args=[figures, index, lock])
		t.start()


# 数字を順序に一回転させる
# figures: 数字の配列
# infex : 処理対象の配列figuresのインデックス番号
def rotate_Y_figure_order(figures, index, lock):
	if index >= len(figures):
		index = 0
		
	figure = figures[index]
	if isinstance(figure, MyFigure) is False:
		return
	
	lock.acquire()
	# 文字が未出現なら出現させる
	if figure.is_hide is True:
		figure.is_hide = False
	
	delay = 0.024
	next_rotate = rotate_Y_figure_order
	
	# y軸の角度を増加
	figure.rotate_angle_y += 45
	
	#一周した場合
	if figure.rotate_angle_y >= 450:
		figure.rotate_angle_y = 90
		index += 1
		#next_rotate = rotate_X_figure_order
		
		if index >= len(figures):
			index = 0
			delay = 3.5
		else:
			delay = 1.5
		
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(delay, next_rotate, args=[figures, index, lock])
		t.start()


def rotate_X_figure_order(figures, index, lock):
	if index >= len(figures):
		index = 0
		
	figure = figures[index]
	if isinstance(figure, MyFigure) is False:
		return
	
	lock.acquire()
	# 文字が未出現なら出現させる
	if figure.is_hide is True:
		figure.is_hide = False
	
	delay = 0.024
	next_rotate = rotate_X_figure_order
	# y軸の角度を増加
	figure.rotate_angle_x += 45
	
	#一周した場合
	if figure.rotate_angle_x >= 450:
		figure.rotate_angle_x = 90
		index += 1
		next_rotate = rotate_Z_figure_order
		
		if index >= len(figures):
			index = 0
			delay = 3.5
		else:
			delay = 1.5
		
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(delay, next_rotate, args=[figures, index, lock])
		t.start()


def rotate_Z_figure_order(figures, index, lock):
	if index >= len(figures):
		index = 0
		
	figure = figures[index]
	if isinstance(figure, MyFigure) is False:
		return
	
	lock.acquire()
	# 文字が未出現なら出現させる
	if figure.is_hide is True:
		figure.is_hide = False
	
	delay = 0.024
	next_rotate = rotate_Z_figure_order
	
	# y軸の角度を増加
	figure.rotate_angle_z += 45
	
	#一周した場合
	if figure.rotate_angle_z >= 450:
		figure.rotate_angle_z = 90
		index += 1
		next_rotate = rotate_Y_figure_order
		
		if index >= len(figures):
			index = 0
			delay = 3.5
		else:
			delay = 1.5
		
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(delay, next_rotate, args=[figures, index, lock])
		t.start()



# 壁を回転させる
# count が0になるまでmove_vectorのベクトルだけ光源を移動する
# move_vector : ベクトルを現す配列。[x,y,z]
def move_light_schedule(main_view, move_vector, count, lock):
	if isinstance(main_view, BaseView) is False:
		return
	if count <= 0:
		return
	
	lock.acquire()
	main_view.light_x += move_vector[0]
	main_view.light_y += move_vector[1]
	main_view.light_z += move_vector[2]
	lock.release()
	count -= 1
	
	if main_view.on_screen is True and count > 0:
		t = threading.Timer(0.05, move_light_schedule, args=[main_view, move_vector, count, lock])
		t.start()
	pass



# 再描画処理
def display_schedule(main_view, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
		
	#lock.acquire()
	main_view.set_needs_display()
	#lock.release()
	
	if main_view.on_screen is True:
		#t = threading.Timer(0.012, display_schedule, args=[main_view, lock])
		t = threading.Timer(0.024, display_schedule, args=[main_view, lock])
		t.start()


if __name__ == '__main__':
	# メイン画面の作成
	main_view = BaseView(frame=(0, 0, 375, 667))
	main_view.name = 'クオータニオン'
	main_view.background_color = 'lightblue'
	
	# カメラの位置
	main_view.camera.set_camera_position(0, 0, 250)
	# カメラの注視点
	main_view.camera.set_lookat_position(0, -100, -250)
	# ビュー座標の軸を生成する
	main_view.camera.set_camera_coodinate_vector()
	
	# 床
	floor = MyFloor(-420, 0, 150)
	main_view.set_floor(floor)
	
	# 壁
	main_view.wall.set_angle_y(0)
	# 光源の球
	main_view.set_light(MyFigure('./obj/ICO_Ball_20.obj', is_hide=True))
	#main_view.set_light(MyFigure('./obj/bou.obj', is_hide=True))
	main_view.light_x = 100
	
	# 棒。クオータニオン回転軸を表現する。
	pole = MyPole('./obj/pole.obj')
	pole.set_center(0, 0, 0)
	pole.set_face_color(0.0, 0.0, 0.0)
	main_view.add_figure(pole)
	
	# Blender 拡大率50倍が適切か。
	hiraganas = ['A', 'I', 'U', 'E', 'O']
	x = 100
	y = -150
	z = 0
	numbers = []
	
	count = 0
	for hiragana in hiraganas:
		filename = './obj/HIRA_' + hiragana + '_25.obj'
		#filename = './obj/saikoro.obj'
		# 字を生成
		figure = MyFigure(filename, is_hide=True)
		figure.set_center(x, y, z)
		if count % 3 == 0:
			figure.set_face_color(0.7, 1.0, 0.7)
		elif count % 3 == 1:
			figure.set_face_color(1.0, 0.7, 0.7)
			
		else:
			figure.set_face_color(0.7, 0.7, 1.0)
		count += 1
		figure.rotate_angle_y = 90
		main_view.add_figure(figure)
		numbers.append(figure)
		z -= 50
		
	main_view.present()
	
	lock = threading.Lock()
	
	# タイマー処理を設定する
	delay = 1.0
	
	# 数字を回す
	ts1 = threading.Timer(delay, rotate_Quat_figure_order, args=[numbers, 0, lock])
	ts1.start()
	
	# 視点移動　上昇
	delay += 0.5
	tv1 = threading.Timer(delay, change_view_y_schedule, args=[main_view, -4*80, -4, lock])
	tv1.start()
	
	# 光源を動かす
	delay += 2.0
	tml_1 = threading.Timer(delay, move_light_schedule, args=[main_view, [0, 10, 0], 10, lock])
	tml_1.start()
	
	# 光源を動かす
	delay += 2.0
	tml_2 = threading.Timer(delay, move_light_schedule, args=[main_view, [-10, 0, 0], 10, lock])
	tml_2.start()
	
	# 回転軸を動かす
	delay += 1.0
	ta_1 = threading.Timer(delay, modefy_Quat_Axis_Angle_order, args=[main_view, pole, 0, 0, -1, 45, lock])
	ta_1.start()
	
	# 光源を動かす
	delay += 2.0
	tml_3 = threading.Timer(delay, move_light_schedule, args=[main_view, [0, 0, 10], 10, lock])
	tml_3.start()
	
	# 視点移動　左右円周
	delay += 5.0
	tv2 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 90, 1, 20, lock])
	tv2.start()
	
	# 回転軸を動かす
	delay += 1.0
	ta_2 = threading.Timer(delay, modefy_Quat_Axis_Angle_order, args=[main_view, pole, 0, 0, 1, 45, lock])
	ta_2.start()
	
	# 視点移動　左右円周
	delay += 2.0
	tv3 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 110, -1, 40, lock])
	tv3.start()
	
	# 回転軸を動かす
	delay += 1.0
	ta_3 = threading.Timer(delay, modefy_Quat_Axis_Angle_order, args=[main_view, pole, 0, 0, 1, 45, lock])
	ta_3.start()
	
	# 回転軸を動かす
	delay += 5.0
	ta_4 = threading.Timer(delay, modefy_Quat_Axis_Angle_order, args=[main_view, pole, 0, 0, -1, 45, lock])
	ta_4.start()
	
	# 回転軸を動かす
	delay += 7.0
	ta_5 = threading.Timer(delay, modefy_Quat_Axis_Angle_order, args=[main_view, pole, -1, 0, 0, 25, lock])
	ta_5.start()
	
	# 回転軸を動かす
	delay += 7.0
	ta_6 = threading.Timer(delay, modefy_Quat_Axis_Angle_order, args=[main_view, pole, 1, 0, 0, 25*2, lock])
	ta_6.start()
	
	# 回転軸を動かす
	delay += 7.0
	ta_7 = threading.Timer(delay, modefy_Quat_Axis_Angle_order, args=[main_view, pole, -1, 0, 0, 25+90, lock])
	ta_7.start()
	
	# 再描画
	td = threading.Timer(0.01, display_schedule, args=[main_view, lock])
	td.start()
	
	
