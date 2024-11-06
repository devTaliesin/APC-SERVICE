import cv2
import numpy
import gi
import socketio
from gi.repository import Gst, GstWebRTC, GstSdp

gi.require_version('Gst', '1.0')
Gst.init(None)

__all__ = ['Gst', 'initialize_socket_client', 'initialize_pipeline', 'push_frame_to_appsrc']

def initialize_socket_client(quality, webrtc:Gst.Element, onvif, client_type="service"):
    sio = socketio.Client()
    nestjs_url = f'http://localhost:3000/stream?type={client_type}&onvif={onvif}&quality={quality}'
    
    @sio.event
    def connect():
        print(f"Connected to NestJS server for {quality} quality stream")
        sio.emit('registerGStreamer')
        
    @sio.event
    def offer(data):
        print(f"Received offer from server for {quality} quality stream")
        offer_sdp = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.OFFER, GstSdp.SDPMessage.parse_buffer(data['sdp']))
        webrtc.emit("set-remote-description", offer_sdp)

        def on_answer_created(promise:Gst.Promise, _):
            answer = promise.get_reply().get_value("answer")
            sio.emit('answer', {'sdp': answer.sdp.as_text()})

        promise = Gst.Promise.new_with_change_func(on_answer_created, None)
        webrtc.emit("gstreamerAnswer", None, promise)
    
    @sio.event
    def disconnect():
        print(f"Disconnected from {quality} quality stream")

    
    sio.connect(nestjs_url)
    return sio

def initialize_pipeline(quality, width, height, bitrate):
    pipeline:Gst.Bin = Gst.parse_launch(
        f"appsrc name=source_{quality} ! videoconvert ! x264enc tune=zerolatency bitrate={bitrate} speed-preset=superfast ! "
        f"rtph264pay config-interval=1 pt=96 ! webrtcbin name=sendrecv"
    )
    appsrc = pipeline.get_by_name(f"source_{quality}")
    appsrc.set_property("caps", Gst.Caps.from_string(f"video/x-raw,format=BGR,width={width},height={height},framerate=15/1"))

    webrtc = pipeline.get_by_name("sendrecv")
    webrtc.set_property("stun-server", "stun://stun.l.google.com:19302")

    pipeline.set_state(Gst.State.PLAYING)
    return appsrc, webrtc, pipeline

def push_frame_to_appsrc(appsrc:Gst.Element, frame, width, height):
    frame_resized:numpy.ndarray = cv2.resize(frame, (width, height))  
    data = frame_resized.tobytes()
    buf = Gst.Buffer.new_allocate(None, len(data), None)
    buf.fill(0, data)
    buf.duration = Gst.SECOND // 15  
    buf.pts = buf.dts = Gst.util_uint64_scale(int(cv2.getTickCount()), Gst.SECOND, cv2.getTickFrequency())
    appsrc.emit("push-buffer", buf)
