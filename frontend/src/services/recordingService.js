/**
 * Service for handling video/audio recording functionality
 */
class RecordingService {
  constructor() {
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.localStream = null;
    this.remoteStream = null;
    this.combinedCanvas = null;
    this.combinedStream = null;
  }

  /**
   * Request access to user's camera and microphone
   * @returns {Promise<MediaStream>} The media stream
   */
  async requestMediaPermissions() {
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      });
      return this.localStream;
    } catch (error) {
      console.error('Error accessing media devices:', error);
      throw new Error(`Could not access camera or microphone: ${error.message}`);
    }
  }

  /**
   * Set the remote stream to be recorded
   * @param {MediaStream} stream - The remote participant's stream
   */
  setRemoteStream(stream) {
    this.remoteStream = stream;
  }

  /**
   * Create a combined video of both local and remote streams
   * @returns {MediaStream} Combined stream
   */
  createCombinedStream() {
    // Create a canvas element to combine both videos
    this.combinedCanvas = document.createElement('canvas');
    this.combinedCanvas.width = 1280;
    this.combinedCanvas.height = 720;
    
    const ctx = this.combinedCanvas.getContext('2d');
    
    // Create video elements for both streams
    const localVideo = document.createElement('video');
    localVideo.srcObject = this.localStream;
    localVideo.muted = true;
    localVideo.play();
    
    const remoteVideo = document.createElement('video');
    if (this.remoteStream) {
      remoteVideo.srcObject = this.remoteStream;
      remoteVideo.play();
    }
    
    // Draw both videos on canvas at 30fps
    const drawVideos = () => {
      // Clear canvas
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, this.combinedCanvas.width, this.combinedCanvas.height);
      
      // Draw main video (remote) on the full canvas
      if (this.remoteStream && this.remoteStream.active) {
        ctx.drawImage(
          remoteVideo, 
          0, 0, 
          this.combinedCanvas.width, this.combinedCanvas.height
        );
      }
      
      // Draw local video in a smaller box in the corner
      const smallWidth = this.combinedCanvas.width / 4;
      const smallHeight = this.combinedCanvas.height / 4;
      ctx.drawImage(
        localVideo, 
        this.combinedCanvas.width - smallWidth - 20, 
        this.combinedCanvas.height - smallHeight - 20, 
        smallWidth, smallHeight
      );
      
      // Add timestamp
      const timestamp = new Date().toLocaleTimeString();
      ctx.font = '20px Arial';
      ctx.fillStyle = 'white';
      ctx.fillText(timestamp, 10, 30);
      
      requestAnimationFrame(drawVideos);
    };
    
    drawVideos();
    
    // Get stream from canvas
    this.combinedStream = this.combinedCanvas.captureStream(30);
    
    // Add audio tracks from both streams
    const audioTracks = [];
    if (this.localStream) {
      const localAudioTrack = this.localStream.getAudioTracks()[0];
      if (localAudioTrack) audioTracks.push(localAudioTrack);
    }
    
    if (this.remoteStream) {
      const remoteAudioTrack = this.remoteStream.getAudioTracks()[0];
      if (remoteAudioTrack) audioTracks.push(remoteAudioTrack);
    }
    
    // Create a new audio context to mix audio
    if (audioTracks.length > 0) {
      const audioContext = new AudioContext();
      const destination = audioContext.createMediaStreamDestination();
      
      audioTracks.forEach(track => {
        const source = audioContext.createMediaStreamSource(new MediaStream([track]));
        source.connect(destination);
      });
      
      destination.stream.getAudioTracks().forEach(track => {
        this.combinedStream.addTrack(track);
      });
    }
    
    return this.combinedStream;
  }

  /**
   * Start recording video and audio
   */
  startRecording() {
    if (!this.localStream) {
      throw new Error('No local media stream available. Call requestMediaPermissions first.');
    }
    
    this.recordedChunks = [];
    
    // Create combined stream if remote stream is available, otherwise just use local
    const streamToRecord = this.remoteStream ? 
      this.createCombinedStream() : 
      this.localStream;
    
    try {
      this.mediaRecorder = new MediaRecorder(streamToRecord, {
        mimeType: 'video/webm;codecs=vp9,opus'
      });
    } catch (e) {
      // Fallback for browsers that don't support the above codec
      this.mediaRecorder = new MediaRecorder(streamToRecord);
    }

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.recordedChunks.push(event.data);
      }
    };

    this.mediaRecorder.start(1000); // Collect data every second
    return this.mediaRecorder;
  }

  /**
   * Stop recording
   * @returns {Promise<Blob>} A promise that resolves with the recorded blob
   */
  stopRecording() {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('No recording in progress'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
        resolve(blob);
      };

      this.mediaRecorder.onerror = (event) => {
        reject(event.error);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Clean up resources
   */
  stopAllTracks() {
    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
      this.localStream = null;
    }
    
    this.remoteStream = null;
    this.combinedStream = null;
  }

  /**
   * Upload a recorded blob to the server
   * @param {Blob} blob - The recorded video blob
   * @param {number} sessionId - The interview session ID
   * @returns {Promise<Object>} - Server response
   */
  async uploadRecording(blob, sessionId) {
    const formData = new FormData();
    formData.append('file', blob, `interview_${sessionId}.webm`);

    const response = await fetch(`http://localhost:8000/api/interviews/${sessionId}/upload-recording`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to upload recording');
    }

    return response.json();
  }
}

export default new RecordingService();