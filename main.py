import socketio
from multiprocessing import Process
import videoProcess

processes: dict[str, Process] = {}
sio = socketio.Client()

@sio.event
def connect():
  print('connect')
  
@sio.event
def videoSource(data):
  print(data, flush=True)
  for videoSource in data:
    p = Process(target=videoProcess.videoProcess, args=[videoSource])
    processes[f'{videoSource["id"]}'] = p
    p.start()
  
@sio.event
def disconnect():
  for p in processes.values():
    p.close()
  print('disconnect')
  
client_type = "service_master"
onvif = ""
quality = ""
NESTJS_SERVER_URL = f'http://192.168.0.18:3000/websocket?type={client_type}&onvif={onvif}&quality={quality}'
print(NESTJS_SERVER_URL)
sio.connect(NESTJS_SERVER_URL)

sio.wait()








# import cv2

# # GStreamer 파이프라인을 통한 RTSP URL 설정
# rtsp_url = "rtsp://localhost:8554/test"  # RTSP 서버 URL
# gst_str = (
#     f"appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! "
#     f"rtph264pay config-interval=1 pt=96 ! udpsink host={rtsp_url} port=8554"
# )

# # OpenCV VideoWriter 객체 생성
# cap = cv2.VideoCapture(0)  # 웹캠에서 캡처, 필요 시 비디오 파일 경로로 대체
# out = cv2.VideoWriter(gst_str, cv2.CAP_GSTREAMER, 0, 30, (640, 480), True)

# if not out.isOpened():
#     print("Failed to open video writer")
#     exit()

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # 프레임을 GStreamer RTSP 파이프라인으로 전송
#     out.write(frame)

# cap.release()
# out.release()