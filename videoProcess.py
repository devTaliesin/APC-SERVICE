import cv2
from utils.stream_utils import initialize_socket_client, initialize_pipeline, push_frame_to_appsrc, Gst

def videoProcess(videoSource):
    # 고품질과 저품질 각각의 Socket.IO 클라이언트 및 파이프라인 설정
    rtsp = videoSource['rtsp']
    onvif = videoSource['onvif']
    appsrc_high, webrtc_high, pipeline_high = initialize_pipeline("high", width=640, height=480, bitrate=1000)
    appsrc_low, webrtc_low, pipeline_low = initialize_pipeline("low", width=320, height=240, bitrate=500)
    sio_high = initialize_socket_client("high", webrtc_high, onvif)
    sio_low = initialize_socket_client("low", webrtc_low, onvif)

    # OpenCV 비디오 캡처 설정
    cap = cv2.VideoCapture(rtsp)

    # 프레임을 GStreamer 파이프라인에 전달
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 고품질과 저품질 스트림으로 각각 프레임 전송
        # push_frame_to_appsrc(appsrc_high, frame, width=640, height=480)
        # push_frame_to_appsrc(appsrc_low, frame, width=320, height=240)
    
    # def start_feed_high(src, length):
    #     ret, frame = cap.read()
    #     if ret:
    #         push_frame_to_appsrc(appsrc_high, frame, width=640, height=480)
    #     else:
    #         print("End of stream or error in high quality stream.")
    #         pipeline_high.set_state(Gst.State.NULL)

    # def start_feed_low(src, length):
    #     ret, frame = cap.read()
    #     if ret:
    #         push_frame_to_appsrc(appsrc_low, frame, width=320, height=240)
    #     else:
    #         print("End of stream or error in low quality stream.")
    #         pipeline_low.set_state(Gst.State.NULL)

    # # need-data 시그널에 데이터 공급 함수 연결
    # appsrc_high.connect("need-data", start_feed_high)
    # appsrc_low.connect("need-data", start_feed_low)
    
    # # 파이프라인을 PLAYING 상태로 전환
    # pipeline_high.set_state(Gst.State.PLAYING)
    # pipeline_low.set_state(Gst.State.PLAYING)

    # 종료 처리
    cap.release()
    pipeline_high.set_state(Gst.State.NULL)
    pipeline_low.set_state(Gst.State.NULL)
    sio_high.wait()
    sio_low.wait()
