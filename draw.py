import googlemaps
from datetime import datetime
import polyline
import matplotlib.pyplot as plt
import json

API_KEY = 'AIzaSyCYrPgiFMb6mFh2SaHVVAWHTnMMT05FhEs'  # 请替换为你的实际 API 金鑰


def routingdata():
    # 創立地圖
    gmaps = googlemaps.Client(key=API_KEY)

    # 定義出發地和目的地
    origin = 'Taipei 101, Taipei, Taiwan'
    destination = 'National Palace Museum, Taipei, Taiwan'

    # 查詢路線，使用駕車方式（其他選項：'driving', 'walking', 'bicycling', 'transit'）
    directions_result = gmaps.directions(
        origin,
        destination,
        mode="driving",
        departure_time=datetime.now())

    # 解析结果并格式化
    route_info = {
        "start_address": directions_result[0]['legs'][0]['start_address'],
        "end_address": directions_result[0]['legs'][0]['end_address'],
        "distance": directions_result[0]['legs'][0]['distance']['text'],
        "duration": directions_result[0]['legs'][0]['duration']['text'],
        "steps": []
    }

    for step in directions_result[0]['legs'][0]['steps']:
        step_info = {
            "instruction": step['html_instructions'],
            "distance": step['distance']['text'],
            "duration": step['duration']['text'],
            "start_location": step['start_location'],
            "end_location": step['end_location'],
            "maneuver": step.get('maneuver', 'N/A')
        }
        route_info["steps"].append(step_info)

    # 保存為JSON文件
    with open('route_info.json', 'w') as f:
        json.dump(route_info, f, indent=4)

    print("Route information has been saved to route_info.json")


def draw():
    print("Starting draw function...")  # 调试信息
    # 创建一个 Google Maps 客户端
    try:
        gmaps = googlemaps.Client(key=API_KEY)
        print("Google Maps client created successfully.")
    except Exception as e:
        print(f"Error creating Google Maps client: {e}")
        return

    # 定义出发地和目的地
    origin = 'Taipei 101, Taipei, Taiwan'
    destination = 'National Palace Museum, Taipei, Taiwan'
    print(f"Origin: {origin}, Destination: {destination}")

    # 查询路线，使用驾车方式
    try:
        directions_result = gmaps.directions(
            origin,
            destination,
            mode="driving",
            departure_time=datetime.now()
        )
        print("Directions result obtained successfully.")
    except Exception as e:
        print(f"Error obtaining directions: {e}")
        return

    print("Directions result:", directions_result)  # 打印 API 响应

    # 确保 directions_result 有数据
    if not directions_result:
        print("No directions found.")
        return

    # 获取折线编码
    try:
        polyline_str = directions_result[0]['overview_polyline']['points']
        print("Polyline string obtained successfully.")
    except KeyError as e:
        print(f"Error obtaining polyline string: {e}")
        return

    print("Polyline string:", polyline_str)  # 打印折线编码

    # 解码折线编码为坐标点
    try:
        coordinates = polyline.decode(polyline_str)
        print("Coordinates decoded successfully.")
    except Exception as e:
        print(f"Error decoding polyline: {e}")
        return

    print("Coordinates:", coordinates)  # 打印解码后的坐标点

    # 提取纬度和经度
    latitudes = [coord[0] for coord in coordinates]
    longitudes = [coord[1] for coord in coordinates]
    print("Latitudes and longitudes extracted successfully.")

    # 绘制路线图
    try:
        plt.figure(figsize=(10, 10))
        plt.plot(longitudes, latitudes, marker='o', color='blue')
        plt.title('Route from Taipei 101 to National Palace Museum')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)
        plt.show()
        print("Route plotted successfully.")
    except Exception as e:
        print(f"Error plotting route: {e}")


# 调用绘图函数
draw()
