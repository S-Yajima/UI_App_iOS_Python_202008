from Matrix import *

# 床。タイルにする。
class  MyCamera():
	
	#camera vector
	camera_x = 0		# カメラの位置座標
	camera_y = 0
	camera_z = 0
	lookat_x = 0		# カメラの注視点
	lookat_y = 0
	lookat_z = 0
	CXV = []				# カメラ座標のXYZ軸ベクトル
	CYV = []
	CZV = []
	CPX = 0					# カメラ座標とカメラX軸との内積
	CPY = 0
	CPZ = 0
	# camera vector
	
	
	# カメラの位置座標を設定する
	def set_camera_position(self, x, y, z):
		self.camera_x = x
		self.camera_y = y
		self.camera_z = z


	# カメラの注視点を設定する
	def set_lookat_position(self, x, y, z):
		self.lookat_x = x
		self.lookat_y = y
		self.lookat_z = z
	
	
	# ビュー座標XYZ軸を作成する
	def set_camera_coodinate_vector(self):
		# カメラのZ軸ベクトルを算出する
		# カメラの位置座標と、注視点の座標を使用する
		CV = [
			self.camera_x - self.lookat_x, self.camera_y - self.lookat_y, 
			self.camera_z - self.lookat_z]
		CZV_normal = normalize(CV)
		
		# カメラのX軸ベクトルを算出する
		# 注意)iOS のビューはY軸上に行くほど値減少
		# 注意)外積対象のベクトルの順序でX軸の方向が事なる
		CXV_cross = cross_product(CZV_normal, [0, -1, 0])
		CXV_normal = normalize(CXV_cross)
		
		# カメラのY軸ベクトルを算出する
		# 注意)外積対象のベクトルの順序でY軸の方向が異なる
		# 注意)正規化されたベクトル同士の外積なので改めて正規化は必要なし
		CYV_normal = cross_product(CZV_normal, CXV_normal)
		
		# カメラ移動計算用の内積を算出する
		camera_position = [self.camera_x, self.camera_y, self.camera_z]
		self.CPX = dot_product(camera_position, CXV_normal)
		self.CPY = dot_product(camera_position, CYV_normal)
		self.CPZ = dot_product(camera_position, CZV_normal)
		
		# 算出したビュー座標XYZ軸ベクトルをメンバ変数に格納
		self.CXV = CXV_normal
		self.CYV = CYV_normal
		self.CZV = CZV_normal
		
	
	# ビュー座標回転
	def camera_rotation(self, x, y, z):
		CXV = self.CXV	# ビュー座標のxyz軸ベクトル
		CYV = self.CYV
		CZV = self.CZV
		
		if len(CXV) != 3 or len(CYV) != 3 or len(CZV) != 3:
			return (x, y, z)
			
		CPX = self.CPX	# カメラ移動計算用の内積
		CPY = self.CPY
		CPZ = self.CPZ
		
		# カメラ座標への回転
		r_x = ((x * CXV[0]) + (y * CXV[1]) + (z * CXV[2]) + (-1 * CPX))
		r_y = ((x * CYV[0]) + (y * CYV[1]) + (z * CYV[2]) + (-1 * CPY))
		r_z = ((x * CZV[0]) + (y * CZV[1]) + (z * CZV[2]) + (-1 * CPZ))
		
		return (r_x, r_y, r_z)
		
	
	# 複数の座標をビュー変換して配列で返す
	def view_conversion(self, points):
		view_points = []
		
		for point in points:
			# ToDo:point配列のエラーチェック
			x, y, z = self.camera_rotation(point[0], point[1], point[2])
			#point[0], point[1], point[2] = x, y, z
			view_points.append([x, y, z])
		
		return view_points
		
		
	# 複数のglyph座標をビュー変換して配列で返す
	def glyphs_view_conversion(self, glyphs):
		r_glyphs = []
		
		for glyph in glyphs:
			r_glyph = []
			for contours in glyph:
				r_points = []
				for point in contours:
					x, y, z = self.camera_rotation(
						point[0], point[1], point[2])
						
					#print(x, y, z)
						
					r_points.append([x, y, z, point[3], point[4]])
				r_glyph.append(r_points)
			r_glyphs.append(r_glyph)
		
		return r_glyphs



