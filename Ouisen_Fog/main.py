import ui
import threading
import copy
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from figure import *
from camera import *
from glyph import *
from character import *
from shogi import *


# 床。タイルにする。
class  MyFloor():
	color = [0.5, 0.5, 1.0]
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

	def level(self):
		return self.position[1]
	
	
	
# 背景と床を描画する
class BaseView(ui.View):
	
	screen_depth = 400	# 視点から投影面までの距離
	
	# 光源
	light_x = 0
	light_y = -300
	light_z = 1000
	
	# 床
	floor = None
	
	# 将棋の駒
	pieces = []
	
	# 文字
	characters = []
	
	# camera 
	camera = None
	
	# フォグ
	fog_min_distance = 500
	fog_max_distance = 1700
	fog_rgb = [0.9, 0.9, 0.9, 1.0]


	def set_camera(self, camera):
		if isinstance(camera, MyCamera) is True:
			self.camera = camera


	def set_piece(self, piece):
		if isinstance(piece, MyPiece) is True:
			self.pieces.append(piece)


	def add_character(self, character):
		self.characters.append(character)


	# 床を設定する
	def set_floor(self, floor):
		if isinstance(floor, MyFloor) is True:
			self.floor = floor


	# glyph座標からフォントのアウトライン描画を行う
	# point   : 座標 x, y, z
	# control : 制御点 x, y, z
	def draw_glyph(self, point, controls, path):
		p_x, p_y = self.projection(point[0], point[1], point[2])
		
		if point[3] == TYPE.LINE:
			path.line_to(p_x, p_y)
		elif point[3] == TYPE.CONTROL:
			controls.append(
								[p_x, p_y, point[2]])
		elif point[3] == TYPE.CURVE:
			if len(controls) == 2:
				path.add_curve(p_x, p_y, 
					controls[0][0], controls[0][1], 
					controls[1][0], controls[1][1])
			elif len(controls) == 1:
				path.add_quad_curve(p_x, p_y, 
					controls[0][0], controls[0][1])
			controls.clear()
	
	
	# 描画
	def draw(self):
		
		if self.camera is None:
			return
		
		# 光源
		light_x ,light_y ,light_z = self.camera.camera_rotation(self.light_x ,self.light_y ,self.light_z)
		
		# camera位置
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
				# 二辺のベクトルを算出する
				AB_vector = [b_x - a_x, b_y - a_y, b_z - a_z]
				AC_vector = [c_x - a_x, c_y - a_y, c_z - a_z]
				# 外積(法線ベクトル)を算出する
				cross_v3 = cross_product(AB_vector, AC_vector)
				# 正規化を行う
				normal_v3 = normalize(cross_v3)
				
				# 視点焦点までのベクトルを算出する
				scr_vector = [
					camera_x - (a_x + b_x + c_x) / 3,
					camera_y - (a_y + b_y + c_y) / 3,
					camera_z - (a_z + b_z + c_z) / 3]
				
				scr_normal = normalize(scr_vector)
				scr_inner = dot_product(normal_v3, scr_normal)
				
				# 光源までのベクトルを算出する
				light_vector = [
					light_x - (a_x + b_x + c_x) / 3,
					light_y - (a_y + b_y + c_y) / 3,
					light_z - (a_z + b_z + c_z) / 3]
				light_normal = normalize(light_vector)
				# 光源との角度を算出する
				light_inner = dot_product(normal_v3, light_normal)
				
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
				rgb = [0.0, 0.0, 0.0]
				if scr_inner < 0.0:
					rgb = ui_color([0.5, 0.5, 1.0], light_inner)
				
				# フォグを反映した色を算出する
				distance = sqrt(scr_vector[0]**2 + scr_vector[1]**2 + scr_vector[2]**2)
				rgb = color_with_fog(
				rgb, distance, 
				self.fog_rgb, 
				self.fog_max_distance, 
				self.fog_min_distance)
					
				ui.set_color((rgb[0], rgb[1], rgb[2], 1.0))
				path_f.fill()
		
		
		# 将棋の駒を描画する
		# ビュー座標の配列を算出する
		# [コマの五角形座標, 文字の座標]
		view_pieces = []
		for piece in self.pieces:
			if piece.is_visible is False:
				continue
			
			# 駒の五角形のローカル座標を取得
			local_points = piece.local_points()
			# ビュー座標変換
			view_points = self.camera.view_conversion(local_points)
			
			# コマの文字
			#local_glyphs = piece.local_glyphs(self.height)
			local_glyphs = piece.local_glyphs()
			view_glyphs = self.camera.glyphs_view_conversion(local_glyphs)
			
			view_pieces.append([view_points, view_glyphs])
			
		# ビュー座標でzソートを実行する
		sorted_view_pieces = sorted(view_pieces, key=self.sort_piece, reverse=True)
		
		for view_piece in sorted_view_pieces:
			
			points = view_piece[0]
			#print(points)
			# 法線ベクトルを算出する
			normal_v3 = normal_vector_with_points(
				points[0], points[1], points[2])
			
			# 光源までのベクトルを算出する
			rate = 1/3
			light_vector = [
				light_x - ((points[0][0] + points[2][0] + points[3][0]) * rate),
				light_y - ((points[0][1] + points[2][1] + points[3][1]) * rate),
				light_z - ((points[0][2] + points[2][2] + points[3][2]) * rate)]
			light_normal = normalize(light_vector)
			# 光源との角度を算出する
			light_inner = dot_product(normal_v3, light_normal)
			
			# 視点焦点までのベクトルを算出する
			scr_vector = [
				camera_x - ((points[0][0] + points[2][0] + points[3][0]) * rate),
				camera_y - ((points[0][1] + points[2][1] + points[3][1]) * rate),
				camera_z - ((points[0][2] + points[2][2] + points[3][2]) * rate)]
			scr_normal = normalize(scr_vector)
			scr_inner = dot_product(normal_v3, scr_normal)
			
			# 五角形座標のプロジェクション変換
			projection_points = self.projection_conversion(view_piece[0])
			# 文字glyph座標のプロジェクション変換
			projection_glyphs = self.glyphs_projection_conversion(view_piece[1])
			
			# 色を算出する
			rgb_color = []
			if scr_inner < 0:	# 表:黄色
				rgb_color = ui_color([1.0, 1.0, 0.1], light_inner)
			else:							# 裏:黒
				rgb_color = ui_color([0.0, 0.0, 0.0], light_inner)
			
			# フォグ色を反映する
			distance = sqrt(scr_vector[0]**2 + scr_vector[1]**2 + scr_vector[2]**2)
			rgb_color = color_with_fog(
				rgb_color, distance, 
				self.fog_rgb, 
				self.fog_max_distance, 
				self.fog_min_distance)
			
			# 描画を行う
			piece.draw(projection_points, projection_glyphs, rgb_color)
		
		# 文字を描画する
		# 文字の座標をビュー座標に変換し配列に格納する
		# 文字を描画する
		view_characters = []
		for character in self.characters:
			if character.is_visible is False:
				continue
			
			# [[x,y,z,type,flag],[],...],[]
			contours = character.glyph(self.height)
			
			# フォント本体のビュー座標変換
			for contour in contours:
				for i in range(0, len(contour)):
					contour[i][0], contour[i][1], contour[i][2] = self.camera.camera_rotation(
						contour[i][0], contour[i][1], contour[i][2])
			
			# 法線ベクトルの為の座標を取得
			point_for_vector = character.point_for_vector(self.height)
			
			# フォント本体を描画するための法線をビュー座標変換し算出する
			for i in range(0, len(point_for_vector)):
				point_for_vector[i][0], point_for_vector[i][1], point_for_vector[i][2] = self.camera.camera_rotation(point_for_vector[i][0], point_for_vector[i][1], point_for_vector[i][2])
			
			view_characters.append([contours, point_for_vector])
			
		# 文字をソート
		sorted_view_characters = sorted(view_characters, key=self.sort_character, reverse=True)
		
		for character in sorted_view_characters:
			contours = character[0]
			point_for_vector = character[1]
			font_normal_vector = normal_vector_with_points(
				point_for_vector[0], point_for_vector[1], point_for_vector[2])
			
			# フォントから視点焦点へのベクトルを算出する
			scr_vector = [
				camera_x - (point_for_vector[0][0] + point_for_vector[1][0] + point_for_vector[2][0]) / 3, 
				camera_y - (point_for_vector[0][1] + point_for_vector[1][1] + point_for_vector[2][1]) / 3, 
				camera_z - (point_for_vector[0][2] + point_for_vector[1][2] + point_for_vector[2][2]) / 3]
			# 視点焦点までのベクトルを正規化する
			scr_normal_vector = normalize(scr_vector)
			# 正規化したフォントの法線ベクトルと視点焦点ベクトルとの内積を取得する
			scr_inner = dot_product(font_normal_vector, scr_normal_vector)
			
			# フォントから光源までのベクトルを算出する
			light_vector = [
				light_x - (point_for_vector[0][0] + point_for_vector[1][0] + point_for_vector[2][0]) / 3, 
				light_y - (point_for_vector[0][1] + point_for_vector[1][1] + point_for_vector[2][1]) / 3, 
				light_z - (point_for_vector[0][2] + point_for_vector[1][2] + point_for_vector[2][2]) / 3]
			# フォントから光源までのベクトルを正規化する
			light_normal_vector = normalize(light_vector)
			# 正規化したフォントの法線ベクトルと光源ベクトルとの内積を取得する
			light_inner = dot_product(font_normal_vector, light_normal_vector)
			
			# フォントを描画する
			path = ui.Path()
			for points in contours:
				if len(points) < 3:
					continue
				
				# 最初のglyph座標
				p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])
				path.move_to(p_x, p_y)
			
				controls = []		# 制御点を格納する
				# 2番目以降のglyph座標
				for i in range(1, len(points)):
					self.draw_glyph(points[i], controls, path)
				# 最後のglyph座標
				self.draw_glyph(points[0], controls, path)
				
			# フォントの色設定と塗り潰し
			#if scr_inner < 0.0:
			rgb = ui_color(
					[0.0, 0.0, 0.0, 1.0], light_inner)
			distance = sqrt(scr_vector[0]**2 + scr_vector[1]**2 + scr_vector[2]**2)
			rgb = color_with_fog(
				rgb, distance, self.fog_rgb, self.fog_max_distance, 
				self.fog_min_distance)
			ui.set_color((rgb[0], rgb[1], rgb[2], 1.0))
			
			path.fill()
			
		pass
	
	
	# 文字のソート
	def sort_character(self, view_character):
		# 細かいエラー制御は省略
		# コマの五角形のビュー座標を取得する
		points = view_character[1]
		# 3つの頂点座標を取得して
		a_x, a_y, a_z = points[0][0], points[0][1], points[0][2]
		c_x, c_y, c_z = points[1][0], points[1][1], points[1][2]
		d_x, d_y, d_z = points[2][0], points[2][1], points[2][2]
		
		rate = 1 / 3
		# 視点焦点までのベクトルを算出する
		scr_vector = [
			0 - ((a_x + c_x + d_x) * rate),
			0 - ((a_y + c_y + d_y) * rate),
			self.screen_depth - ((a_z + c_z + d_z) * rate)]
		
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2

		return length
	

	# コマのソート
	def sort_piece(self, view_piece):
		# 細かいエラー制御は省略
		# コマの五角形のビュー座標を取得する
		points = view_piece[0]
		# 3つの頂点座標を取得して
		a_x, a_y, a_z = points[0][0], points[0][1], points[0][2]
		c_x, c_y, c_z = points[2][0], points[2][1], points[2][2]
		d_x, d_y, d_z = points[3][0], points[3][1], points[3][2]
		
		rate = 1 / 3
		# 視点焦点までのベクトルを算出する
		scr_vector = [
			0 - ((a_x + c_x + d_x) * rate),
			0 - ((a_y + c_y + d_y) * rate),
			self.screen_depth - ((a_z + c_z + d_z) * rate)]
		
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2

		return length
	
	
	# フォントグリフ座標の透視投影変換座標を返す
	def glyphs_projection_conversion(self, glyphs):
		r_glyphs = []
		
		for glyph in glyphs:
			r_glyph = []
			for contours in glyph:
				r_points = []
				for point in contours:
					x, y = self.projection(
						point[0], point[1], point[2])
						
					r_points.append([x, y, point[2], point[3], point[4]])
				r_glyph.append(r_points)
			r_glyphs.append(r_glyph)
		
		return r_glyphs
	
	
	# 透視投影変換座標を返す
	def projection_conversion(self, points):
		projection_points = []
		
		for point in points:
			x, y = self.projection(point[0], point[1], point[2])
			projection_points.append([x, y])
		
		return projection_points
	
	
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
	
	
	
	
	# 正規化した反射光のベクトルと視線のベクトルの
	# なす角度を算出してcos数値で返す
	# light_vector: 光源から図形のベクトル
	# triangle_normal: 図形の法線(正規化済)
	# scr_normal: 図形への視線(正規化済)
	def specular_inner(self, light_vector, triangle_normal, scr_normal):
		nega_light_vector = [
			-1 * light_vector[0],
			-1 * light_vector[1],
			-1 * light_vector[2]]
		# 入光ベクトルと法線の内積で光源までの距離cosを算出
		light_cos = dot_product(nega_light_vector, triangle_normal)
		# 反射光ベクトル R = F + 2(-F・N)N
		r_light_vector = [
			light_vector[0] + (2 * light_cos * triangle_normal[0]),
			light_vector[1] + (2 * light_cos * triangle_normal[1]),
			light_vector[2] + (2 * light_cos * triangle_normal[2])]
		
		# 視線と反射光のなす角度を求める
		# 反射光のベクトルを正規化する
		r_light_normal = normalize(r_light_vector)
		# 反射受光角度を算出する
		specular_inner = dot_product(scr_normal, r_light_normal)
		
		return specular_inner



# カメラの位置上昇下降
# goal_y: カメラ位置目的y座標値
# add_y: 上昇下降移動量
def change_view_y_schedule(main_view, goal_y, add_y, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(main_view.camera, MyCamera) is False:
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
def change_view_round_schedule(main_view, angle, goal_angle, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
	
	#round = 450
	round = 1050
	add_angle = 0.5
	
	lock.acquire()
	
	angle += add_angle
	if abs(goal_angle - angle) < add_angle:
		angle = goal_angle
	
	main_view.camera.camera_x = round * cos(radians(angle))
	main_view.camera.camera_z = round * sin(radians(angle)) + (-250)
	main_view.camera.set_camera_coodinate_vector()
	
	lock.release()
	
	if main_view.on_screen is True and isclose(angle, goal_angle) is False:
		t = threading.Timer(0.02, change_view_round_schedule, args=[main_view, angle, goal_angle, lock])
		t.start()
		

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


# 文字 をX軸に回転させる
# 一周するまで本関数が繰り返し呼ばれる
# 回転中に文字の「文字列を表示するフラグ」を設定する
def rotate_x_character_schedule(main_view, character):
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(character, Character) is False:
		return
	
	if character.is_visible is False:
		character.set_visible(True)
	
	character.rotate_angle_x += 20
	if character.rotate_angle_x >= 360:
		character.set_angle_x(0)
	
	if main_view.on_screen is True and character.rotate_angle_x > 0:
		t = threading.Timer(0.02, rotate_x_character_schedule, args=[main_view, character])
		t.start()


# コマ をY軸に回転させる
# 一周するまで本関数が繰り返し呼ばれる
# 回転中に文字の「文字列を表示するフラグ」を設定する
def rotate_y_piece_schedule(main_view, piece):
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(piece, MyPiece) is False:
		return
	
	piece.rotate_angle_y += 10
	if piece.rotate_angle_y >= 360:
		piece.set_angle_y(0)
	
	if piece.is_visible is False:
		piece.set_visible(True)
	
	if main_view.on_screen is True and piece.rotate_angle_y > 0:
		t = threading.Timer(0.02, rotate_y_piece_schedule, args=[main_view, piece])
		t.start()



# 「表示するフラグ」を設定する
def set_visible_schedule(main_view, object, is_visible = True):
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(object, MyPiece) is False and isinstance(object, Character) is False:
		return
	
	object.set_visible(is_visible)
	
	


# 3Dフォントを生成する
def character_with_info(glyph, x, y, z, glyph_scale, angle_y=270):
	# ToDo 見直し
	rotate_center_x = -800
	rotate_center_y = -800
	scale = 0.1
	
	if isclose(glyph_scale, 1.000) is False:
		for contour in glyph:
			for point in contour:
				point[0] *= glyph_scale
				point[1] *= glyph_scale
				
				
	character = Character(glyph)
	character.set_center(rotate_center_x, rotate_center_y, 0)
	
	character.set_angle_y(angle_y) # 
	character.translate(x, y, z)
	character.set_scale(scale)
	
	return character



if __name__ == '__main__':
	# メイン画面の作成
	main_view = BaseView(frame=(0, 0, 375, 667))
	main_view.name = '王位戦(フォグ付き)'
	main_view.background_color = (0.9,0.9,0.9,1.0)
	# 
	camera = MyCamera()
	# カメラの位置 / 注視点
	camera.set_camera_position(0, 0, 800)
	camera.set_lookat_position(0, 0, -250)
	# ビュー座標の軸を生成する
	camera.set_camera_coodinate_vector()
	main_view.set_camera(camera)
	
	# 床
	floor = MyFloor(-420, 300, 150)
	main_view.set_floor(floor)
	
	# 将棋の駒
	def_y = 250
	def_z = 100
	piece_1 = MyPiece()
	piece_1.add_glyph(glyph_王_JP())
	piece_1.add_glyph(glyph_位_JP())
	piece_1.translate(0, def_y, def_z)
	main_view.set_piece(piece_1)
	
	def_z -= 150
	piece_2 = MyPiece()
	piece_2.add_glyph(glyph_棋_JP())
	piece_2.add_glyph(glyph_聖_JP())
	piece_2.translate(200, def_y, def_z)
	main_view.set_piece(piece_2)
	
	piece_3 = MyPiece()
	piece_3.add_glyph(glyph_棋_JP())
	piece_3.add_glyph(glyph_王_JP())
	piece_3.translate(-200, def_y, def_z)
	main_view.set_piece(piece_3)
	
	def_z -= 150
	piece_4 = MyPiece()
	piece_4.add_glyph(glyph_名_JP())
	piece_4.add_glyph(glyph_人_JP())
	piece_4.translate(-300, def_y, def_z)
	main_view.set_piece(piece_4)
	
	piece_5 = MyPiece()
	piece_5.add_glyph(glyph_竜_JP())
	piece_5.add_glyph(glyph_王_JP())
	piece_5.translate(300, def_y, def_z)
	main_view.set_piece(piece_5)
	
	def_z -= 150
	piece_6 = MyPiece()
	piece_6.add_glyph(glyph_叡_JP())
	piece_6.add_glyph(glyph_王_JP())
	piece_6.translate(200, def_y, def_z)
	main_view.set_piece(piece_6)
	
	piece_7 = MyPiece()
	piece_7.add_glyph(glyph_王_JP())
	piece_7.add_glyph(glyph_将_JP())
	piece_7.translate(-200, def_y, def_z)
	main_view.set_piece(piece_7)
	
	def_z -= 150
	piece_8 = MyPiece()
	piece_8.add_glyph(glyph_王_JP())
	piece_8.add_glyph(glyph_座_JP())
	piece_8.translate(0, def_y, def_z)
	main_view.set_piece(piece_8)
	
	
	# 文字
	def_x = 1300
	def_z = 1000
	def_y = 7000
	
	start_scale = 1.0
	# 藤井 藤
	char_Fujii_Fuji = character_with_info(glyph_藤_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Fujii_Fuji)
	# 藤井 井
	def_z -= 2000
	char_Fujii_I = character_with_info(glyph_井_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Fujii_I)
	# 聡太　聡
	def_z -= 2000
	char_Souta_Sou = character_with_info(glyph_聡_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Souta_Sou)
	# 聡太　太
	def_z -= 2000
	char_Souta_Ta = character_with_info(glyph_太_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Souta_Ta)
	
	def_z = 2000
	def_y = 9000
	start_scale = 0.5
	# 挑戦者　挑
	char_Tyou = character_with_info(glyph_挑_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Tyou)
	# 挑戦者　戦
	def_z -= 1000
	char_Sen = character_with_info(glyph_戦_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Sen)
	# 挑戦者　者
	def_z -= 1000
	char_Sya = character_with_info(glyph_者_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Sya)
	
	# 棋聖　棋
	def_y -= 2000
	def_z -= 6000
	char_Kisei_Ki = character_with_info(glyph_棋_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Kisei_Ki)
	# 棋聖　聖
	def_z -= 1000
	char_Kisei_Sei = character_with_info(glyph_聖_JP(), def_x, def_y, def_z, start_scale)
	main_view.add_character(char_Kisei_Sei)
	
	
	def_x = -3200
	def_z = 1500
	def_y = 7000
	start_scale = 1.0
	# 木村　木
	char_kimura_ki = character_with_info(glyph_木_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_kimura_ki)
	# 木村　村
	def_z -= 2000
	char_kimura_mura = character_with_info(glyph_村_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_kimura_mura)
	# 一基　一
	def_z -= 2000
	char_kazuki_kazu = character_with_info(glyph_一_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_kazuki_kazu)
	# 一基　基
	def_z -= 2000
	char_kazuki_ki = character_with_info(glyph_基_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_kazuki_ki)
	
	def_z = 1000
	def_y = 9000
	start_scale = 0.4
	# タ
	char_Holder_Ta = character_with_info(glyph_タ_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_Ta)
	# イ
	def_z -= 700
	char_Holder_I = character_with_info(glyph_イ_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_I)
	# ト
	def_z -= 700
	char_Holder_To = character_with_info(glyph_ト_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_To)
	# ル
	def_z -= 700
	char_Holder_Ru_1 = character_with_info(glyph_ル_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_Ru_1)
	# ホ
	def_z -= 700
	char_Holder_Ho = character_with_info(glyph_ホ_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_Ho)
	# ル
	def_z -= 700
	char_Holder_Ru_2 = character_with_info(glyph_ル_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_Ru_2)
	# ダ
	def_z -= 700
	char_Holder_Da = character_with_info(glyph_ダ_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_Da)
	# -
	def_z -= 700
	char_Holder_Long = character_with_info(glyph_ー_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Holder_Long)
	
	
	# 王位　王
	def_y -= 2000
	def_z -= 3000
	start_scale = 0.5
	char_Oui_Ou = character_with_info(glyph_王_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Oui_Ou)
	# 王位　位
	def_z -= 1000
	char_Oui_I = character_with_info(glyph_位_JP(), def_x, def_y, def_z, start_scale, 90)
	main_view.add_character(char_Oui_I)
	
	# 王位戦　王
	def_x = -1000
	def_y = 8000
	def_z = 1000
	start_scale = 1.0
	char_Ouisen_Ou = character_with_info(glyph_王_JP(), def_x, def_y, def_z, start_scale, 0)
	main_view.add_character(char_Ouisen_Ou)
	# 王位戦　位
	def_y -= 2000
	char_Ouisen_I = character_with_info(glyph_位_JP(), def_x, def_y, def_z, start_scale, 0)
	main_view.add_character(char_Ouisen_I)
	# 王位戦　戦
	def_y -= 2000
	char_Ouisen_Sen = character_with_info(glyph_戦_JP(), def_x, def_y, def_z, start_scale, 0)
	main_view.add_character(char_Ouisen_Sen)
	
	main_view.present()
	
	# タイマー処理を設定する
	lock = threading.Lock()
	
	# コマの配列
	pieces = [piece_1, piece_2, piece_3, 
		piece_4, piece_5, piece_6, piece_7, piece_8]
	
	# コマの出現と回転
	delay = 1.5
	for index in range(len(pieces) - 1, -1, -1):
		t = threading.Timer(delay, rotate_y_piece_schedule, args=[main_view, pieces[index]])
		t.start()
		delay += 0.5
	
	
	# 文字の配列　保持者名前
	delay += 1.5
	holder_name_chars = [
		char_kimura_ki, char_kimura_mura, char_kazuki_kazu, char_kazuki_ki]
	# 文字の出現
	for character in holder_name_chars:
		t = threading.Timer(delay, rotate_x_character_schedule, args=[main_view, character])
		t.start()
		delay += 1
	
	
	# 保持者
	delay += 1
	holder_chars = [
		char_Holder_Ta, char_Holder_I, char_Holder_To, char_Holder_Ru_1, char_Holder_Ho, char_Holder_Ru_2, char_Holder_Da, char_Holder_Long, char_Oui_Ou, char_Oui_I]
	# 文字の出現
	for character in holder_chars:
		t = threading.Timer(delay, set_visible_schedule, args=[main_view, character])
		t.start()
		delay += 0.05
		
	
	# 文字の配列　挑戦者名前
	delay += 1
	challenger_name_chars = [
		char_Fujii_Fuji, char_Fujii_I, char_Souta_Sou, char_Souta_Ta]
	# 挑戦者名前
	for character in challenger_name_chars:
		t = threading.Timer(delay, rotate_x_character_schedule, args=[main_view, character])
		t.start()
		delay += 1
	
	# 保持者
	delay += 1
	challenger_chars = [
		char_Tyou, char_Sen, char_Sya, char_Kisei_Ki, char_Kisei_Sei]
	# 文字の出現
	for character in challenger_chars:
		t = threading.Timer(delay, set_visible_schedule, args=[main_view, character])
		t.start()
		delay += 0.05
	
	
	# 視点移動　周回
	delay += 0.5
	tv2 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 90, 90+360, lock])
	tv2.start()
	
	# コマの回転
	for i in range(5):
		delay += 5
		for index in range(0, len(pieces)):
			t = threading.Timer(delay, rotate_y_piece_schedule, args=[main_view, pieces[index]])
			t.start()
			delay += 0.5
	
	# 視点移動　上昇
	tv1 = threading.Timer(40.0, change_view_y_schedule, args=[main_view, -200, -4, lock])
	tv1.start()
	
	# 王位戦
	delay += 1
	ouisen_chars = [
		char_Ouisen_Ou, char_Ouisen_I, char_Ouisen_Sen]
	# 文字の出現
	for character in ouisen_chars:
		t = threading.Timer(delay, set_visible_schedule, args=[main_view, character])
		t.start()
		delay += 0.5
	
	
	td = threading.Timer(0.01, display_schedule, args=[main_view, lock])
	td.start()
	
	
