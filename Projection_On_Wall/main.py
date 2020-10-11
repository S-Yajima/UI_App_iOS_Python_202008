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


# 背景と床を描画する
class BaseView(ui.View):
	
	screen_depth = 400	# 視点から投影面までの距離
	
	# 床
	froor = None
	# 壁
	wall = Wall()
	
	# スケーリング倍率
	magnification = -1
	
	# 物体の配列
	figures = []
	
	# 視点移動用のカメラ
	camera = MyCamera()
	
	# 光源(仮)
	light_x = 200
	light_y = -300
	light_z = 500
	
	
	# 物体を追加する
	def add_figure(self, figure):
		if isinstance(figure, MyFigure) is True:
			self.figures.append(figure)
	
	# 床を設定する
	def set_floor(self, floor):
		if isinstance(floor, MyFloor) is True:
			self.floor = floor
	
	
	
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
	# ビュー変換後の座標で、視点からの距離の値を比較し三角ポリゴンのソートを行う
	def sort_triangle(self, corners):
		camera_x, camera_y, camera_z = self.camera.camera_rotation(
			self.camera.camera_x, self.camera.camera_y, self.camera.camera_z)
		
		a_x, a_y, a_z = (corners[0][0], corners[0][1], corners[0][2])
		b_x, b_y, b_z = (corners[1][0], corners[1][1], corners[1][2])
		c_x, c_y, c_z = (corners[2][0], corners[2][1], corners[2][2])
		
		# 視点焦点までのベクトルを算出する
		scr_vector = [
			camera_x - (a_x + b_x + c_x) / 3,
			camera_y - (a_y + b_y + c_y) / 3,
			camera_z - (a_z + b_z + c_z) / 3]
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2
			
		return length
	
	
	# 図形(物体)のソート
	def sort_figure(self, figure):
		camera_x, camera_y, camera_z = self.camera.camera_rotation(
			self.camera.camera_x, self.camera.camera_y, self.camera.camera_z)
			
		c_x, c_y, c_z = self.camera.camera_rotation(
			figure.center.x, figure.center.y, figure.center.z)
		
		# 視点焦点までのベクトルを算出する
		scr_vector = [
			camera_x - c_x,
			camera_y - c_y,
			camera_z - c_z]
		
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2

		return length
	

	
	# 光源を返す
	def light_point(self):
		#x, y, z = (0, 0, 0)
		x, y, z = (
			self.light_x, self.light_y, self.light_z, 
		)
		return (x, y, z)



	# 描画
	def draw(self):
		# 光源
		light_x ,light_y ,light_z = self.light_point()
		light_x ,light_y ,light_z = self.camera.camera_rotation(light_x ,light_y ,light_z)
		# カメラ位置のビュー座標
		camera_x ,camera_y ,camera_z = self.camera.camera_rotation(
			self.camera.camera_x, 
			self.camera.camera_y, 
			self.camera.camera_z)
		
		
		# 床
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
				# 折り紙の部品の二辺のベクトルを算出する
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
		
		self.draw_wall()
		
		# 図形の座標をビュー座標に変換し配列に格納する
		# 図形をソートする
		sorted_figures = sorted(self.figures, key=self.sort_figure, reverse=True)
		
		for figure in sorted_figures:
			# 描画フラグを判別
			if figure.is_hide is True:
				continue
			
			triangles = []
			
			# ビュー座標を配列に格納
			local_points = figure.local_points()
			
			for triangle in local_points:
				vertexes = []
				prpjection_vertexes = []
				for vertex in triangle:
					# 図形本体の座標をビュー座標に変換する
					x, y, z = self.camera.camera_rotation(
						vertex[0], vertex[1], vertex[2])
					vertexes.append([x, y, z])
					# 壁に図形を投影する
					p_x, p_y, p_z = self.wall_projection(vertex[0], vertex[1], vertex[2], figure.magnification)
					p_x, p_y, p_z = self.camera.camera_rotation(p_x, p_y, p_z)
					prpjection_vertexes.append([p_x, p_y, p_z])
				triangles.append(vertexes)
				triangles.append(prpjection_vertexes)
			
			# 取得したビュー座標を視点からの距離でソートする
			sorted_triangles = sorted(triangles, key=self.sort_triangle, reverse=True)

			# ソート済の三角形ビュー座標の配列で描画を行う
			for corners in sorted_triangles:
				a_x, a_y, a_z = (corners[0][0], corners[0][1], corners[0][2])
				b_x, b_y, b_z = (corners[1][0], corners[1][1], corners[1][2])
				c_x, c_y, c_z = (corners[2][0], corners[2][1], corners[2][2])
				
				p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
				p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
				p_c_x, p_c_y = self.projection(c_x, c_y, c_z)
				
				path_t = ui.Path()
				path_t.move_to(p_a_x, p_a_y)
				path_t.line_to(p_b_x, p_b_y)
				path_t.line_to(p_c_x, p_c_y)
				path_t.line_to(p_a_x, p_a_y)
				
				# 法線ベクトルから表裏と陰影を算出する
				# 折り紙の部品の二辺のベクトルを算出する
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
					r, g, b, a = figure.face_color_value()
					color = ui_color([r, g, b], light_inner, specular=20, specular_inner=specular_inner_cos)
					
					ui.set_color((color[0], color[1], color[2], 1.0))
					
					path_t.fill()
				
		

	# ___ 
	
	# 座標x,y,zに対しスケーリング、投影処理を行う
	# x,y,z 壁にスケーリング,投影する対象の座標
	# magnification スケーリング行列処理の倍率
	# =0 正投影　<0 リフレクション　>0 スケーリング
	def wall_projection(self, x, y, z, magnification=0):
		p_x, p_y, p_z = (0, 0, 0)
		# 壁の法線
		wall_normal = self.wall.normal
		# スケーリング行列処理
		zero_matrix = [[0, 0, 0, 0], 
									[0, 0, 0, 0], 
									[0, 0, 0, 0]]
		projection_matrix = make_Scale_With_Vector_Matrix(zero_matrix, wall_normal, magnification)
		p_x, p_y, p_z = transform3D([x, y, z], projection_matrix)
		
		return (p_x, p_y, p_z)



	# 壁を描画する
	def draw_wall(self):
		# 壁
		wall_points = self.wall.points()
		wall_vertexes = []
		for wall_point in wall_points:
			x, y, z = self.camera.camera_rotation(
				wall_point[0], wall_point[1], wall_point[2])
			wall_vertexes.append([x, y, z])
		
		p_a_x, p_a_y = self.projection(wall_vertexes[0][0], wall_vertexes[0][1], wall_vertexes[0][2])
		p_b_x, p_b_y = self.projection(wall_vertexes[1][0], wall_vertexes[1][1], wall_vertexes[1][2])
		p_c_x, p_c_y = self.projection(wall_vertexes[2][0], wall_vertexes[2][1], wall_vertexes[2][2])
		p_d_x, p_d_y = self.projection(wall_vertexes[3][0], wall_vertexes[3][1], wall_vertexes[3][2])
		
		path_w = ui.Path()
		path_w.move_to(p_a_x, p_a_y)
		path_w.line_to(p_b_x, p_b_y)
		path_w.line_to(p_c_x, p_c_y)
		path_w.line_to(p_d_x, p_d_y)
		path_w.line_to(p_a_x, p_a_y)
		ui.set_color((1.0, 1.0, 1.0, 0.5))
		path_w.fill()
		
	

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

'''
# カメラが外周を円旋回する
# angle : 開始カメラアングル
# goal_angle : 移動終了時のカメラアングル
def change_view_round_schedule(main_view, angle, goal_angle, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
	
	round = 550
	add_angle = -3.0
	
	angle += add_angle
	if abs(goal_angle - angle) < add_angle:
		angle = goal_angle
	
	lock.acquire()
	
	main_view.camera.camera_x = round * cos(radians(angle))
	main_view.camera.camera_z = round * sin(radians(angle)) + (-250)
	main_view.camera.set_camera_coodinate_vector()
	
	lock.release()
	
	if main_view.on_screen is True and isclose(angle, goal_angle) is False:
		t = threading.Timer(0.02, change_view_round_schedule, args=[main_view, angle, goal_angle, lock])
		t.start()
'''


# カメラが外周を円旋回する
# angle : 開始カメラアングル
# add_angle : 移動毎のカメラアングル移動角度
# count : 残りの処理回数
def change_view_round_schedule(main_view, angle, add_angle, count, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
	if count <= 0:
		return
	
	round = 700
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


# 数字を順序に一回転させる
# figures: 数字の配列
# infex : 処理対象の配列figuresのインデックス番号
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
	# y軸の角度を増加
	figure.rotate_angle_y += 45
	
	delay = 0.012
	
	#一周した場合
	if figure.rotate_angle_y >= 450:
		figure.rotate_angle_y = 90
		index += 1
		if index >= len(figures):
			index = 0
			delay = 3.5
		else:
			delay = 1.5
		
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(delay, rotate_Z_figure_order, args=[figures, index, lock])
		t.start()


# 壁を回転させる
# count が0になるまでangleの角度だけ回転させる
def rotate_wall_y_schedule(main_view, angle, count, lock):
	if isinstance(main_view, BaseView) is False:
		return
	if count <= 0 or angle == 0:
		return
	main_view.wall.set_angle_y(main_view.wall.rotate_angle_y + angle)
	count -= 1
	
	if main_view.on_screen is True and count > 0:
		t = threading.Timer(0.1, rotate_wall_y_schedule, args=[main_view, angle, count, lock])
		t.start()
	pass


# 文字のスケーリング倍率を順番に変更させる
# index : 倍率変更対象の図形インデックス
# up_flg : 倍率の値を増加または減少させるフラグ
#	倍率が一定の値に達したらフラグの値を入れ替える
def change_magnification_schedule(main_view, index, up_flg, lock):
	if isinstance(main_view, BaseView) is False:
		return
	if index < 0 or len(main_view.figures) <= index:
		return
	
	delay = 0.024
	add_value = 0.2
	figure = main_view.figures[index]
	
	if up_flg is False:
		add_value *= -1
		
	figure.magnification += add_value
	
	if figure.magnification >= 0:
		up_flg = False
		figure.magnification = 0
		index += 1
		if len(main_view.figures) <= index:
			index = 0
			delay = 3.0
	elif figure.magnification <= -1:
		up_flg = True
		figure.magnification = -1.0
	
	
	if main_view.on_screen is True:
		t = threading.Timer(delay, change_magnification_schedule, args=[main_view, index, up_flg, lock])
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
		t = threading.Timer(0.012, display_schedule, args=[main_view, lock])
		#t = threading.Timer(0.024, display_schedule, args=[main_view, lock])
		t.start()


if __name__ == '__main__':
	# メイン画面の作成
	main_view = BaseView(frame=(0, 0, 375, 667))
	main_view.name = '壁に図形を投影'
	main_view.background_color = 'lightblue'
	
	# カメラの位置
	main_view.camera.set_camera_position(0, 0, 450)
	# カメラの注視点
	main_view.camera.set_lookat_position(0, -100, -250)
	# ビュー座標の軸を生成する
	main_view.camera.set_camera_coodinate_vector()
	
	# 床
	floor = MyFloor(-420, 200, 150)
	main_view.set_floor(floor)
	
	# 壁
	main_view.wall.set_angle_y(0)
	
	# Blender 拡大率50倍が適切か。
	hiraganas = ['A', 'I', 'U', 'E', 'O']
	x = 100
	y = 0
	z = 200
	numbers = []
	
	count = 0
	for hiragana in hiraganas:
		filename = './obj/HIRA_' + hiragana + '_25.obj'
	
		# 字を生成
		figure = MyFigure(filename, is_hide=True)
		figure.set_center(x, y, z)
		if count % 3 == 0:
			figure.set_face_color(0.7, 1.0, 0.7)
		elif count % 3 == 1:
			figure.set_face_color(0.7, 0.7, 1.0)
		else:
			figure.set_face_color(1.0, 0.7, 0.7)
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
	ts1 = threading.Timer(delay, rotate_Z_figure_order, args=[numbers, 0, lock])
	ts1.start()
	
	
	# 壁を動かす
	delay += 5.0
	t = threading.Timer(delay, rotate_wall_y_schedule, args=[main_view, 2.0, 10, lock])
	t.start()
	
	# 壁を動かす
	delay += 10.0
	t = threading.Timer(delay, rotate_wall_y_schedule, args=[main_view, -2.0, 20, lock])
	t.start()
	
	# 視点移動　左右円周
	delay += 5.0
	tv1 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 90, 1, 20, lock])
	tv1.start()
	
	# スケーリングの倍率を順次変える
	delay += 5.0
	t = threading.Timer(delay, change_magnification_schedule, args=[main_view, 0, False, lock])
	t.start()
	
	# 視点移動　左右円周
	delay += 1.0
	tv1 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 110, -1, 20, lock])
	tv1.start()
	
	# 壁を動かす
	delay += 5.0
	t = threading.Timer(delay, rotate_wall_y_schedule, args=[main_view, 2.0, 20, lock])
	t.start()
	
	# 壁を動かす
	delay += 10.0
	t = threading.Timer(delay, rotate_wall_y_schedule, args=[main_view, -2.0, 20, lock])
	t.start()

	# 壁を動かす
	delay += 10.0
	t = threading.Timer(delay, rotate_wall_y_schedule, args=[main_view, 2.0, 20, lock])
	t.start()
	
	# 壁を動かす
	delay += 10.0
	t = threading.Timer(delay, rotate_wall_y_schedule, args=[main_view, -2.0, 20, lock])
	t.start()
	
	# 視点移動　上昇
	delay += 0.5
	tv4 = threading.Timer(delay, change_view_y_schedule, args=[main_view, -200, -4, lock])
	tv4.start()
	
	# 再描画
	td = threading.Timer(0.01, display_schedule, args=[main_view, lock])
	td.start()
	
	
