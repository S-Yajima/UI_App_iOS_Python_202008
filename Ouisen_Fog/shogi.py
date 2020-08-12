import ui
from figure import *
from glyph import *


# (将棋の)駒
# 五角形のローカル座標を持たせる
# 文字(複数)を持たせる
# 
class MyPiece(MyFigure):
	face_color = [1.0, 1.0, 0.1]
	back_color = [0.0, 0.0, 0.0]
	# 
	is_visible = False
	
	
	
	def __init__(self):
		super().__init__()
		# 五角形のローカル座標を設定する
		self.A_x = 0
		self.A_y = -220
		self.A_z = 0
		self.B_x = -60
		self.B_y = -190
		self.B_z = 0
		self.C_x = -75
		self.C_y = 0
		self.C_z = 0
		self.D_x = 75
		self.D_y = 0
		self.D_z = 0
		self.E_x = 60
		self.E_y = -190
		self.E_z = 0
		# 文字を格納する配列を初期化する
		self.glyphs = []
	
	
	def set_visible(self, flag):
		self.is_visible = flag
		
		
	def add_glyph(self, glyph):
		rate = 0.05
		x_gap = 50
		y_gap = 110
		
		# 何文字保持してるかチェック
		# print(len(self.glyphs))
		if len(self.glyphs) > 0:
			y_gap = 20
		
		contours = []
		for contour in glyph:
			points = []
			for point in contour:
				work_list = []
				work_list.append(point[0] * rate - x_gap)	# x座標
				work_list.append((point[1] * rate + y_gap) * -1)	# y座標 マイナスにして上下の違いを吸収する
				work_list.append(0)
				work_list.append(point[2])	# line/curve/control
				work_list.append(True)			# 表示/非表示
				
				#print(work_list)
				
				points.append(work_list)
				
			contours.append(points)
		
		self.glyphs.append(contours)
		pass
		


	# 
	def local_points(self):
		a_x, a_y, a_z = self.queue(self.A_x, self.A_y, self.A_z)
		b_x, b_y, b_z = self.queue(self.B_x, self.B_y, self.B_z)
		c_x, c_y, c_z = self.queue(self.C_x, self.C_y, self.C_z)
		d_x, d_y, d_z = self.queue(self.D_x, self.D_y, self.D_z)
		e_x, e_y, e_z = self.queue(self.E_x, self.E_y, self.E_z)
		
		return [
			[a_x, a_y, a_z], [b_x, b_y, b_z], 
			[c_x, c_y, c_z], [d_x, d_y, d_z], 
			[e_x, e_y, e_z]]
		
	
	# 
	def local_glyphs(self, height=0):
		r_glyphs = []
		
		for glyph in self.glyphs:
			r_glyph = []
			for contours in glyph:
				r_points = []
				for point in contours:
					
					x, y, z = self.queue(
						point[0], point[1], point[2])
					
					# glyphデータのy座標とViewのy座標は
					# 上下逆転しているので吸収する
					#y = height - y
				
					r_points.append([x, y, z, point[3], point[4]])
					
					#print(point)
					
				r_glyph.append(r_points)
			r_glyphs.append(r_glyph)
		
		return r_glyphs



	# color : 配列　[r, g, b, (a)]
	# 描画対象物がdraw()メソッドを
	# zソートなどを解決可能か検討する
	def draw(self, points, glyphs, color):
		
		path = ui.Path()
		path.move_to(points[0][0], points[0][1])
		path.line_to(points[1][0], points[1][1])
		path.line_to(points[2][0], points[2][1])
		path.line_to(points[3][0], points[3][1])
		path.line_to(points[4][0], points[4][1])
		path.line_to(points[0][0], points[0][1])
		# 描画色を設定する
		
		ui.set_color((color[0], color[1], color[2], 1.0))
		path.fill()
		
		# 文字を描画
		path_g = ui.Path()
			
		for contours in glyphs:
			for g_points in contours:
				if len(g_points) < 3:
					continue
				
				# 最初のglyph座標
				#p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])
				#print(g_points[0], g_points[0][1])
				p_x, p_y = (g_points[0][0], g_points[0][1])
				path_g.move_to(p_x, p_y)
			
				controls = []		# 制御点を格納する
				# 2番目以降のglyph座標
				for i in range(1, len(g_points)):
					self.draw_glyph(g_points[i], controls, path_g)
				# 最後のglyph座標
				self.draw_glyph(g_points[0], controls, path_g)
				
			# フォントの色設定と塗り潰し
			#if scr_inner < 0.0:
		ui.set_color('black')
		path_g.fill()
		
		pass



	# glyph座標からフォントのアウトライン描画を行う
	# point   : 座標 x, y, z
	# control : 制御点 x, y, z
	def draw_glyph(self, point, controls, path):
		#p_x, p_y = self.projection(point[0], point[1], point[2])
		p_x, p_y = (point[0], point[1])
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



