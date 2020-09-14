from ctypes import *
from Matrix import *

class Color(Structure):
	_fields_ = [('r', c_float), 
							('g', c_float),
							('b', c_float),
							('a', c_float)]


# --------------------------------------------
# 色を算出するための関数
# --------------------------------------------

# 内積の値cosθと光源との距離からuiにRGBの値を設定する
# light_inner : 光源との角度(cosθ) 
# 1=0度, 0=90度, -1=180度, 0=270度
# light_length : 光源との距離の二乗
# 入光する光の色は白(1.0, 1.0, 1.0)を前提とする
# 鏡面度 specular
# 反射受光角度　specular_inner(視線と反射光の角度)
def ui_color(color, light_inner, light_length=1, brightness=1, specular=0, specular_inner=1):
	
	# 反射率 RGB
	#r_ref, g_ref, b_ref = (1.0, 1.0, 1.0)
	r_ref, g_ref, b_ref = (0.0, 0.0, 0.0)
	if len(color) >= 3:
		r_ref = color[0]
		g_ref = color[1]
		b_ref = color[2]
	
	
	# 拡散反射
	# (光源光量 * cosθ) / 距離の二乗
	diffused_value = 0
	if light_inner < 0:
		diffused_value = (-1 * brightness * light_inner) / light_length
	
	# 鏡面反射
	# (光源光量 * (反射光と視線の角度cosθ**鏡面度) / 距離の二乗
	# 0未満: 光が鋭角で、当たっている
	specular_value = 0
	if specular_inner < 0:
		specular_value = (brightness * ((-1*specular_inner)**specular)) / light_length
	
	
	return [
		r_ref * diffused_value + specular_value, 
		g_ref * diffused_value + specular_value, 
		b_ref * diffused_value + specular_value, 1.0]


# フォグを反映した色を算出
# 
def color_with_fog(color, distance, fog_color, max_distance, min_distance):
	fogged_color = [color[0], color[1], color[2]]
	
	if min_distance < distance and \
		distance < max_distance:
		# fig値を算出する
		fog_val = (distance - min_distance) / (max_distance - min_distance)
		# フォグを反映した色を算出する
		fogged_color[0] = color[0] + fog_val * (fog_color[0] - color[0])
		fogged_color[1] = color[1] + fog_val * (fog_color[1] - color[1])
		fogged_color[2] = color[2] + fog_val * (fog_color[2] - color[2])
	elif distance >= max_distance:
		fogged_color = [fog_color[0], fog_color[1], fog_color[2]]
	
	return fogged_color


	
# 正規化した反射光のベクトルと視線のベクトルの
# なす角度を算出してcos数値で返す
# light_vector: 光源から図形のベクトル
# triangle_normal: 図形の法線(正規化済)
# scr_normal: 図形への視線(正規化済)
def specular_inner(light_vector, triangle_normal, scr_normal):
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


