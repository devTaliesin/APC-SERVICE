import cv2
import numpy
import socketio
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstWebRTC', '1.0')
from gi.repository import Gst, GstWebRTC, GstSdp
Gst.init(None)

__all__ = ['Gst', 'initialize_socket_client', 'initialize_pipeline', 'push_frame_to_appsrc']

def initialize_socket_client(quality, webrtc:Gst.Element, onvif, client_type="service"):
    sio = socketio.Client()
    nestjs_url = f'http://192.168.0.18:3000/websocket?type={client_type}&onvif={onvif}&quality={quality}'
    
    @sio.event
    def connect():
        print(f"Connected to NestJS server for {quality} quality stream",flush=True)
        sio.emit('registerGStreamer')
        
    @sio.event
    def offer(data):
        print(f"Received offer from server for {quality} quality stream",flush=True)

        # SDPMessage 객체 생성 및 파싱
        result, sdp_message = GstSdp.SDPMessage.new()
        
        if result == GstSdp.SDPResult.OK:
            result = GstSdp.sdp_message_parse_buffer(data['sdp'].encode('utf-8'), sdp_message)
            
            if result == GstSdp.SDPResult.OK:
                offer_sdp = GstWebRTC.WebRTCSessionDescription.new(
                    GstWebRTC.WebRTCSDPType.OFFER,
                    sdp_message
                )
                
                # set-remote-description에 대한 완료 핸들러 추가
                def on_set_remote_description(promise: Gst.Promise, _):
                    print("Remote description set successfully.",flush=True)
                    
                    # 파이프라인 상태 설정
                    webrtc.set_state(Gst.State.PLAYING)
                    state_change_result = webrtc.get_state(Gst.CLOCK_TIME_NONE)
                    print(f"Pipeline state change result: {state_change_result}",flush=True)
                    
                # on-negotiation-needed 핸들러
                def on_negotiation_needed(element):
                    print("Negotiation needed, creating answer.",flush=True)
                    # Answer 생성 함수
                    def on_answer_created(promise: Gst.Promise, _):
                        reply = promise.get_reply()
                        if reply is not None and reply.has_field("answer"):
                            answer = reply.get_value("answer").sdp
                            sio.emit('answer', {'sdp': answer.as_text()})
                        else:
                            print("Failed to get 'answer' from promise reply",flush=True)

                    # Promise 생성 및 create-answer 호출
                    promise = Gst.Promise.new_with_change_func(on_answer_created, None)
                    webrtc.emit("create-answer", None, promise)

                # set-remote-description에 대한 Promise 생성 및 호출
                promise = Gst.Promise.new_with_change_func(on_set_remote_description, None)
                webrtc.emit("set-remote-description", offer_sdp, promise)

                # on-negotiation-needed 시그널 핸들러 연결
                webrtc.connect("on-negotiation-needed", on_negotiation_needed)

                # ICE 후보 이벤트 핸들러 추가
                def on_ice_candidate(webrtc, mlineindex, candidate):
                    print(f"Received ICE candidate: {candidate}",flush=True)
                    # 서버로 ICE candidate 전송하는 코드 추가 가능
                    # 예시: sio.emit('ice-candidate', {'candidate': candidate})

                webrtc.connect("on-ice-candidate", on_ice_candidate)

            else:
                print("Failed to parse SDP message",flush=True)
        else:
            print("Failed to create SDP message",flush=True)
            
    @sio.event
    def disconnect():
        print(f"Disconnected from {quality} quality stream")

    
    sio.connect(nestjs_url)
    return sio

def initialize_pipeline(quality, width, height, bitrate):
    pipeline: Gst.Bin = Gst.parse_launch(
        # f"appsrc name=source_{quality} ! videoconvert ! "
        "videotestsrc ! videoconvert ! "#삭제해야되는부분
        f"x264enc tune=zerolatency bitrate={bitrate} speed-preset=superfast ! "
        f"rtph264pay config-interval=1 pt=96 ! "
        f"application/x-rtp,media=video,encoding-name=H264,clock-rate=90000,payload=96 ! "
        f"rtpbin ! "
        f"webrtcbin name=sendrecv"
    )
    appsrc = pipeline.get_by_name("sendrecv") #삭제해야되는부분
    # appsrc = pipeline.get_by_name(f"source_{quality}")
    # if not appsrc:
    #     print("Error: Could not find appsrc element.",flush=True)
    #     return None, None, pipeline
    
    # appsrc.set_property("caps", Gst.Caps.from_string(f"video/x-raw,format=BGR,width={width},height={height},framerate=15/1"))

    webrtc = pipeline.get_by_name("sendrecv")
    if not webrtc:
        print("Error: Could not find webrtcbin element.",flush=True)
        return None, None, pipeline
    webrtc.set_property("stun-server", "stun://stun.l.google.com:19302")
    webrtc.set_property("bundle-policy", "max-bundle")  # 번들 사용 설정
    
    return appsrc, webrtc, pipeline

def push_frame_to_appsrc(appsrc:Gst.Element, frame, width, height):
    frame_resized:numpy.ndarray = cv2.resize(frame, (width, height))  
    data = frame_resized.tobytes()
    buf = Gst.Buffer.new_allocate(None, len(data), None)
    buf.fill(0, data)
    buf.duration = Gst.SECOND // 15  
    buf.pts = buf.dts = Gst.util_uint64_scale(int(cv2.getTickCount()), Gst.SECOND, cv2.getTickFrequency())
    appsrc.emit("push-buffer", buf)
